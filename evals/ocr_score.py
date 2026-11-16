"""Bir okuyucunun çıktısını doğru cevapla (evals/ocr_truth.py) puanlar.

Okuma biçimi okuyucudan bağımsızdır: sayfa başına sırayla satırlar, satır başına hücreler. Hücrenin
yatay konumu biliniyorsa (metin katmanı, OCR kutusu) sütun konumla, bilinmiyorsa (HTML tablo) sıra
numarasıyla eşleşir. Her okuyucu için bu biçime çeviren bir bağdaştırıcı yazılır; burada yalnız
dijital PDF metin katmanınınki var: betiği sınamak içindir, sonucu %100 doğru olmalıdır.

Sonuç türleri (her doğru cevap değeri için bir tane):
- doğru: değer doğru yerde ve eşdeğer (eşdeğerlik: ocr_truth.canonical).
- ayraç farkı: doğru yerde, yalnız rakamlar arasındaki virgül–nokta farklı.
- yanlış karakter: doğru yerde başka bir yazı var.
- bağ kopması: değer okunmuş ama satırı, sütunu ya da etiketi kopmuş (en ağır tür).
- atlama: değer okunmamış.
"""

import argparse
import json
import re
import subprocess
import tempfile
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from difflib import SequenceMatcher
from enum import StrEnum
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from evals.ocr_truth import (
    TruthDocument,
    TruthPage,
    TruthValue,
    ValueKind,
    canonical,
    same_value,
    separator_only,
)
from visual_agent.domain.document import Chunk, ChunkKind
from visual_agent.ingest.elements import SECTION_SEPARATOR
from visual_agent.verification.text import contains_token

if TYPE_CHECKING:
    from PIL import Image

_SIMILAR = 0.75
"""Satır anahtarı ya da etiket bu kadar benzerse bulunmuş sayılır: karakter hatası bağı
koparmaz."""
_TEXT_SIMILAR = 0.8


class Outcome(StrEnum):
    CORRECT = "doğru"
    SEPARATOR = "ayraç farkı"
    WRONG = "yanlış karakter"
    BROKEN = "bağ kopması"
    MISSING = "atlama"
    HIDDEN_RIGHT = "gizlendi (doğruydu)"
    """Okuyucu değeri belirsiz sayıp göstermedi; okuma doğruydu (gizlemenin bedeli)."""
    HIDDEN_WRONG = "gizlendi (yanlıştı)"
    """Okuyucu yanlış okuduğu değeri belirsiz sayıp göstermedi (kural 1 korundu)."""


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ReadCell(_Model):
    text: str
    left: float | None = None
    right: float | None = None
    uncertain: bool = False
    """Okuyucu bu hücrenin bir değerini belirsiz sayıp kullanıcıya göstermiyor."""


class ReadRow(_Model):
    cells: tuple[ReadCell, ...]


class ReadPage(_Model):
    page: int
    rows: tuple[ReadRow, ...]


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, canonical(a), canonical(b)).ratio()


def _compare(read: str, value: str) -> Outcome:
    if same_value(read, value):
        return Outcome.CORRECT
    if separator_only(read, value):
        return Outcome.SEPARATOR
    return Outcome.MISSING if not read.strip() else Outcome.WRONG


def _judge(read: str, value: str, uncertain: bool, misplaced: bool) -> Outcome:
    """Doğru yerdeki okumanın sonucu. Değer başka yerde okunmuşsa bağ kopmuştur; okuyucu
    gizlediyse kullanıcı görmez."""
    outcome = _compare(read, value)
    if outcome in (Outcome.WRONG, Outcome.MISSING) and misplaced:
        return Outcome.BROKEN
    if uncertain and outcome is not Outcome.MISSING:
        return Outcome.HIDDEN_RIGHT if outcome is Outcome.CORRECT else Outcome.HIDDEN_WRONG
    return outcome


def _find_cell(rows: Sequence[ReadRow], text: str) -> tuple[int, int] | None:
    """Önce eşdeğer, yoksa en benzer hücre (satır, hücre)."""
    best, best_score = None, _SIMILAR
    for r, row in enumerate(rows):
        for c, cell in enumerate(row.cells):
            if same_value(cell.text, text):
                return r, c
            score = _similar(cell.text, text)
            if score > best_score:
                best, best_score = (r, c), score
    return best


def _anywhere(rows: Sequence[ReadRow], value: str) -> bool:
    return any(same_value(cell.text, value) for row in rows for cell in row.cells)


def _column_cell(header: ReadRow, header_index: int, row: ReadRow) -> ReadCell | None:
    """Başlık hücresinin altındaki hücre: konum biliniyorsa en çok örtüşen, yoksa aynı sıradaki."""
    target = header.cells[header_index]
    if target.left is None or target.right is None:
        return row.cells[header_index] if header_index < len(row.cells) else None
    best, best_overlap = None, 0.0
    for cell in row.cells:
        if cell.left is None or cell.right is None:
            continue
        overlap = min(cell.right, target.right) - max(cell.left, target.left)
        if cell.left >= target.left - 1 and overlap > best_overlap:
            best, best_overlap = cell, overlap
    return best


def _header(rows: Sequence[ReadRow], above: int, columns: Sequence[str]) -> int | None:
    """Satırın üstündeki en yakın başlık satırı: tablonun sütun adlarının yarısından çoğu."""
    for r in range(above - 1, -1, -1):
        names = sum(any(same_value(c.text, name) for c in rows[r].cells) for name in columns)
        if names * 2 > len(columns):
            return r
    return None


def _score_cell(value: TruthValue, rows: Sequence[ReadRow], columns: Sequence[str]) -> Outcome:
    found = _find_cell(rows, value.row_key or "")
    if value.value == value.row_key:
        if found is None:
            return Outcome.MISSING
        key = rows[found[0]].cells[found[1]]
        return _judge(key.text, value.value, key.uncertain, misplaced=False)
    if found is None:
        return Outcome.BROKEN if _anywhere(rows, value.value) else Outcome.MISSING
    row = rows[found[0]]
    in_row = any(same_value(c.text, value.value) for c in row.cells)
    header = _header(rows, found[0], columns)
    names = (
        []
        if header is None
        else [same_value(c.text, value.column or "") for c in rows[header].cells]
    )
    if header is None or True not in names:
        return Outcome.BROKEN if in_row else Outcome.MISSING
    cell = _column_cell(rows[header], names.index(True), row)
    if cell is None:
        return Outcome.BROKEN if in_row else Outcome.MISSING
    return _judge(cell.text, value.value, cell.uncertain, misplaced=in_row)


def _strip_labels(text: str, labels: Sequence[str]) -> str:
    """Hücrenin başındaki etiketler atılır: "Base size Grade rule XS" → "XS"."""
    text = canonical(text)
    stripped = True
    while stripped:
        stripped = False
        for label in labels:
            prefix = canonical(label) + " "
            if text.startswith(prefix):
                text, stripped = text[len(prefix) :], True
    return text


def _neighbors(rows: Sequence[ReadRow], r: int, c: int) -> list[ReadCell]:
    """Etiket hücresine bağlı sayılan hücreler: sağındaki ve (form tablo gibi okunduysa)
    hemen altındaki."""
    cell, row = rows[r].cells[c], rows[r].cells
    right = [
        other
        for d, other in enumerate(row)
        if (d > c if cell.right is None or other.left is None else other.left >= cell.right)
    ]
    found = [right[0] if right else ReadCell(text="")]
    if r + 1 < len(rows):
        below = rows[r + 1].cells
        if cell.left is None and c < len(below):
            found.append(below[c])
        elif cell.left is not None:
            found += [o for o in below if o.left is not None and abs(o.left - cell.left) < 2]
    return found


def _assigned(rows: Sequence[ReadRow], label: str) -> list[ReadCell]:
    """Okumada etikete bağlanan değerler: etiketin sağındaki ya da altındaki hücre, ya da
    etiketle aynı hücreye okunmuş kalan ("Grade rule Ronu - 2027")."""
    found: list[ReadCell] = []
    prefix = canonical(label) + " "
    for r, row in enumerate(rows):
        for c, cell in enumerate(row.cells):
            text = canonical(cell.text)
            if same_value(cell.text, label):
                found += _neighbors(rows, r, c)
            elif text.startswith(prefix):
                found.append(ReadCell(text=text[len(prefix) :], uncertain=cell.uncertain))
    return found


def _score_pair(value: TruthValue, rows: Sequence[ReadRow], labels: Sequence[str]) -> Outcome:
    label = value.label or ""
    own = _assigned(rows, label)
    if not own:
        fuzzy = _find_cell(rows, label)
        if fuzzy is not None:
            own = _assigned(rows, rows[fuzzy[0]].cells[fuzzy[1]].text)
    others = [cell for other in labels if other != label for cell in _assigned(rows, other)]
    misplaced = any(
        same_value(_strip_labels(cell.text, labels), value.value) for cell in others
    ) or _anywhere(rows, value.value)
    if not own:
        return Outcome.BROKEN if misplaced else Outcome.MISSING
    cell = next((c for c in own if same_value(c.text, value.value)), own[0])
    if not same_value(cell.text, value.value) and _mixed(cell.text, value.value, label, labels):
        return Outcome.BROKEN  # iki etiket karışık okunmuş: "Etiket A Etiket B DeğerA"
    return _judge(cell.text, value.value, cell.uncertain, misplaced)


def _contains(text: str, part: str) -> bool:
    """Sözcük sınırlarıyla içerir: "XS" "XS FW27" içinde var, "XS-5XL" içinde yok."""
    return (
        re.search(rf"(?<![\w-]){re.escape(canonical(part))}(?![\w-])", canonical(text)) is not None
    )


def _mixed(read: str, value: str, label: str, labels: Sequence[str]) -> bool:
    """Etikete bağlanan okumada başka bir etiket ve beklenen değer birlikte geçiyor."""
    others = [other for other in labels if other != label and other]
    return _contains(read, value) and any(_contains(read, other) for other in others)


def _score_text(value: TruthValue, rows: Sequence[ReadRow]) -> Outcome:
    lines = [
        (" ".join(c.text for c in row.cells), any(c.uncertain for c in row.cells)) for row in rows
    ]
    target = canonical(value.value)
    for line, uncertain in lines:
        if target in canonical(line):
            return Outcome.HIDDEN_RIGHT if uncertain else Outcome.CORRECT
    best = max(lines, key=lambda line: _similar(line[0], value.value), default=("", False))
    if _similar(best[0], value.value) < _TEXT_SIMILAR:
        return Outcome.MISSING
    if best[1]:
        return Outcome.HIDDEN_WRONG
    return Outcome.SEPARATOR if separator_only(best[0], value.value) else Outcome.WRONG


def score_page(truth: TruthPage, read: ReadPage | None) -> list[tuple[TruthValue, Outcome]]:
    rows = read.rows if read is not None else ()
    columns: dict[int | None, list[str]] = {}
    for value in truth.values:
        if value.kind is ValueKind.CELL and value.column not in columns.get(value.table, []):
            columns.setdefault(value.table, []).append(value.column or "")
    labels = [value.label or "" for value in truth.values if value.kind is ValueKind.PAIR]
    results = []
    for value in truth.values:
        if value.kind is ValueKind.CELL:
            outcome = _score_cell(value, rows, columns[value.table])
        elif value.kind is ValueKind.PAIR:
            outcome = _score_pair(value, rows, labels)
        else:
            outcome = _score_text(value, rows)
        results.append((value, outcome))
    return results


def score_document(
    truth: TruthDocument, pages: Sequence[ReadPage]
) -> list[tuple[int, TruthValue, Outcome]]:
    by_number = {page.page: page for page in pages}
    return [
        (page.page, value, outcome)
        for page in truth.pages
        for value, outcome in score_page(page, by_number.get(page.page))
    ]


_CELL_GAP = 4.5
_CELL_GAP_SHARE = 0.45
"""Bu kadar noktadan (ya da yazı yüksekliğinin bu payından) geniş boşluk iki hücreyi ayırır;
sözcük arası boşluk daha dardır."""
_WORD_GAP = 0.15
"""Karakter yüksekliğine oranla: bundan geniş boşluk sözcük arasıdır."""
_CONTINUATION_INDENT = 10.0


_Char = tuple[str, float, float, float, float]
"""(karakter, sol, sağ, alt, üst) PDF noktası."""


def _chars(page: object) -> list[_Char]:
    textpage = page.get_textpage()  # type: ignore[attr-defined]
    chars = []
    for index in range(textpage.count_chars()):
        text = textpage.get_text_range(index, 1)
        if not text.strip():
            continue
        left, bottom, right, top = textpage.get_charbox(index, loose=True)
        chars.append((text, left, right, bottom, top))
    return chars


def _lines(chars: list[_Char]) -> list[list[_Char]]:
    """Karakterler dikey ortalarına göre satırlara (yukarıdan aşağı) toplanır."""
    ordered = sorted(chars, key=lambda c: -(c[3] + c[4]) / 2)
    lines: list[list[_Char]] = []
    for char in ordered:
        center, height = (char[3] + char[4]) / 2, char[4] - char[3]
        if lines:
            last = lines[-1]
            last_center = sum((c[3] + c[4]) / 2 for c in last) / len(last)
            if abs(last_center - center) < 0.5 * max(height, max(c[4] - c[3] for c in last)):
                last.append(char)
                continue
        lines.append([char])
    return lines


def _row(line: list[_Char]) -> list[ReadCell]:
    cells: list[ReadCell] = []
    text, left, right, height = "", 0.0, 0.0, 0.0
    for char, c_left, c_right, bottom, top in sorted(line, key=lambda c: c[1]):
        gap = c_left - right
        if text and gap > max(_CELL_GAP, _CELL_GAP_SHARE * (top - bottom)):
            cells.append(ReadCell(text=text, left=left, right=right))
            text = ""
        if not text:
            text, left, height = char, c_left, top - bottom
        else:
            text += (" " if gap > _WORD_GAP * max(height, top - bottom) else "") + char
        right = max(right, c_right) if text != char else c_right
    if text:
        cells.append(ReadCell(text=text, left=left, right=right))
    return cells


def _join_continuations(rows: list[list[ReadCell]]) -> list[ReadRow]:
    """Sol kenardan içeride başlayan satır, bir üstteki satırın kayan hücresinin devamıdır."""
    margin = min((row[0].left or 0.0) for row in rows) if rows else 0.0
    joined: list[list[ReadCell]] = []
    for row in rows:
        if joined and (row[0].left or 0.0) > margin + _CONTINUATION_INDENT:
            previous = joined[-1]
            for cell in row:
                target = min(previous, key=lambda p: abs((p.left or 0.0) - (cell.left or 0.0)))
                index = previous.index(target)
                previous[index] = ReadCell(
                    text=f"{target.text} {cell.text}",
                    left=target.left,
                    right=max(target.right or 0.0, cell.right or 0.0),
                )
            continue
        joined.append(list(row))
    return [ReadRow(cells=tuple(row)) for row in joined]


def text_layer_pages(pdf: Path) -> list[ReadPage]:
    """Dijital PDF'in metin katmanını okuma biçimine çevirir (konumlu hücreler)."""
    import pypdfium2

    document = pypdfium2.PdfDocument(pdf)
    try:
        pages = []
        for number in range(len(document)):
            rows = [_row(line) for line in _lines(_chars(document[number]))]
            pages.append(ReadPage(page=number + 1, rows=tuple(_join_continuations(rows))))
        return pages
    finally:
        document.close()


class _HtmlTable(HTMLParser):
    """HTML tablonun satırları; birleşik hücre (colspan) kapladığı sütun kadar yer tutar."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._cell: list[str] | None = None
        self._span = 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.rows.append([])
        elif tag in ("td", "th"):
            self._cell, self._span = [], int(dict(attrs).get("colspan") or 1)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._cell is not None and self.rows:
            # PaddleOCR-VL hücre içi satır sonunu "\\n" diye yazar: biçimdir, boşluk sayılır.
            text = "".join(self._cell).replace("\\n", "\n")
            self.rows[-1] += [" ".join(text.split())] + [""] * (self._span - 1)
            self._cell = None

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)


def html_rows(table: str) -> list[list[str]]:
    parser = _HtmlTable()
    parser.feed(table)
    return parser.rows


def paddle_vl_page(
    result: Path, page: int, uncertain: Mapping[int, Sequence[str]] | None = None
) -> ReadPage:
    """PaddleOCR-VL'nin sayfa sonucu (`*_res.json`): bloklar okuma sırasıyla; tablo bloğu
    satır ve hücreleriyle (konumsuz, sıra numarasıyla eşleşir), metin bloğu satır satır.

    uncertain: ikinci okumanın uyuşmadığı parçalar, blok numarasına (block_id) göre; bu parçayı
    taşıyan hücre gizlenmiş sayılır."""
    data = json.loads(result.read_text(encoding="utf-8"))
    rows: list[ReadRow] = []
    for block in data["parsing_res_list"]:
        content = str(block.get("block_content") or "")
        tokens = (uncertain or {}).get(int(block.get("block_id", -1)), ())

        def cell(text: str, tokens: Sequence[str] = tokens) -> ReadCell:
            return ReadCell(text=text, uncertain=bool(set(value_tokens(text)) & set(tokens)))

        if block.get("block_label") == "table":
            rows += [ReadRow(cells=tuple(cell(t) for t in r)) for r in html_rows(content)]
        else:
            rows += [ReadRow(cells=(cell(line),)) for line in content.splitlines() if line.strip()]
    return ReadPage(page=page, rows=tuple(rows))


_TOKEN_EDGES = ".,;:()[]{}|\"'"
_CODE_RE = re.compile(r"^[A-ZÇĞİÖŞÜ]{2,}(?:-[A-Z0-9ÇĞİÖŞÜ]+)*$")
"""Rakamsız kod: en az iki büyük harf, tireyle parçalar ("AXL", "XS-AXL")."""


def value_tokens(text: str) -> list[str]:
    """Karşılaştırılan sayı ve kod parçaları (eşdeğerlik kurallarına göre yazılmış): rakam
    içeren her parça ve rakamsız kodlar. "27 1/2" iki parçadır: "27" ve "1/2"."""
    tokens = []
    for raw in canonical(text).split():
        token = raw.strip(_TOKEN_EDGES)
        if token and (any(ch.isdigit() for ch in token) or _CODE_RE.match(token)):
            tokens.append(token)
    return tokens


def count_mismatches(primary: str, second: str) -> list[str]:
    """Birinci okumanın sayı ve kod parçalarından, iki okumada geçiş sayısı farklı olanlar.
    Bilinen zayıflık: aynı bloktaki iki hata birbirini dengelerse (bir "1/4" → "1/2", bir
    "1/2" → "1/4") sayılar tutar ve geçer."""
    first, other = Counter(value_tokens(primary)), Counter(value_tokens(second))
    return sorted(token for token, count in first.items() if other[token] != count)


Tesseract = Callable[["Image.Image"], str]


def tesseract_reader(executable: str = "tesseract", language: str = "tur+eng") -> Tesseract:
    """İkinci okuma: Tesseract, eğiklik düzeltmesiz. Seyrek kip (psm 11): sayım için sıra
    gerekmez, tablodaki dağınık hücreler de okunur."""

    def read(image: "Image.Image") -> str:
        with tempfile.TemporaryDirectory() as work:
            source = Path(work) / "blok.png"
            image.save(source)
            command = [executable, str(source), "stdout", "-l", language, "--psm", "11"]
            return subprocess.run(command, capture_output=True, text=True, check=True).stdout

    return read


_BLOCK_PAD = 4


def second_reading_marks(
    result: Path, image: "Image.Image", read: Tesseract
) -> dict[int, list[str]]:
    """PaddleOCR-VL'nin her bloğu için ikinci okumayla geçiş sayısı tutmayan parçalar
    ({blok numarası: [parça]}). Blok kutusu PaddleOCR-VL'ye verilen görüntünün pikselidir."""
    data = json.loads(result.read_text(encoding="utf-8"))
    scale_x = image.width / float(data.get("width") or image.width)
    scale_y = image.height / float(data.get("height") or image.height)
    marks: dict[int, list[str]] = {}
    for block in data["parsing_res_list"]:
        content = str(block.get("block_content") or "")
        if block.get("block_label") == "table":
            content = " ".join(text for row in html_rows(content) for text in row)
        if not value_tokens(content):
            continue
        left, top, right, bottom = block["block_bbox"]
        box = (
            max(0, int(left * scale_x) - _BLOCK_PAD),
            max(0, int(top * scale_y) - _BLOCK_PAD),
            min(image.width, int(right * scale_x) + _BLOCK_PAD),
            min(image.height, int(bottom * scale_y) + _BLOCK_PAD),
        )
        mismatched = count_mismatches(content, read(image.crop(box)))
        if mismatched:
            marks[int(block["block_id"])] = mismatched
    return marks


def pipeline_pages(chunks: Sequence[Chunk]) -> list[ReadPage]:
    """Mevcut hattın parçaları. Tablo satırı ("Başlık: değer | Başlık: değer") bir başlık
    satırı ve bir değer satırı olur: sütun sırası korunur. Bölüm adı ve tablo notu ayrı satırdır.
    Hattın belirsiz saydığı (cevapta gizlediği) değerin hücresi işaretlenir."""
    pages: dict[int, list[ReadRow]] = {}
    seen: dict[int, set[str]] = {}
    for chunk in chunks:
        page = chunk.location.page or 1
        rows, emitted = pages.setdefault(page, []), seen.setdefault(page, set())
        for part in chunk.section.split(SECTION_SEPARATOR) if chunk.section else ():
            if part not in emitted:
                emitted.add(part)
                rows.append(ReadRow(cells=(ReadCell(text=part),)))

        def cell(text: str, chunk: Chunk = chunk) -> ReadCell:
            hidden = any(contains_token(text, token) for token in chunk.ocr_uncertain)
            return ReadCell(text=text, uncertain=hidden)

        if chunk.kind is ChunkKind.TABLE_ROW:
            parts = [part.partition(": ") for part in chunk.text.split(" | ")]
            pairs = [(label, value) if sep else ("", label) for label, sep, value in parts]
            rows.append(ReadRow(cells=tuple(ReadCell(text=label) for label, _ in pairs)))
            rows.append(ReadRow(cells=tuple(cell(value) for _, value in pairs)))
        else:
            rows.append(ReadRow(cells=(cell(chunk.text),)))
    return [ReadPage(page=page, rows=tuple(rows)) for page, rows in sorted(pages.items())]


def summarize(results: Sequence[tuple[str, int, TruthValue, Outcome]]) -> dict[str, object]:
    counts = Counter((value.kind.value, outcome.value) for _, _, value, outcome in results)
    total = len(results)
    correct = sum(1 for *_, outcome in results if outcome is Outcome.CORRECT)
    return {
        "değer": total,
        "doğru_oranı": round(correct / total, 4) if total else 0.0,
        "türe_göre": {f"{kind} / {outcome}": n for (kind, outcome), n in sorted(counts.items())},
        "doğru_olmayan_örnekler": [
            {
                "belge": doc,
                "sayfa": page,
                "tür": value.kind.value,
                "beklenen": value.value,
                "sonuç": outcome.value,
            }
            for doc, page, value, outcome in results
            if outcome is not Outcome.CORRECT
        ][:20],
    }


def read_pages(reader: str, doc_id: str, pdf: Path, reading: Path | None) -> list[ReadPage]:
    """Okuyucunun belge çıktısı:
    - textlayer: dijital PDF'in metin katmanı (betiğin sınaması),
    - paddle-vl: `<reading>/<doc_id>/s<sayfa>_res.json` (PaddleOCR-VL sayfa sonuçları) ve varsa
      yanında `s<sayfa>_uncertain.json` (ikinci okuma: {blok numarası: [belirsiz parça]}),
    - pipeline: `<reading>` mevcut hattın parça dosyası ({belge: [parça]}, evals çıktısı).
    """
    if reader == "textlayer":
        return text_layer_pages(pdf)
    if reading is None:
        raise ValueError("--reading gerekli")
    if reader == "paddle-vl":
        pages = []
        for result in sorted((reading / doc_id).glob("s*_res.json")):
            number = int(result.name[1:].split("_")[0])
            marks = result.with_name(f"s{number}_uncertain.json")
            uncertain = (
                {int(k): v for k, v in json.loads(marks.read_text(encoding="utf-8")).items()}
                if marks.exists()
                else None
            )
            pages.append(paddle_vl_page(result, number, uncertain))
        return pages
    data = json.loads(reading.read_text(encoding="utf-8"))
    return pipeline_pages([Chunk.model_validate(c) for c in data.get(doc_id, [])])


def main() -> None:
    parser = argparse.ArgumentParser(description="Okuyucu çıktısını doğru cevapla puanlar.")
    parser.add_argument("--set", type=Path, required=True, help="PDF ve doğru cevap JSON klasörü")
    parser.add_argument("--reader", choices=("textlayer", "paddle-vl", "pipeline"), required=True)
    parser.add_argument("--reading", type=Path, help="okuyucu çıktısı (bkz. read_pages)")
    args = parser.parse_args()
    results = []
    for truth_file in sorted(args.set.glob("*.json")):
        truth = TruthDocument.model_validate_json(truth_file.read_text(encoding="utf-8"))
        pages = read_pages(
            args.reader, truth.doc_id, args.set / f"{truth.doc_id}.pdf", args.reading
        )
        results += [(truth.doc_id, *item) for item in score_document(truth, pages)]
    print(json.dumps(summarize(results), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
