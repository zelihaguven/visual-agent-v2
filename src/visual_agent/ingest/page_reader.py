"""Metin katmanı olmayan sayfaların okuyucusu: PaddleOCR-VL okur, Tesseract ikinci kez okur.

Karar 0010: sayfa PaddleOCR-VL'nin resmi akışıyla (düzen + bölge) okunur; her bloğun sayı ve
kodları Tesseract'ın aynı bloktaki okumasıyla sayılarak karşılaştırılır, sayısı tutmayan değer
belirsiz sayılır ve cevapta gizlenir.

Eşdeğerlik kuralları ve sayarak karşılaştırma `evals/ocr_score.py` ile `evals/ocr_truth.py`
içindeki ölçülmüş kodun kopyasıdır: o dosyalar sha256 ile donmuştur, uygulama da ölçüm
paketinden içe aktarmaz. İki kopyanın aynı sonucu verdiğini `tests/test_page_reader.py` set A
kaydı üzerinde sınar; biri değişirse test kırılır.
"""

import logging
import re
import tempfile
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, cast

import httpx
import pypdfium2
import pypdfium2.raw as pdfium_c
from PIL import Image, ImageOps

from visual_agent.domain.document import Box, SourceLocation
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.external import ReaderUnavailable, tesseract_text
from visual_agent.ingest.pdf_tables import TableCell, group_table_rows
from visual_agent.ingest.text_layer import IMAGE_COVER_RATIO

logger = logging.getLogger(__name__)

LOCAL_BACKEND = "local"
_MODEL = "PaddlePaddle/PaddleOCR-VL-1.6"
_PIPELINE_VERSION = "v1.6"
RENDER_DPI = 300
POINTS_PER_INCH = 72
_SERVER_TIMEOUT_SECONDS = 5.0
_TESSERACT_TIMEOUT_SECONDS = 120
_BLANK_LEVEL = 250
"""En koyu pikseli bu kadar açık olan sayfa boştur."""
_HEADING_LABELS = frozenset({"paragraph_title", "doc_title"})

NOT_CONFIGURED = (
    "Taranmış sayfalar için okuyucu ayarlanmamış (VA_PAGE_READER); belge okuyucuyu bekliyor."
)
UNREACHABLE = "Taranmış sayfaların okuyucusuna ulaşılamadı; belge okuyucuyu bekliyor."


# --- Ölçülmüş kodun kopyası: eşdeğerlik (evals/ocr_truth.py) ---

_VULGAR = {
    "½": "1/2",
    "⅓": "1/3",
    "⅔": "2/3",
    "¼": "1/4",
    "¾": "3/4",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
}
_SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
_SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_SCRIPT_FRACTION_RE = re.compile(r"(\d?)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)[⁄/∕]([₀₁₂₃₄₅₆₇₈₉0-9]+)")
_LATEX_FRACTION_RE = re.compile(r"(\d?)\s*\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}")
_MINUS_RE = re.compile(r"[−–‑]")
_SIGN_SPACE_RE = re.compile(r"(?<![\w)])- +(?=\d)")
_SLASH_SPACE_RE = re.compile(r"(?<=\d) */ *(?=\d)")
_QUOTES = str.maketrans({"″": '"', "“": '"', "”": '"', "’": "'", "‘": "'", "$": None})


def _script_fraction(match: re.Match[str]) -> str:
    lead, top, bottom = match.groups()
    space = " " if lead else ""
    return f"{lead}{space}{top.translate(_SUPER)}/{bottom.translate(_SUB)}"


def canonical(text: str) -> str:
    """Değerin karşılaştırılan yazımı: kesir, eksi, boşluk ve tırnak yazımları tekleşir."""
    text = _LATEX_FRACTION_RE.sub(
        lambda m: f"{m.group(1)} {m.group(2)}/{m.group(3)}".lstrip(), text
    )
    for glyph, plain in _VULGAR.items():
        text = re.sub(rf"(\d?){glyph}", rf"\1 {plain}", text)
    text = _SCRIPT_FRACTION_RE.sub(_script_fraction, text)
    text = text.replace("⁄", "/").replace("∕", "/").translate(_QUOTES)
    text = _MINUS_RE.sub("-", text)
    text = " ".join(text.split())
    text = _SIGN_SPACE_RE.sub("-", text)
    text = _SLASH_SPACE_RE.sub("/", text)
    return text.replace(" %", "%")


# --- Ölçülmüş kodun kopyası: sayarak karşılaştırma (evals/ocr_score.py) ---


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


_TOKEN_EDGES = ".,;:()[]{}|\"'"
_CODE_RE = re.compile(r"^[A-ZÇĞİÖŞÜ]{2,}(?:-[A-Z0-9ÇĞİÖŞÜ]+)*$")
"""Rakamsız kod: en az iki büyük harf, tireyle parçalar ("AXL", "XS-AXL")."""


def value_tokens(text: str) -> list[str]:
    """Karşılaştırılan sayı ve kod parçaları: rakam içeren her parça ve rakamsız kodlar.
    "27 1/2" iki parçadır: "27" ve "1/2"."""
    tokens = []
    for raw in canonical(text).split():
        token = raw.strip(_TOKEN_EDGES)
        if token and (any(ch.isdigit() for ch in token) or _CODE_RE.match(token)):
            tokens.append(token)
    return tokens


def count_mismatches(primary: str, second: str) -> list[str]:
    """Birinci okumanın sayı ve kod parçalarından, iki okumada geçiş sayısı farklı olanlar.
    Bilinen zayıflık: aynı bloktaki iki hata birbirini dengelerse sayılar tutar ve geçer."""
    first, other = Counter(value_tokens(primary)), Counter(value_tokens(second))
    return sorted(token for token, count in first.items() if other[token] != count)


SecondReader = Callable[[Image.Image], str]
_BLOCK_PAD = 4


def _block_text(block: Mapping[str, Any]) -> str:
    content = str(block.get("block_content") or "")
    if block.get("block_label") == "table":
        return " ".join(text for row in html_rows(content) for text in row)
    return content


def second_reading_marks(
    data: Mapping[str, Any], image: Image.Image, read: SecondReader
) -> dict[int, list[str]]:
    """Her blok için ikinci okumayla geçiş sayısı tutmayan parçalar ({blok numarası: [parça]}).
    Blok kutusu okuyucuya verilen görüntünün pikselidir."""
    scale_x = image.width / float(data.get("width") or image.width)
    scale_y = image.height / float(data.get("height") or image.height)
    marks: dict[int, list[str]] = {}
    for block in data["parsing_res_list"]:
        content = _block_text(block)
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


def tesseract_reader(executable: str, language: str = "tur+eng") -> SecondReader:
    """İkinci okuma: Tesseract, eğiklik düzeltmesiz, seyrek kip (psm 11): sayım için sıra
    gerekmez, tablodaki dağınık hücreler de okunur."""

    def read(image: Image.Image) -> str:
        with tempfile.TemporaryDirectory() as work:
            source = Path(work) / "blok.png"
            image.save(source)
            return tesseract_text(executable, source, language, "11", _TESSERACT_TIMEOUT_SECONDS)

    return read


# --- Bloklardan öğelere ---


def _uncertain(text: str, tokens: Sequence[str]) -> tuple[str, ...]:
    present = set(value_tokens(text))
    return tuple(token for token in tokens if token in present)


_DIGIT_RE = re.compile(r"\d")


def _first_row_is_header(rows: Sequence[Sequence[str]]) -> bool:
    """Okuyucu başlık hücresini işaretlemez (HTML'de yalnız <td> var); karar tablonun yapısından
    verilir. Başlık kanıtı: bir sütunda ilk hücrede rakam yok, altındaki dolu hücrelerin en az
    yarısında var (etiketin altında değerler). Karşı kanıt: ilk hücrede rakam var, altındakilerin
    çoğunda yok (ilk hücre kendisi bir değer). Form gibi tablolarda (etiket ile değeri aynı
    satırda yan yana) kanıt çıkmaz ya da karşı kanıt çıkar: ilk satır başlık değildir."""
    evidence = counter = False
    for column in range(max((len(row) for row in rows), default=0)):
        head = rows[0][column] if column < len(rows[0]) else ""
        body = [row[column] for row in rows[1:] if column < len(row) and row[column].strip()]
        if not head.strip() or not body:
            continue
        numeric = sum(bool(_DIGIT_RE.search(cell)) for cell in body) * 2 >= len(body)
        if _DIGIT_RE.search(head):
            counter = counter or not numeric
        else:
            evidence = evidence or numeric
    return evidence and not counter


EMPTY_CELL = "(boş)"
"""Boş hücre işareti. Tire ya da çizgi gerçek belgelerde kendisi bir değer olabilir ("—", "-");
açık bir sözcük hücrenin boş olduğunu söyler (ürün sahibi kararı, 2026-11-17)."""


def _with_empty_cells_marked(row: Sequence[str]) -> list[str]:
    """Okunduğu gibi yazılan satırda aradaki boş hücre yerini korur: atılırsa etiket bir sonraki
    hücreyle yan yana kalır ve onun değeri sanılır ("Supplier Request Round | Material
    Description | …"). Satır sonundaki boş hücreler yazılmaz."""
    filled = len(row)
    while filled and not row[filled - 1].strip():
        filled -= 1
    return [cell if cell.strip() else EMPTY_CELL for cell in row[:filled]]


def _table_elements(content: str, location: SourceLocation, tokens: Sequence[str]) -> list[Element]:
    """Başlıklı tabloda satır "Başlık: değer" biçimindedir; başlıksız tabloda (form, tek satır)
    satır okunduğu gibi kalır: hücreler sırayla, ilk satır da bir satırdır, aradaki boş hücre
    yerini korur. Başlık satırının hücre sayısı bir veri satırınınkinden farklıysa tablo da
    başlıksız yazılır: okuyucu bir hücreyi düşürdüyse başlıklar bir sütun kayar ve değer yanlış
    sütunun adını alır (fotoğrafta "S: Bel | M: 38,0"; doğrusu S 38,0). İkinci okuma bunu
    yakalamaz, sayılar doğrudur."""
    rows = [[canonical(text) for text in row] for row in html_rows(content)]
    aligned = all(len(row) == len(rows[0]) for row in rows)
    has_header = len(rows) > 1 and aligned and _first_row_is_header(rows)
    if not has_header:
        rows = [_with_empty_cells_marked(row) for row in rows]
    cells = [
        TableCell(r, r + 1, c, c + 1, text, header=has_header and r == 0)
        for r, row in enumerate(rows)
        for c, text in enumerate(row)
    ]
    return [
        Element(
            ElementKind.TABLE_ROW,
            row.text,
            location,
            from_ocr=True,
            # Bölüm etiketi ve tablo notu satırın bağlamına girer; değerleri de satıra bağlanır.
            ocr_uncertain=_uncertain(f"{row.text} {row.context}", tokens),
            ocr_checked=True,
            context=row.context,
        )
        for row in group_table_rows(cells, infer_header=False)
    ]


def page_elements(
    data: Mapping[str, Any],
    page: int,
    page_size: tuple[float, float],
    marks: Mapping[int, Sequence[str]],
) -> list[Element]:
    """Okuyucunun sayfa sonucu, okuma sırasıyla öğelere çevrilir. Metin karşılaştırılan yazımla
    yazılır ("14⅞" → "14 7/8"): belirsiz değerler cevap denetiminde aynı yazımla aranır.
    Tabloda hücre konumu yoktur; satırın kaynağı tablonun kutusudur."""
    width, height = page_size
    scale_x = width / float(data.get("width") or width)
    scale_y = height / float(data.get("height") or height)
    elements: list[Element] = []
    for block in data["parsing_res_list"]:
        content = str(block.get("block_content") or "")
        if not content.strip():
            continue
        left, top, right, bottom = block["block_bbox"]
        box = Box(
            page=page,
            left=left * scale_x,
            top=top * scale_y,
            right=right * scale_x,
            bottom=bottom * scale_y,
            page_width=width,
            page_height=height,
        )
        location = SourceLocation(page=page, boxes=(box,))
        tokens = marks.get(int(block.get("block_id", -1)), ())
        if block.get("block_label") == "table":
            elements += _table_elements(content, location, tokens)
            continue
        text = canonical(content)
        heading = block.get("block_label") in _HEADING_LABELS
        elements.append(
            Element(
                ElementKind.HEADING if heading else ElementKind.TEXT,
                text,
                location,
                from_ocr=True,
                ocr_uncertain=_uncertain(text, tokens),
                ocr_checked=True,
            )
        )
    return elements


# --- Okuyucu ---


@dataclass(frozen=True)
class ReaderConfig:
    backend: str
    url: str | None = None


def parse_reader_setting(value: str | None) -> ReaderConfig | None:
    """`VA_PAGE_READER`: "local" (model bu süreçte; GPU varsa onu, yoksa işlemciyi kullanır) ya
    da "<arka uç>@<adres>" (ör. "mlx-vlm-server@http://localhost:8111/"). Boşsa okuyucu yoktur."""
    if value is None or not value.strip():
        return None
    backend, _, url = value.strip().partition("@")
    if backend == LOCAL_BACKEND and not url:
        return ReaderConfig(LOCAL_BACKEND)
    if not backend or backend == LOCAL_BACKEND or not url.startswith(("http://", "https://")):
        raise ValueError(
            f'VA_PAGE_READER "local" ya da "<arka uç>@http://adres/" biçiminde olmalı: {value!r}'
        )
    return ReaderConfig(backend, url)


def _result_data(result: Any) -> dict[str, Any]:
    data = result.json
    inner = data.get("res", data)
    if not isinstance(inner, dict) or "parsing_res_list" not in inner:
        raise ReaderUnavailable(UNREACHABLE)
    return inner


class PaddleVlReader:
    """PaddleOCR-VL'nin resmi akışı. Model ve sunucu bağlantısı ilk sayfada kurulur."""

    def __init__(self, config: ReaderConfig) -> None:
        self._config = config
        self._pipeline: Any = None

    def _check_server(self) -> None:
        if self._config.url is None:
            return
        try:
            httpx.get(self._config.url, timeout=_SERVER_TIMEOUT_SECONDS)
        except httpx.HTTPError as error:
            raise ReaderUnavailable(UNREACHABLE) from error

    def _open(self) -> Any:
        if self._pipeline is None:
            try:
                from paddleocr import PaddleOCRVL
            except ImportError as error:
                raise ReaderUnavailable(NOT_CONFIGURED) from error
            server = (
                {}
                if self._config.url is None
                else {
                    "vl_rec_backend": self._config.backend,
                    "vl_rec_server_url": self._config.url,
                    "vl_rec_api_model_name": _MODEL,
                    # Bloklar sunucuya tek tek gider. Aynı anda giden istekleri sunucu birlikte
                    # işler ve çıktı isteklerin denk gelişine göre değişir: aynı fotoğrafta
                    # tablonun başlık hücresi bir okumada düştü, sonrakilerde düşmedi.
                    "vl_rec_max_concurrency": 1,
                }
            )
            self._pipeline = PaddleOCRVL(pipeline_version=_PIPELINE_VERSION, **server)
        return self._pipeline

    def read(self, image_path: Path) -> dict[str, Any]:
        """Okuyucunun hatası belgeyi bozuk saydırmaz: belge okuyucuyu bekler."""
        self._check_server()
        try:
            results = list(self._open().predict(str(image_path)))
            return _result_data(results[0])
        except ReaderUnavailable:
            raise
        except Exception as error:
            logger.exception("Sayfa okuyucusu sayfayı okuyamadı")
            raise ReaderUnavailable(UNREACHABLE) from error


_OCR_LAYER_SHARE = 0.9
"""Metin nesnelerinin bu kadarı gizliyse sayfanın metni bir taramanın OCR katmanıdır."""


def is_ocr_layer(page: Any, page_area: float) -> bool:
    """Sayfayı kaplayan bir görüntü var ve metin görünmüyor: yazım kipi görünmez ya da metin
    o görüntünün altında. Böyle metin dijital değil, başka bir aracın OCR çıktısıdır
    (ocrmypdf, tarayıcı yazılımı); sayfa taranmış sayılır ve sayfa okuyucusuna gider."""
    kinds = [pdfium_c.FPDF_PAGEOBJ_IMAGE, pdfium_c.FPDF_PAGEOBJ_TEXT]
    items = [(item, item.get_bounds()) for item in page.get_objects(filter=kinds, max_depth=4)]
    covers = [
        (index, bounds)
        for index, (item, bounds) in enumerate(items)
        if item.type == pdfium_c.FPDF_PAGEOBJ_IMAGE
        and (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]) >= IMAGE_COVER_RATIO * page_area
    ]
    texts = [
        (index, item, bounds)
        for index, (item, bounds) in enumerate(items)
        if item.type == pdfium_c.FPDF_PAGEOBJ_TEXT
    ]
    if not covers or not texts:
        return False
    hidden = sum(
        pdfium_c.FPDFTextObj_GetTextRenderMode(item.raw) == pdfium_c.FPDF_TEXTRENDERMODE_INVISIBLE
        or any(
            above > index
            and left >= cover[0] - 1
            and bottom >= cover[1] - 1
            and right <= cover[2] + 1
            and top <= cover[3] + 1
            for above, cover in covers
        )
        for index, item, (left, bottom, right, top) in texts
    )
    return bool(hidden >= _OCR_LAYER_SHARE * len(texts))


ReadPage = Callable[[Path], dict[str, Any]]


def _native_scale(page: Any) -> float:
    """Tarama kendi pikselleriyle okunur: sayfadaki en büyük görüntünün çözünürlüğü. Büyütülmüş
    görüntüde Tesseract'ın ikinci okuması bozulur (120 dpi tarama 300 dpi'ye çizilince tablodaki
    bütün değerler uyuşmadı, kendi çözünürlüğünde hepsi uyuştu). Görüntü yoksa 300 dpi."""
    best_area, scale = 0.0, RENDER_DPI / POINTS_PER_INCH
    for image in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE]):
        left, bottom, right, top = image.get_bounds()
        width, area = right - left, (right - left) * (top - bottom)
        if width > 0 and area > best_area:
            best_area, scale = area, image.get_px_size()[0] / width
    return scale


def page_reader_from_setting(value: str | None) -> ReadPage | None:
    """Ayar boşsa okuyucu yoktur; taranmış sayfası olan belgeler okuyucuyu bekler."""
    config = parse_reader_setting(value)
    if config is None:
        logger.warning(NOT_CONFIGURED)
        return None
    return PaddleVlReader(config).read


def read_scanned_pages(
    path: Path,
    pages: Sequence[int],
    work: Path,
    read_page: ReadPage | None,
    second: SecondReader,
    source_image: Path | None = None,
) -> list[Element]:
    """Metin katmanı olmayan sayfaları okur. Okuyucu yoksa ya da ulaşılamıyorsa
    `ReaderUnavailable`: sayfa başka yoldan okunmaz, belge okuyucuyu bekler.

    source_image: belge bir görsel dosyasıysa (jpg, png) dosyanın kendisi. Okuyucuya PDF'e
    çevrilmiş kopyası değil, kendi pikselleri verilir (yalnız çekim yönü düzeltilir)."""
    document = pypdfium2.PdfDocument(path)
    try:
        elements: list[Element] = []
        for number in pages:
            page = document[number - 1]
            if source_image is not None:
                with Image.open(source_image) as opened:
                    image = ImageOps.exif_transpose(opened).convert("RGB")
            else:
                image = page.render(scale=_native_scale(page)).to_pil().convert("RGB")
            darkest, _ = cast(tuple[int, int], image.convert("L").getextrema())
            if darkest >= _BLANK_LEVEL:
                continue  # boş sayfa: okunacak bir şey yok, okuyucu da gerekmez
            if read_page is None:
                raise ReaderUnavailable(NOT_CONFIGURED)
            source = work / f"okuyucu-s{number}.png"
            image.save(source)
            data = read_page(source)
            marks = second_reading_marks(data, image, second)
            elements += page_elements(data, number, page.get_size(), marks)
        return elements
    finally:
        document.close()
