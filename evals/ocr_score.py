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
from collections import Counter
from collections.abc import Sequence
from difflib import SequenceMatcher
from enum import StrEnum
from pathlib import Path

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


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ReadCell(_Model):
    text: str
    left: float | None = None
    right: float | None = None


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
        return _compare(rows[found[0]].cells[found[1]].text, value.value)
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
    outcome = _compare(cell.text if cell is not None else "", value.value)
    if outcome in (Outcome.WRONG, Outcome.MISSING) and in_row:
        return Outcome.BROKEN
    return outcome


def _joined_pair(rows: Sequence[ReadRow], label: str) -> str | None:
    """Etiket ile değer aynı hücreye okunmuşsa ("Grade rule Ronu - 2027") değer kısmı."""
    prefix = canonical(label) + " "
    for row in rows:
        for cell in row.cells:
            text = canonical(cell.text)
            if text.startswith(prefix):
                return text[len(prefix) :]
    return None


def _score_pair(value: TruthValue, rows: Sequence[ReadRow]) -> Outcome:
    found = _find_cell(rows, value.label or "")
    if found is None or not same_value(rows[found[0]].cells[found[1]].text, value.label or ""):
        joined = _joined_pair(rows, value.label or "")
        if joined is not None:
            return _compare(joined, value.value)
    if found is None:
        return Outcome.BROKEN if _anywhere(rows, value.value) else Outcome.MISSING
    row = rows[found[0]]
    label = row.cells[found[1]]
    after = [
        cell
        for c, cell in enumerate(row.cells)
        if (c > found[1] if label.right is None or cell.left is None else cell.left >= label.right)
    ]
    outcome = _compare(after[0].text if after else "", value.value)
    if outcome in (Outcome.WRONG, Outcome.MISSING) and _anywhere(rows, value.value):
        return Outcome.BROKEN
    return outcome


def _score_text(value: TruthValue, rows: Sequence[ReadRow]) -> Outcome:
    lines = [" ".join(cell.text for cell in row.cells) for row in rows]
    target = canonical(value.value)
    if any(target in canonical(line) for line in lines):
        return Outcome.CORRECT
    best = max(lines, key=lambda line: _similar(line, value.value), default="")
    if _similar(best, value.value) < _TEXT_SIMILAR:
        return Outcome.MISSING
    return Outcome.SEPARATOR if separator_only(best, value.value) else Outcome.WRONG


def score_page(truth: TruthPage, read: ReadPage | None) -> list[tuple[TruthValue, Outcome]]:
    rows = read.rows if read is not None else ()
    columns: dict[int | None, list[str]] = {}
    for value in truth.values:
        if value.kind is ValueKind.CELL and value.column not in columns.get(value.table, []):
            columns.setdefault(value.table, []).append(value.column or "")
    results = []
    for value in truth.values:
        if value.kind is ValueKind.CELL:
            outcome = _score_cell(value, rows, columns[value.table])
        elif value.kind is ValueKind.PAIR:
            outcome = _score_pair(value, rows)
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Okuyucu çıktısını doğru cevapla puanlar.")
    parser.add_argument("--set", type=Path, required=True, help="PDF ve doğru cevap JSON klasörü")
    parser.add_argument("--reader", choices=("textlayer",), required=True)
    args = parser.parse_args()
    results = []
    for truth_file in sorted(args.set.glob("*.json")):
        truth = TruthDocument.model_validate_json(truth_file.read_text(encoding="utf-8"))
        pages = text_layer_pages(args.set / f"{truth.doc_id}.pdf")
        results += [(truth.doc_id, *item) for item in score_document(truth, pages)]
    print(json.dumps(summarize(results), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
