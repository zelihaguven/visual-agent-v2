"""Bir dosyayı arama parçalarına ve kapsam raporuna dönüştürür."""

import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
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
from visual_agent.ingest.two_reading import page_ranges
from visual_agent.verification.text import contains_token

_MIN_CAPTURED_TEXT_RATIO = 0.5
_SQL_STATEMENT = (
    r"^\s*(?:SELECT\b.+\bFROM\b|INSERT\s+INTO\b|UPDATE\b.+\bSET\b|DELETE\s+FROM\b|ALTER\s+TABLE\b"
    r"|CREATE\s+(?:TABLE|INDEX|VIEW)\b|DROP\s+(?:TABLE|INDEX|VIEW)\b|TRUNCATE\s+TABLE\b)"
)
_SQL_KEYWORDS_RE = re.compile(_SQL_STATEMENT, re.DOTALL)
_SQL_ANY_CASE_RE = re.compile(_SQL_STATEMENT, re.DOTALL | re.IGNORECASE)


@dataclass(frozen=True)
class PageInfo:
    page: int
    kind: PageKind
    chars: int
    image_boxes: tuple[Box, ...]


@dataclass(frozen=True)
class OcrOutcome:
    pdf_path: Path
    ocr_pages: Mapping[int, tuple[str, ...]]
    # OCR okuması kalite eşiğinin altında kaldığı için metni indekse girmeyen sayfalar.
    image_only_pages: tuple[int, ...] = ()


@dataclass(frozen=True)
class IngestTools:
    office_to_pdf: Callable[[Path, Path], Path]
    legacy_spreadsheet_to_xlsx: Callable[[Path, Path], Path]
    image_to_pdf: Callable[[Path, Path], Path]
    inspect_pdf: Callable[[Path], list[PageInfo]]
    run_ocr: Callable[[Path, list[PageInfo], str, Path], OcrOutcome]
    parse_pdf: Callable[[Path], list[Element]]
    read_embedded_images: Callable[[Path, list[PageInfo], str], list[Element]]
    recover_page_text: Callable[[Path, int], list[Element]]
    skipped_image_warnings: Callable[[list[PageInfo]], list[str]]


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


def annotate_ocr_pages(
    elements: Sequence[Element], ocr_pages: Mapping[int, tuple[str, ...]]
) -> list[Element]:
    """OCR'dan gelen sayfaların öğelerini işaretler, belirsiz değerleri bağlar."""
    annotated = []
    for element in elements:
        page = element.location.page
        if page is None or page not in ocr_pages:
            annotated.append(element)
            continue
        uncertain = tuple(t for t in ocr_pages[page] if contains_token(element.text, t))
        annotated.append(replace(element, from_ocr=True, ocr_uncertain=uncertain))
    return annotated


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
    pdf_path: Path, meta: DocumentMeta, tools: IngestTools, work: Path
) -> tuple[list[Element], list[PageInfo], OcrOutcome]:
    pages = tools.inspect_pdf(pdf_path)
    outcome = tools.run_ocr(pdf_path, pages, meta.language, work)
    parsed = annotate_ocr_pages(
        promote_code_elements(tools.parse_pdf(outcome.pdf_path)), outcome.ocr_pages
    )
    recovered = annotate_ocr_pages(
        [
            element
            for page in pages_missing_text(parsed, pages)
            for element in tools.recover_page_text(outcome.pdf_path, page)
        ],
        outcome.ocr_pages,
    )
    images = tools.read_embedded_images(outcome.pdf_path, pages, meta.language)
    combined = [*parsed, *recovered, *images]
    return sorted(combined, key=lambda element: element.location.page or 0), pages, outcome


@dataclass(frozen=True)
class _Parsed:
    elements: list[Element]
    warnings: Sequence[str] = ()
    pages: Sequence[PageInfo] = ()
    outcome: OcrOutcome | None = None


def _build_report(
    meta: DocumentMeta,
    input_format: InputFormat,
    chunks: Sequence[Chunk],
    parsed: _Parsed,
) -> IngestReport:
    empty = () if chunks else ("Belgeden okunabilir içerik çıkarılamadı.",)
    warnings = (*empty, *parsed.warnings)
    pages, outcome = parsed.pages, parsed.outcome
    return IngestReport(
        doc_id=meta.doc_id,
        page_count=len(pages),
        page_kinds=dict(Counter(page.kind.value for page in pages)),
        ocr_pages=tuple(sorted(outcome.ocr_pages)) if outcome else (),
        uncertain_values=sum(len(chunk.ocr_uncertain) for chunk in chunks),
        chunks_by_kind=dict(Counter(chunk.kind.value for chunk in chunks)),
        warnings=warnings,
        input_format=input_format,
        rules_version=RULES_VERSIONS[input_format],
    )


def _image_only_warnings(outcome: OcrOutcome) -> list[str]:
    if not outcome.image_only_pages:
        return []
    pages = page_ranges(outcome.image_only_pages)
    return [f"Sayfa {pages}: metin okunamadı, yalnız görüntü olarak kaldı; aramada bulunmaz."]


def _pdf_source(path: Path, input_format: InputFormat, tools: IngestTools, work: Path) -> Path:
    if input_format is InputFormat.OFFICE:
        return tools.office_to_pdf(path, work)
    if input_format is InputFormat.IMAGE:
        return tools.image_to_pdf(path, work)
    return path


def _parse(
    path: Path, input_format: InputFormat, meta: DocumentMeta, tools: IngestTools, work: Path
) -> _Parsed:
    if input_format in (InputFormat.SQL, InputFormat.TEXT, InputFormat.MARKDOWN):
        return _Parsed(parse_plain_text(path, input_format))
    if input_format is InputFormat.SPREADSHEET:
        return _Parsed(*parse_workbook(path))
    if input_format is InputFormat.LEGACY_SPREADSHEET:
        return _Parsed(*parse_workbook(tools.legacy_spreadsheet_to_xlsx(path, work)))
    pdf_path = _pdf_source(path, input_format, tools, work)
    elements, pages, outcome = _elements_from_pdf(pdf_path, meta, tools, work)
    warnings = [*_image_only_warnings(outcome), *tools.skipped_image_warnings(pages)]
    return _Parsed(elements, warnings, pages, outcome)


def ingest_document(path: Path, meta: DocumentMeta, tools: IngestTools, work: Path) -> IngestResult:
    input_format = detect_format(path)
    parsed = _parse(path, input_format, meta, tools, work)
    chunks = tuple(build_chunks(parsed.elements, meta))
    report = _build_report(meta, input_format, chunks, parsed)
    display_pdf = parsed.outcome.pdf_path if parsed.outcome else None
    return IngestResult(chunks, report, display_pdf)
