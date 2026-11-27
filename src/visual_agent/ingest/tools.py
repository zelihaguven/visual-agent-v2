"""Dış araçlar: LibreOffice, Tesseract, sayfa okuyucusu ve Docling. İşçide çalışır."""

from functools import partial
from pathlib import Path
from typing import Any

import pypdfium2
import pypdfium2.raw as pdfium_c
from PIL import Image, ImageOps

from visual_agent.domain.document import Box, SourceLocation
from visual_agent.ingest.elements import Element, ElementKind, carries_value
from visual_agent.ingest.external import ExternalTools, locate_tools
from visual_agent.ingest.page_reader import (
    CHECK_MAX_TOKENS,
    CHECK_PROMPT,
    FIGURE_MAX_TOKENS,
    FIGURE_PROMPT,
    CloudConfig,
    CloudReaders,
    ReadPage,
    SecondReader,
    cloud_reader,
    figure_parts,
    is_ocr_layer,
    read_embedded_images,
    read_scanned_pages,
    tesseract_reader,
)
from visual_agent.ingest.pdf_tables import TableCell, group_table_rows
from visual_agent.ingest.pipeline import IngestTools, PageInfo
from visual_agent.ingest.text_layer import PageKind, classify_page, quality_score
from visual_agent.verification.text import identifiers_in

_IMAGE_PAGE_DPI = 150


def office_to_pdf(path: Path, work: Path, external: ExternalTools) -> Path:
    return external.convert(path, work, "pdf")


def legacy_spreadsheet_to_xlsx(path: Path, work: Path, external: ExternalTools) -> Path:
    return external.convert(path, work, "xlsx")


def image_to_pdf(path: Path, work: Path) -> Path:
    target = work / f"{path.stem}.pdf"
    with Image.open(path) as image:
        ImageOps.exif_transpose(image).convert("RGB").save(
            target, format="PDF", resolution=_IMAGE_PAGE_DPI
        )
    return target


def _image_boxes(page: Any, number: int, width: float, height: float) -> tuple[Box, ...]:
    boxes = []
    for item in page.get_objects(filter=[pdfium_c.FPDF_PAGEOBJ_IMAGE], max_depth=4):
        left, bottom, right, top = item.get_bounds()
        # Kırpılmış (clip) görselin sınırları sayfa dışına taşabilir: kutu sayfayla kesişir.
        left, right = max(left, 0.0), min(right, width)
        top, bottom = max(height - top, 0.0), min(height - bottom, height)
        if right > left and bottom > top:
            boxes.append(
                Box(
                    page=number,
                    left=left,
                    top=top,
                    right=right,
                    bottom=bottom,
                    page_width=width,
                    page_height=height,
                )
            )
    return tuple(boxes)


def _shifted(page: Any) -> bool:
    """Dönmüş ya da başlangıcı kaydırılmış sayfada görsel kutusu çizimle örtüşmez."""
    return bool(page.get_rotation()) or tuple(page.get_cropbox()[:2]) != (0.0, 0.0)


def _page_text(page: Any) -> str:
    return str(page.get_textpage().get_text_bounded())


def inspect_pdf(path: Path) -> list[PageInfo]:
    document = pypdfium2.PdfDocument(path)
    try:
        result = []
        for number, page in enumerate(document, start=1):
            width, height = page.get_size()
            text = _page_text(page)
            boxes = _image_boxes(page, number, width, height)
            area = sum((b.right - b.left) * (b.bottom - b.top) for b in boxes)
            cover = min(area / (width * height or 1.0), 1.0)
            chars = len(text.strip())
            kind = classify_page(chars, cover, quality_score(text))
            if is_ocr_layer(page, width * height):
                kind, chars = PageKind.NONE, 0  # OCR katmanı metin katmanı sayılmaz
            elif kind is PageKind.TEXT and boxes and _shifted(page):
                kind = PageKind.SCANNED  # görselli sayfa bütünüyle okuyucuya gider
            result.append(PageInfo(page=number, kind=kind, chars=chars, image_boxes=boxes))
        return result
    finally:
        document.close()


def _layer_text(path: Path, page_number: int) -> str:
    document = pypdfium2.PdfDocument(path)
    try:
        return _page_text(document[page_number - 1])
    finally:
        document.close()


def parse_pdf(path: Path) -> list[Element]:
    return parse_with_docling(path)


def recover_page_text(path: Path, page: int) -> list[Element]:
    text = _layer_text(path, page).strip()
    if not text:
        return []
    return [Element(ElementKind.TEXT, " ".join(text.split()), SourceLocation(page=page))]


def _second_reader(external: ExternalTools, read_page: ReadPage | None) -> SecondReader:
    """İkinci okuma ölçümdeki gibi Tesseract tur+eng; bulut varsa yalnız yedeği (0035).
    Tesseract yoksa belge bunu söyler. Okuyucu yoksa boş olmayan görüntü zaten okunamaz;
    Tesseract aranmaz."""
    if read_page is None:
        return lambda _: ""
    return tesseract_reader(external.require_tesseract("tur+eng"))


def _cloud_readers(cloud: CloudConfig | None) -> CloudReaders | None:
    """Anahtar yoksa ikinci okuma Tesseract, şekil blokları bugünkü gibi atlanır. Şekil
    okumasının JSON'u bozuk ya da yarımsa (token sınırı) bir kez yeniden istenir; yine bozuksa
    blok atlanır."""
    if cloud is None:
        return None
    return CloudReaders(
        check=cloud_reader(cloud, cloud.reader_model, CHECK_PROMPT, CHECK_MAX_TOKENS),
        figure_read=cloud_reader(
            cloud,
            cloud.reader_model,
            FIGURE_PROMPT,
            FIGURE_MAX_TOKENS,
            accept=lambda content: figure_parts(content) is not None,
        ),
        figure_check=cloud_reader(
            cloud, cloud.figure_check_model, FIGURE_PROMPT, FIGURE_MAX_TOKENS
        ),
        max_page_share=cloud.max_page_share,
    )


def _read_scanned(
    path: Path,
    pages: list[int],
    work: Path,
    image: Path | None,
    external: ExternalTools,
    read_page: ReadPage | None,
    cloud: CloudConfig | None,
) -> list[Element]:
    second = _second_reader(external, read_page)
    readers = _cloud_readers(cloud)
    return read_scanned_pages(path, pages, work, read_page, second, image, readers)


def _read_images(
    path: Path,
    images: list[Box],
    work: Path,
    external: ExternalTools,
    read_page: ReadPage | None,
    cloud: CloudConfig | None,
) -> list[Element]:
    second = _second_reader(external, read_page)
    readers = _cloud_readers(cloud)
    return read_embedded_images(path, images, work, read_page, second, readers)


def default_tools(
    external: ExternalTools | None = None,
    read_page: ReadPage | None = None,
    cloud: CloudConfig | None = None,
) -> IngestTools:
    """Araç yolları verilmezse PATH'te aranır. Sayfa okuyucusu yoksa yalnız metinli olmayan
    sayfası (metin katmansız, zayıf ya da taranmış katmanlı) olan belge okuyucuyu bekler.
    cloud: OpenRouter bağlantısı (0035); yoksa ikinci okuma Tesseract, şekil blokları atlanır."""
    found = external if external is not None else locate_tools(None, None)
    return IngestTools(
        read_scanned_pages=partial(_read_scanned, external=found, read_page=read_page, cloud=cloud),
        office_to_pdf=partial(office_to_pdf, external=found),
        legacy_spreadsheet_to_xlsx=partial(legacy_spreadsheet_to_xlsx, external=found),
        image_to_pdf=image_to_pdf,
        inspect_pdf=inspect_pdf,
        parse_pdf=parse_pdf,
        recover_page_text=recover_page_text,
        read_embedded_images=partial(
            _read_images, external=found, read_page=read_page, cloud=cloud
        ),
    )


# --- docling_parser ------------------------------------------------------------------------------
# Docling çıktısını ortak öğe biçimine çevirir.

_HEADING_LABELS = {"title", "section_header"}
_TEXT_LABELS = {"text", "paragraph", "list_item", "caption", "footnote", "formula"}
_CODE_LABELS = {"code"}
_TABLE_LABEL = "table"
_PAGE_HEADER_LABEL = "page_header"


def page_header_identifies(text: str) -> bool:
    """Model ya da belge kodu taşıyan üst bilgi bağlam olarak korunur, diğerleri atılır."""
    return bool(identifiers_in(text))


def _converter() -> Any:
    from docling.datamodel.base_models import InputFormat as DoclingFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    options = PdfPipelineOptions()
    options.do_ocr = False
    options.do_table_structure = True
    return DocumentConverter(
        format_options={DoclingFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )


def _label(item: Any) -> str:
    return str(getattr(item, "label", "")).split(".")[-1].lower()


def _box(document: Any, provenance: Any) -> Box:
    size = document.pages[provenance.page_no].size
    top_left = provenance.bbox.to_top_left_origin(page_height=size.height)
    return Box(
        page=provenance.page_no,
        left=top_left.l,
        top=top_left.t,
        right=top_left.r,
        bottom=top_left.b,
        page_width=size.width,
        page_height=size.height,
    )


def _location(boxes: tuple[Box, ...]) -> SourceLocation:
    return SourceLocation(page=boxes[0].page, boxes=boxes)


def _table_cells(item: Any, page_height: float) -> list[TableCell]:
    cells = []
    for cell in item.data.table_cells:
        bbox = None
        if cell.bbox is not None:
            top_left = cell.bbox.to_top_left_origin(page_height=page_height)
            bbox = (top_left.l, top_left.t, top_left.r, top_left.b)
        cells.append(
            TableCell(
                row_start=cell.start_row_offset_idx,
                row_end=cell.end_row_offset_idx,
                column_start=cell.start_col_offset_idx,
                column_end=cell.end_col_offset_idx,
                text=cell.text or "",
                header=bool(cell.column_header),
                bbox=bbox,
            )
        )
    return cells


def _table_elements(item: Any, table_box: Box) -> list[Element]:
    data = getattr(item, "data", None)
    if data is None or not data.table_cells:
        return []
    elements = []
    for row in group_table_rows(_table_cells(item, table_box.page_height)):
        box = table_box
        if row.bbox is not None:
            left, top, right, bottom = row.bbox
            box = table_box.model_copy(
                update={"left": left, "top": top, "right": right, "bottom": bottom}
            )
        location = SourceLocation(page=table_box.page, boxes=(box,))
        elements.append(Element(ElementKind.TABLE_ROW, row.text, location, context=row.context))
    return elements


def _item_elements(document: Any, item: Any) -> list[Element]:
    provenance = getattr(item, "prov", None) or []
    if not provenance:
        return []
    boxes = tuple(_box(document, entry) for entry in provenance)
    label = _label(item)
    if label == _TABLE_LABEL:
        return _table_elements(item, boxes[0])
    text = (getattr(item, "text", "") or "").strip()
    if not text:
        return []
    if label in _HEADING_LABELS:
        heading = Element(ElementKind.HEADING, text, _location(boxes))
        # Numaralı madde başlık sanılabiliyor ("1. Hood crossover should be 7/8""); değer taşıyan
        # başlık metin olarak da kalır, yoksa yalnız bölüm adı olur, aranamaz ve alıntılanamaz.
        if carries_value(text):
            return [heading, Element(ElementKind.TEXT, text, _location(boxes))]
        return [heading]
    if label == _PAGE_HEADER_LABEL and page_header_identifies(text):
        return [Element(ElementKind.HEADING, text, _location(boxes))]
    if label in _CODE_LABELS:
        return [Element(ElementKind.CODE, text, _location(boxes))]
    if label in _TEXT_LABELS:
        return [Element(ElementKind.TEXT, text, _location(boxes))]
    return []


_BODY, _FURNITURE = "body", "furniture"
"""Docling'in içerik katmanları (ContentLayer bir dizgi enum'u; docling burada yüklenmez)."""


def _kept(item: Any) -> bool:
    """Gövde öğeleri ve yalnız sayfa üst bilgisi: üst bilgi FURNITURE katmanındadır."""
    return getattr(item, "content_layer", _BODY) != _FURNITURE or _label(item) == _PAGE_HEADER_LABEL


def parse_with_docling(path: Path) -> list[Element]:
    """Sayfa üst bilgisi de gezilir: docling belgenin ilk satırını ("CKT-7308 ölçü föyü") üst
    bilgi sayıyordu ve yalnız gövde gezildiği için kod taşıyan üst bilgi kuralı hiç çalışmıyor,
    model kodu hiçbir parçaya geçmiyordu."""
    document = _converter().convert(str(path)).document
    return [
        element
        for item, _level in document.iterate_items(included_content_layers={_BODY, _FURNITURE})
        if _kept(item)
        for element in _item_elements(document, item)
    ]
