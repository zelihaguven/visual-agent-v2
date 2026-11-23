"""Bir dosyayı arama parçalarına ve kapsam raporuna dönüştürür."""

import re
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from visual_agent.domain.document import Box, Chunk, DocumentMeta, FrozenModel
from visual_agent.ingest.chunking import build_chunks
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.formats import (
    RULES_VERSIONS,
    UNRECORDED_RULES,
    InputFormat,
    detect_format,
)
from visual_agent.ingest.plain_text import parse_plain_text
from visual_agent.ingest.spreadsheet import parse_workbook
from visual_agent.ingest.text_layer import PageKind

_MIN_CAPTURED_TEXT_RATIO = 0.5
_SQL_STATEMENT = (
    r"^\s*(?:SELECT\b.+\bFROM\b|INSERT\s+INTO\b|UPDATE\b.+\bSET\b|DELETE\s+FROM\b|ALTER\s+TABLE\b"
    r"|CREATE\s+(?:TABLE|INDEX|VIEW)\b|DROP\s+(?:TABLE|INDEX|VIEW)\b|TRUNCATE\s+TABLE\b)"
)
_SQL_KEYWORDS_RE = re.compile(_SQL_STATEMENT, re.DOTALL)
_SQL_ANY_CASE_RE = re.compile(_SQL_STATEMENT, re.DOTALL | re.IGNORECASE)
IMAGES_NOT_SEARCHED = "Bu belgedeki görsellerin içeriği aranmaz."
"""Metinli sayfadaki gömülü görseller okunmaz (karar 0028)."""


@dataclass(frozen=True)
class PageInfo:
    page: int
    kind: PageKind
    chars: int
    image_boxes: tuple[Box, ...]


@dataclass(frozen=True)
class IngestTools:
    office_to_pdf: Callable[[Path, Path], Path]
    legacy_spreadsheet_to_xlsx: Callable[[Path, Path], Path]
    image_to_pdf: Callable[[Path, Path], Path]
    inspect_pdf: Callable[[Path], list[PageInfo]]
    read_scanned_pages: Callable[[Path, list[int], Path, Path | None], list[Element]]
    """Metin katmanı olmayan, zayıf ya da taranmış metin katmanlı sayfalar (karar 0011, 0028).
    Son değer: belge bir görsel dosyasıysa dosyanın kendisi (doğrudan okunur). Okuyucu yoksa
    `ReaderUnavailable`."""
    parse_pdf: Callable[[Path], list[Element]]
    recover_page_text: Callable[[Path, int], list[Element]]


class IngestReport(FrozenModel):
    doc_id: str
    page_count: int
    page_kinds: dict[str, int]
    ocr_pages: tuple[int, ...]
    uncertain_values: int
    chunks_by_kind: dict[str, int]
    warnings: tuple[str, ...]
    input_format: InputFormat | None = None
    rules_version: int = UNRECORDED_RULES


@dataclass(frozen=True)
class IngestResult:
    chunks: tuple[Chunk, ...]
    report: IngestReport
    display_pdf: Path | None


def _looks_like_sql(text: str) -> bool:
    if _SQL_KEYWORDS_RE.match(text):
        return True
    return text.rstrip().endswith(";") and _SQL_ANY_CASE_RE.match(text) is not None


def promote_code_elements(elements: Sequence[Element]) -> list[Element]:
    """Ayrıştırıcının düz metin saydığı komutları kod bloğuna çevirir."""
    return [
        replace(element, kind=ElementKind.CODE)
        if element.kind is ElementKind.TEXT and _looks_like_sql(element.text)
        else element
        for element in elements
    ]


def pages_missing_text(elements: Sequence[Element], pages: Sequence[PageInfo]) -> list[int]:
    """Ayrıştırıcının metin katmanının yarısından azını yakaladığı sayfalar."""
    captured: Counter[int] = Counter()
    for element in elements:
        if element.location.page is not None:
            captured[element.location.page] += len(element.text)
    return [
        page.page
        for page in pages
        if page.chars > 0 and captured[page.page] < page.chars * _MIN_CAPTURED_TEXT_RATIO
    ]


def _elements_from_pdf(
    pdf_path: Path, tools: IngestTools, work: Path, image: Path | None = None
) -> tuple[list[Element], list[PageInfo], list[int]]:
    pages = tools.inspect_pdf(pdf_path)
    # Metin katmanı olmayan, zayıf ya da taranmış metin katmanlı sayfalar yalnız sayfa
    # okuyucusundan geçer (karar 0028). Okuyucu yoksa belge hiç indekslenmez
    # (ReaderUnavailable yükselir).
    scanned = [page.page for page in pages if page.kind is not PageKind.TEXT]
    read = tools.read_scanned_pages(pdf_path, scanned, work, image) if scanned else []
    parsed = [
        element
        for element in promote_code_elements(tools.parse_pdf(pdf_path))
        if element.location.page not in scanned
    ]
    text_pages = [page for page in pages if page.kind is PageKind.TEXT]
    recovered = [
        element
        for page in pages_missing_text(parsed, text_pages)
        for element in tools.recover_page_text(pdf_path, page)
    ]
    combined = [*parsed, *recovered, *read]
    return sorted(combined, key=lambda element: element.location.page or 0), pages, scanned


@dataclass(frozen=True)
class _Parsed:
    elements: list[Element]
    warnings: Sequence[str] = ()
    pages: Sequence[PageInfo] = ()
    read_pages: Sequence[int] = ()
    display_pdf: Path | None = None


def _build_report(
    meta: DocumentMeta,
    input_format: InputFormat,
    chunks: Sequence[Chunk],
    parsed: _Parsed,
) -> IngestReport:
    empty = () if chunks else ("Belgeden okunabilir içerik çıkarılamadı.",)
    warnings = (*empty, *parsed.warnings)
    pages = parsed.pages
    return IngestReport(
        doc_id=meta.doc_id,
        page_count=len(pages),
        page_kinds=dict(Counter(page.kind.value for page in pages)),
        ocr_pages=tuple(sorted(parsed.read_pages)),
        # Sayfa başına tekil değer: başlıktaki belirsiz değer altındaki her parçaya taşınır
        # (doğrulama için), değer taşıyan başlık metin olarak da kalır, satır bağlamı gruptaki
        # her satıra yazılır; belgenin "net okunamadı" sayısında aynı değer bir kez geçer.
        uncertain_values=len(
            {
                (element.location.page, element.location.sheet, token)
                for element in parsed.elements
                for token in element.ocr_uncertain
            }
        ),
        chunks_by_kind=dict(Counter(chunk.kind.value for chunk in chunks)),
        warnings=warnings,
        input_format=input_format,
        rules_version=RULES_VERSIONS[input_format],
    )


def _pdf_source(path: Path, input_format: InputFormat, tools: IngestTools, work: Path) -> Path:
    if input_format is InputFormat.OFFICE:
        return tools.office_to_pdf(path, work)
    if input_format is InputFormat.IMAGE:
        return tools.image_to_pdf(path, work)
    return path


def _parse(path: Path, input_format: InputFormat, tools: IngestTools, work: Path) -> _Parsed:
    if input_format in (InputFormat.SQL, InputFormat.TEXT, InputFormat.MARKDOWN):
        return _Parsed(parse_plain_text(path, input_format))
    if input_format is InputFormat.SPREADSHEET:
        return _Parsed(*parse_workbook(path))
    if input_format is InputFormat.LEGACY_SPREADSHEET:
        return _Parsed(*parse_workbook(tools.legacy_spreadsheet_to_xlsx(path, work)))
    pdf_path = _pdf_source(path, input_format, tools, work)
    image = path if input_format is InputFormat.IMAGE else None
    elements, pages, read_pages = _elements_from_pdf(pdf_path, tools, work, image)
    has_images = any(page.kind is PageKind.TEXT and page.image_boxes for page in pages)
    warnings = (IMAGES_NOT_SEARCHED,) if has_images else ()
    return _Parsed(elements, warnings, pages, read_pages, pdf_path)


def ingest_document(path: Path, meta: DocumentMeta, tools: IngestTools, work: Path) -> IngestResult:
    input_format = detect_format(path)
    parsed = _parse(path, input_format, tools, work)
    chunks = tuple(build_chunks(parsed.elements, meta))
    report = _build_report(meta, input_format, chunks, parsed)
    return IngestResult(chunks, report, parsed.display_pdf)
