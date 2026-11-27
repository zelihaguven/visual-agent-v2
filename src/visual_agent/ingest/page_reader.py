"""Taranmış sayfaların ve gömülü görsellerin okuyucusu: PaddleOCR-VL okur, ikinci okuma bloğu
yeniden okur (0011, 0028, 0035).

Karar 0010: sayfa PaddleOCR-VL'nin resmi akışıyla (düzen + bölge) okunur; her bloğun sayı ve
kodları ikinci okumanın aynı bloktaki okumasıyla sayılarak karşılaştırılır, sayısı tutmayan değer
belirsiz sayılır ve cevapta gizlenir. Karar 0035: OpenRouter anahtarı varsa ikinci okuma
Qwen3-VL'dir (ZDR), alınamayan blokta Tesseract; okuyucunun boş bıraktığı şekil bloklarını Qwen3-VL
okur, Gemma denetler.

Eşdeğerlik kuralları ve sayarak karşılaştırma `evals/ocr_score.py` ile `evals/ocr_truth.py`
içindeki ölçülmüş kodun kopyasıdır: o dosyalar sha256 ile donmuştur, uygulama da ölçüm
paketinden içe aktarmaz. İki kopyanın aynı sonucu verdiğini `tests/test_page_reader.py` set A
kaydı üzerinde sınar; biri değişirse test kırılır.
"""

import asyncio
import email.utils
import hashlib
import html
import io
import ipaddress
import json
import logging
import re
import tempfile
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

import httpx
import pypdfium2
import pypdfium2.raw as pdfium_c
from PIL import Image, ImageOps

from visual_agent.domain.document import Box, SourceLocation
from visual_agent.generation.helpers import JsonModel
from visual_agent.generation.openrouter import fetch_zdr_index, select_providers
from visual_agent.ingest.elements import (
    CLOUD_OUTAGE,
    CloudOutage,
    Element,
    ElementKind,
    carries_value,
    header_fits,
    report_progress,
    with_empty_cells_marked,
)
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
    "Taranmış sayfalar ve görseller için okuyucu ayarlanmamış (VA_PAGE_READER); belge okuyucuyu"
    " bekliyor."
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
_LATEX_FRACTION_RE = re.compile(
    r"(\d?)\s*\\[dt]?frac\{(\{)?([^{}]*)\}(?(2)\})\{(\{)?([^{}]*)\}(?(4)\})"
)
"""Okuyucu kesrin argümanlarını tek ya da çift süslü parantezle yazabilir ("1\\frac{{1}}{{8}}");
kapanış açılışla aynı sayıda parantezdir: kesre ait olmayan parantez yutulmaz."""
_LATEX_GROUP_RE = re.compile(
    r"\{(\s*-?\d*\s*\\[dt]?frac\{(\{)?[^{}]*\}(?(2)\})\{(\{)?[^{}]*\}(?(3)\})\s*)\}"
)
"""Kesri saran LaTeX grup parantezi biçimdir: "-{1\\frac{1}{4}}" "-1 1/4" okunur."""
_MINUS_RE = re.compile(r"[−–‑]")
_SIGN_SPACE_RE = re.compile(r"(?<![\w)])- +(?=\d)")
_SLASH_SPACE_RE = re.compile(r"(?<=\d) */ *(?=\d)")
_QUOTES = str.maketrans({"″": '"', "“": '"', "”": '"', "’": "'", "‘": "'", "$": None})


def _script_fraction(match: re.Match[str]) -> str:
    lead, top, bottom = match.groups()
    space = " " if lead else ""
    return f"{lead}{space}{top.translate(_SUPER)}/{bottom.translate(_SUB)}"


def canonical(text: str) -> str:
    """Değerin karşılaştırılan yazımı: kesir, eksi, boşluk ve tırnak yazımları tekleşir.
    Kesir yazımları ölçülmüş kopyadan (evals/ocr_truth.py) geniştir: çift parantezli argüman ve
    kesri saran grup parantezi (2026-11-26); set A okumalarında ikisi de geçmez."""
    text = _LATEX_GROUP_RE.sub(r"\1", text)
    text = _LATEX_FRACTION_RE.sub(
        lambda m: f"{m.group(1)} {m.group(3)}/{m.group(5)}".lstrip(), text
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


def _block_crop(
    data: Mapping[str, Any], image: Image.Image, block: Mapping[str, Any]
) -> Image.Image:
    """Bloğun kırpıntısı; blok kutusu okuyucuya verilen görüntünün pikselidir."""
    scale_x = image.width / float(data.get("width") or image.width)
    scale_y = image.height / float(data.get("height") or image.height)
    left, top, right, bottom = block["block_bbox"]
    return image.crop(
        (
            max(0, int(left * scale_x) - _BLOCK_PAD),
            max(0, int(top * scale_y) - _BLOCK_PAD),
            min(image.width, int(right * scale_x) + _BLOCK_PAD),
            min(image.height, int(bottom * scale_y) + _BLOCK_PAD),
        )
    )


def second_reading_marks(
    data: Mapping[str, Any], image: Image.Image, read: SecondReader
) -> dict[int, list[str]]:
    """Her blok için ikinci okumayla geçiş sayısı tutmayan parçalar ({blok numarası: [parça]})."""
    marks: dict[int, list[str]] = {}
    for block in data["parsing_res_list"]:
        content = _block_text(block)
        if not value_tokens(content):
            continue
        mismatched = count_mismatches(content, read(_block_crop(data, image, block)))
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


# --- Bulut okuması (karar 0035): ikinci okuma Qwen3-VL, şekil blokları Qwen3-VL + Gemma ---

CHECK_PROMPT = (
    "Görüntüdeki bütün yazıyı, sayıları ve işaretleri olduğu gibi aynen yaz. Tablo varsa her satırı"
    " ayrı satıra yaz, hücreleri ' | ' ile ayır. Düzeltme, çeviri, özet ya da yorum ekleme;"
    " okuyamadığını yazma. Yalnız metni ver."
)
FIGURE_PROMPT = (
    "Görseldeki bütün yazıları, sayıları ve etiketleri satır satır aynen yaz; tablo varsa"
    " satır/sütunla; yorum ekleme. Okuyamadığını yazma."
    ' Yalnız JSON ver: {"lines": ["..."], "tables": [{"rows": [["hücre", "..."]]}]}.'
    " Yazı yoksa boş listeler ver."
)
"""İki istem de ölçülen istemlerdir (docs/okuma-planlari.md, A-q1)."""
CHECK_MAX_TOKENS = 4096
FIGURE_MAX_TOKENS = 2048
_CLOUD_SECONDS = 120.0
_RATE_LIMIT_RETRIES = 3
"""429 (istek sınırı) alınan çağrı en çok bu kadar kez beklenip yeniden denenir."""
_RATE_LIMIT_FIRST_WAIT = 2.0
_RATE_LIMIT_MAX_WAIT = 60.0
_sleep = asyncio.sleep
"""Testler sahte uykuyla değiştirir."""


def _rate_limit_wait(response: httpx.Response, attempt: int) -> float:
    """Retry-After (saniye ya da HTTP tarihi) varsa ona uyulur, yoksa 2, 4, 8 sn; üst sınır
    60 sn."""
    header = str(response.headers.get("retry-after", "")).strip()
    wait: float = _RATE_LIMIT_FIRST_WAIT * 2**attempt
    if header:
        try:
            wait = float(header)
        except ValueError:
            try:
                when = email.utils.parsedate_to_datetime(header)
                wait = (when - datetime.now(when.tzinfo or UTC)).total_seconds()
            except (TypeError, ValueError):
                pass
    return min(max(wait, 0.0), _RATE_LIMIT_MAX_WAIT)


async def _read_with_retries(client: JsonModel, prompt: str, png: bytes, max_tokens: int) -> str:
    """429 alan çağrı beklenip yeniden denenir; denemeler tükenirse hata yükselir ve çağıran
    belgenin devresini açar."""
    for attempt in range(_RATE_LIMIT_RETRIES):
        try:
            return await client.read_image(prompt, png, max_tokens)
        except httpx.HTTPStatusError as error:
            if error.response.status_code != httpx.codes.TOO_MANY_REQUESTS:
                raise
            await _sleep(_rate_limit_wait(error.response, attempt))
    return await client.read_image(prompt, png, max_tokens)


class CloudUnavailable(RuntimeError):
    """Bulut okuması alınamadı: ağ, HTTP hatası, süre, ZDR sağlayıcısı yok."""


@dataclass(frozen=True)
class CloudConfig:
    base_url: str
    api_key: str
    cache: Path
    reader_model: str
    figure_check_model: str
    transport: httpx.AsyncBaseTransport | None = None
    """Yalnız testler verir."""


_REQUEST_ERRORS = frozenset({400, 413, 415, 422})
"""İsteğin kendisine özgü hatalar (bozuk ya da çok büyük görüntü): belgenin devresini açmaz."""


def _rejected_request(error: Exception) -> bool:
    """Okuma isteği bu bloğa özgü bir 4xx ile reddedildi: yalnız o blok yedeğe düşer. Ağ
    hatası, zaman aşımı, 5xx, kimlik/yetki hataları ve denemeleri tükenmiş 429 devreyi açar."""
    return (
        isinstance(error, httpx.HTTPStatusError)
        and error.response.status_code in _REQUEST_ERRORS
        and error.request.url.path.endswith("/chat/completions")
    )


def _cached_content(path: Path) -> str | None:
    """Önbellekteki cevap; dosya yoksa ya da bozuksa (yarım yazılmış, elle değişmiş) None:
    bozuk dosya yok sayılır, cevap yeniden istenir ve dosyanın üstüne yazılır."""
    try:
        content = json.loads(path.read_text(encoding="utf-8"))["content"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    return content if isinstance(content, str) else None


def cloud_reader(
    config: CloudConfig,
    model: str,
    prompt: str,
    max_tokens: int,
    accept: Callable[[str], bool] | None = None,
) -> SecondReader:
    """Bloğun kırpıntısını bulut modeli okur: buluta bütün sayfa değil blok gider, yalnız ZDR
    sağlayıcılarla (kural 4). Cevap diskte sha256(model + istem + görüntü) adıyla saklanır:
    aynı kırpıntı ikinci kez ödenmez. Okunamazsa `CloudUnavailable`; o modelin ilk hatasından
    sonra belgenin kalanında istek gitmez (`CLOUD_OUTAGE`, ZDR dizini de yeniden istenmez).

    accept: cevabın kullanılabilir olduğu denetimi (ör. şekil okumasında JSON). Kullanılamayan
    cevap önbelleğe yazılmaz ve bir kez yeniden istenir; yine kullanılamazsa olduğu gibi döner.
    Boş cevap da önbelleğe yazılmaz."""
    chosen: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    own = CloudOutage()

    async def call(png: bytes) -> str:
        async with httpx.AsyncClient(transport=config.transport, timeout=_CLOUD_SECONDS) as http:
            if not chosen:
                index = await fetch_zdr_index(http, config.base_url, config.api_key)
                chosen.append(select_providers(model, (), index))
            providers, ignored = chosen[0]
            client = JsonModel(http, config.base_url, config.api_key, model, providers, ignored)
            return await _read_with_retries(client, prompt, png, max_tokens)

    def read(image: Image.Image) -> str:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        png = buffer.getvalue()
        key = hashlib.sha256(b"\0".join([model.encode(), prompt.encode(), png])).hexdigest()
        cached = config.cache / f"{key}.json"
        if (stored := _cached_content(cached)) is not None:
            return stored
        outage = CLOUD_OUTAGE.get() or own
        if model in outage.reasons:
            raise CloudUnavailable(f"{model}: {outage.reasons[model]}")
        for _ in range(1 if accept is None else 2):
            try:
                content = asyncio.run(call(png))
            except Exception as error:  # okuma durmaz; çağıran yedeğe geçer ya da değeri gizler
                if _rejected_request(error):
                    logger.warning("Bulut bu bloğu reddetti; yalnız blok yedeğe düşer: %s", error)
                else:
                    outage.reasons[model] = repr(error)[:200]
                    logger.warning(
                        "Bulut okuması alınamadı; belgenin kalanında istenmez: %s", error
                    )
                raise CloudUnavailable(f"{model}: {error!r}"[:300]) from error
            if content.strip() and (accept is None or accept(content)):
                config.cache.mkdir(parents=True, exist_ok=True)
                partial = cached.with_suffix(".tmp")
                partial.write_text(
                    json.dumps({"model": model, "content": content}), encoding="utf-8"
                )
                partial.replace(cached)
                break
        return content

    return read


@dataclass(frozen=True)
class CloudReaders:
    """Bulut okuyucuları (karar 0035): `check` okuyucunun bloklarını ikinci kez okur; okuyucunun
    boş bıraktığı şekil bloklarını `figure_read` okur, `figure_check` denetler (ikisi de JSON).
    Sayfayı kaplayan blok da buluta gider (şirket onayı, 2026-11-27; karar 0035)."""

    check: SecondReader
    figure_read: SecondReader
    figure_check: SecondReader


def _checker(second: SecondReader, cloud: CloudReaders | None) -> SecondReader:
    """İkinci okuma: bulut varsa bulut; bulut okuması alınamayan blok bugünkü gibi `second`
    (Tesseract) ile denetlenir."""
    if cloud is None:
        return second

    def read(crop: Image.Image) -> str:
        try:
            return cloud.check(crop)
        except CloudUnavailable:
            outage = CLOUD_OUTAGE.get()
            if outage is not None:
                outage.fallback_blocks += 1
            return second(crop)

    return read


_FIGURE_LABELS = frozenset({"image", "chart", "figure", "seal", "header_image", "footer_image"})
FigurePart = tuple[str, str]
"""Şekil okumasının bir parçası, okuyucunun blok biçiminde: ("text", satır) ya da
("table", HTML tablo)."""
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def figure_parts(content: str) -> list[FigurePart] | None:
    """Şekil okumasının JSON'u parçalara: her satır bir metin, her tablo bir HTML tablo. JSON
    nesnesi yoksa None."""
    match = _JSON_OBJECT_RE.search(content)
    try:
        parsed = json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        parsed = None
    if not isinstance(parsed, dict):
        return None
    lines, tables = parsed.get("lines"), parsed.get("tables")
    parts = [
        ("text", str(line))
        for line in (lines if isinstance(lines, list) else [])
        if str(line).strip()
    ]
    for table in tables if isinstance(tables, list) else []:
        rows = table.get("rows") if isinstance(table, dict) else table
        cells = [
            [html.escape(str(cell)) for cell in (row if isinstance(row, list) else [row])]
            for row in (rows if isinstance(rows, list) else [])
        ]
        body = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in cells
            if any(cell.strip() for cell in row)
        )
        if body:
            parts.append(("table", f"<table>{body}</table>"))
    return parts


def _parts_text(parts: Sequence[FigurePart]) -> str:
    return " ".join(
        _block_text({"block_label": label, "block_content": content}) for label, content in parts
    )


def read_figures(
    data: Mapping[str, Any], image: Image.Image, readers: CloudReaders
) -> tuple[dict[int, list[FigurePart]], dict[int, list[str]]]:
    """Okuyucunun içeriğini boş bıraktığı şekil blokları ({blok numarası: parçalar}) ve
    denetimde geçiş sayısı tutmayan değerleri. Değer iki okumada sayısı tutarsa gösterilir;
    denetim okuması alınamazsa bloğun bütün değerleri belirsizdir (denetlenmeden gösterilmez)."""
    figures: dict[int, list[FigurePart]] = {}
    marks: dict[int, list[str]] = {}
    for block in data["parsing_res_list"]:
        if block.get("block_label") not in _FIGURE_LABELS or _block_text(block).strip():
            continue
        crop = _block_crop(data, image, block)
        if _is_blank(crop):
            continue
        try:
            parts = figure_parts(readers.figure_read(crop))
        except CloudUnavailable as error:
            logger.warning("Şekil bloğu okunamadı; atlanır: %s", error)
            continue
        if not parts:
            continue
        block_id = int(block["block_id"])
        figures[block_id] = parts
        primary = _parts_text(parts)
        if not value_tokens(primary):
            continue  # gizlenecek değer yok; denetim okumasına gerek yok
        try:
            other = readers.figure_check(crop)
        except CloudUnavailable as error:
            logger.warning("Şekil bloğu denetlenemedi; değerleri gizlenir: %s", error)
            marks[block_id] = sorted(set(value_tokens(primary)))
            continue
        checked = figure_parts(other)
        mismatched = count_mismatches(primary, other if checked is None else _parts_text(checked))
        if mismatched:
            marks[block_id] = mismatched
    return figures, marks


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


HeaderKey = tuple[str, ...]


def _header_key(row: Sequence[str]) -> HeaderKey:
    """Başlık satırının karşılaştırma biçimi: hücre hücre, boşluksuz ("// " ile "/ /" aynı)."""
    return tuple("".join(cell.split()) for cell in row)


def _table_elements(
    content: str,
    location: SourceLocation,
    tokens: Sequence[str],
    known_headers: frozenset[HeaderKey] = frozenset(),
    learned: set[HeaderKey] | None = None,
) -> list[Element]:
    """Başlıklı tabloda satır "Başlık: değer" biçimindedir; başlıksız tabloda (form, tek satır)
    satır okunduğu gibi kalır: hücreler sırayla, ilk satır da bir satırdır, aradaki boş hücre
    yerini korur. Başlık satırının hücre sayısı bir veri satırınınkinden farklıysa tablo da
    başlıksız yazılır: okuyucu bir hücreyi düşürdüyse başlıklar bir sütun kayar ve değer yanlış
    sütunun adını alır (fotoğrafta "S: Bel | M: 38,0"; doğrusu S 38,0). İkinci okuma bunu
    yakalamaz, sayılar doğrudur.

    Belgenin önceki sayfalarında yapıdan başlık sayılmış satırın birebir aynısı (known_headers)
    karşı kanıta rağmen başlıktır: belgeler sütun başlığını her sayfada tekrarlar, değerleri
    rakamsız olan sayfada ("As Artwork") rakamlı başlık hücresi ("100: White") karşı kanıt
    sayılıyordu. Yalnız yapıdan kabul edilen başlıklar öğrenilir (learned); kabul zincirlenmez."""
    rows = [[canonical(text) for text in row] for row in html_rows(content)]
    structural = len(rows) > 1 and _first_row_is_header(rows)
    repeated = len(rows) > 1 and _header_key(rows[0]) in known_headers
    has_header = len(rows) > 1 and header_fits(rows[0], rows[1:]) and (structural or repeated)
    if has_header and structural and learned is not None:
        learned.add(_header_key(rows[0]))
    if not has_header:
        rows = [with_empty_cells_marked(row) for row in rows]
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
            context=row.context,
        )
        for row in group_table_rows(cells, infer_header=False)
    ]


def page_elements(
    data: Mapping[str, Any],
    page: int,
    page_size: tuple[float, float],
    marks: Mapping[int, Sequence[str]],
    known_headers: frozenset[HeaderKey] = frozenset(),
    learned: set[HeaderKey] | None = None,
    region: Box | None = None,
    figures: Mapping[int, Sequence[FigurePart]] | None = None,
) -> list[Element]:
    """Okuyucunun sayfa sonucu, okuma sırasıyla öğelere çevrilir. Metin karşılaştırılan yazımla
    yazılır ("14⅞" → "14 7/8"): belirsiz değerler cevap denetiminde aynı yazımla aranır.
    Tabloda hücre konumu yoktur; satırın kaynağı tablonun kutusudur. region: okunan görüntü
    sayfanın bir bölgesiyse (gömülü görsel) kutular o bölgeden sayfaya taşınır; görseldeki başlık
    bölüm açmaz, metin olarak kalır (altındaki dijital metin görselin başlığına bağlanmasın).
    figures: okuyucunun boş bıraktığı şekil bloklarının bulut okuması (`read_figures`); şeklin
    her satırı ve tablosu bloğun yerinde ayrı öğedir."""
    page_width, page_height = page_size
    left0, top0 = (region.left, region.top) if region else (0.0, 0.0)
    width = region.right - region.left if region else page_width
    height = region.bottom - region.top if region else page_height
    scale_x = width / float(data.get("width") or width)
    scale_y = height / float(data.get("height") or height)
    elements: list[Element] = []
    for block in data["parsing_res_list"]:
        block_id = int(block.get("block_id", -1))
        content = str(block.get("block_content") or "")
        parts: Sequence[FigurePart] = (
            [(str(block.get("block_label")), content)]
            if content.strip()
            else (figures or {}).get(block_id, ())
        )
        if not parts:
            continue
        left, top, right, bottom = block["block_bbox"]
        box = Box(
            page=page,
            left=left0 + left * scale_x,
            top=top0 + top * scale_y,
            right=left0 + right * scale_x,
            bottom=top0 + bottom * scale_y,
            page_width=page_width,
            page_height=page_height,
        )
        location = SourceLocation(page=page, boxes=(box,))
        tokens = marks.get(block_id, ())
        for label, part in parts:
            if label == "table":
                elements += _table_elements(part, location, tokens, known_headers, learned)
                continue
            text = canonical(part)
            heading = region is None and label in _HEADING_LABELS
            element = Element(
                ElementKind.HEADING if heading else ElementKind.TEXT,
                text,
                location,
                from_ocr=True,
                ocr_uncertain=_uncertain(text, tokens),
            )
            elements.append(element)
            # Değer taşıyan başlık metin olarak da kalır (docling yolundaki kural).
            if heading and carries_value(text):
                elements.append(replace(element, kind=ElementKind.TEXT))
    return elements


# --- Okuyucu ---


@dataclass(frozen=True)
class ReaderConfig:
    backend: str
    url: str | None = None


def _on_local_network(url: str) -> bool:
    """Bu makine ya da yerel ağ: localhost, ".local" adı ya da özel/yerel IP adresi."""
    host = urlsplit(url).hostname or ""
    if host == "localhost" or host.endswith(".local"):
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address.is_private or address.is_loopback or address.is_link_local


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
    if not _on_local_network(url):
        # Okuyucuya bütün sayfa görüntüsü gider; ZDR denetimi yok (kural 4).
        raise ValueError(
            f"VA_PAGE_READER sunucusu bu makinede ya da yerel ağda olmalı "
            f"(localhost, .local adı ya da özel IP): {url!r}"
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


def _is_blank(image: Image.Image) -> bool:
    darkest, _ = cast(tuple[int, int], image.convert("L").getextrema())
    return darkest >= _BLANK_LEVEL


_Reading = tuple[dict[str, Any], dict[int, list[str]], dict[int, list[FigurePart]]]


def _read_image(
    image: Image.Image,
    source: Path,
    read_page: ReadPage | None,
    second: SecondReader,
    cloud: CloudReaders | None,
    whole_page: bool = False,
) -> _Reading | None:
    """Okuyucu sonucu, ikinci okumanın işaretleri ve şekil blokları; görüntü boşsa None (okuyucu
    gerekmez). Bulut yoksa ikinci okuma `second`, şekil blokları bugünkü gibi atlanır.
    whole_page: görüntü metin katmanı olmayan bir sayfanın tamamı; düzen modeli üzerinde hiç
    blok bulamazsa (Bold s.14) sayfa tek şekil bloğu sayılır ve şekil gibi okunur."""
    if _is_blank(image):
        return None
    if read_page is None:
        raise ReaderUnavailable(NOT_CONFIGURED)
    image.save(source)
    data = read_page(source)
    marks = second_reading_marks(data, image, _checker(second, cloud))
    if cloud is None:
        return data, marks, {}
    if whole_page and not data["parsing_res_list"]:
        width, height = data.get("width") or image.width, data.get("height") or image.height
        page_block = {"block_id": 0, "block_label": "image", "block_content": ""}
        data = {**data, "parsing_res_list": [{**page_block, "block_bbox": [0, 0, width, height]}]}
    read, figure_marks = read_figures(data, image, cloud)
    return data, {**marks, **figure_marks}, read


_MIN_IMAGE_SCALE = 1.0
_MAX_IMAGE_SCALE = 600 / POINTS_PER_INCH
"""Görsel 72–600 dpi arasında kendi çözünürlüğüyle çizilir: çok küçük çözünürlük okunamaz,
çok büyüğü (küçültülerek konmuş fotoğraf) belleği taşırır."""


def _image_scale(page: Any, box: Box) -> float:
    """Kutuyla en çok örtüşen görsel nesnesinin kendi çözünürlüğü (sınırlar içinde)."""
    height = page.get_size()[1]
    best, scale = 0.0, RENDER_DPI / POINTS_PER_INCH
    for image in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE], max_depth=4):
        left, bottom, right, top = image.get_bounds()
        overlap = max(0.0, min(right, box.right) - max(left, box.left)) * max(
            0.0, min(height - bottom, box.bottom) - max(height - top, box.top)
        )
        if overlap > best and right > left:
            best, scale = overlap, image.get_px_size()[0] / (right - left)
    return min(max(scale, _MIN_IMAGE_SCALE), _MAX_IMAGE_SCALE)


def read_embedded_images(
    path: Path,
    images: Sequence[Box],
    work: Path,
    read_page: ReadPage | None,
    second: SecondReader,
    cloud: CloudReaders | None = None,
) -> list[Element]:
    """Metinli sayfadaki gömülü görseller sayfa okuyucusuyla okunur (karar 0028): yalnız görselin
    bölgesi kendi çözünürlüğünde çizilir, öğelerin kutuları sayfaya taşınır. Okuyucu yoksa
    `ReaderUnavailable`: belge okuyucuyu bekler."""
    document = pypdfium2.PdfDocument(path)
    try:
        elements: list[Element] = []
        report_progress("images", 0, len(images))
        for index, box in enumerate(images):
            page = document[box.page - 1]
            width, height = page.get_size()
            margins = (box.left, height - box.bottom, width - box.right, box.top)
            bitmap = page.render(scale=_image_scale(page, box), crop=margins)
            crop = bitmap.to_pil().convert("RGB")
            source = work / f"okuyucu-s{box.page}-g{index}.png"
            read = _read_image(crop, source, read_page, second, cloud)
            if read is not None:
                data, marks, shapes = read
                elements += page_elements(
                    data, box.page, page.get_size(), marks, region=box, figures=shapes
                )
            report_progress("images", index + 1, len(images))
        return elements
    finally:
        document.close()


def read_scanned_pages(
    path: Path,
    pages: Sequence[int],
    work: Path,
    read_page: ReadPage | None,
    second: SecondReader,
    source_image: Path | None = None,
    cloud: CloudReaders | None = None,
) -> list[Element]:
    """Metin katmanı olmayan, zayıf ya da taranmış metin katmanlı sayfaları okur (0011, 0028).
    Okuyucu yoksa ya da ulaşılamıyorsa `ReaderUnavailable`: sayfa başka yoldan okunmaz, belge
    okuyucuyu bekler.

    source_image: belge bir görsel dosyasıysa (jpg, png) dosyanın kendisi. Okuyucuya PDF'e
    çevrilmiş kopyası değil, kendi pikselleri verilir (yalnız çekim yönü düzeltilir)."""
    document = pypdfium2.PdfDocument(path)
    try:
        elements: list[Element] = []
        known_headers: frozenset[HeaderKey] = frozenset()
        report_progress("pages", 0, len(pages))
        for done, number in enumerate(pages, start=1):
            page = document[number - 1]
            if source_image is not None:
                with Image.open(source_image) as opened:
                    image = ImageOps.exif_transpose(opened).convert("RGB")
            else:
                image = page.render(scale=_native_scale(page)).to_pil().convert("RGB")
            source = work / f"okuyucu-s{number}.png"
            read = _read_image(image, source, read_page, second, cloud, whole_page=True)
            if read is not None:  # boş sayfada okunacak bir şey yok, okuyucu da gerekmez
                data, marks, shapes = read
                learned: set[HeaderKey] = set()
                elements += page_elements(
                    data, number, page.get_size(), marks, known_headers, learned, figures=shapes
                )
                known_headers |= learned  # yalnız sonraki sayfalar için
            report_progress("pages", done, len(pages))
        return elements
    finally:
        document.close()
