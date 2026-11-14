"""Docling çıktısını ortak öğe biçimine çevirir."""

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

from visual_agent.domain.document import Box, SourceLocation
from visual_agent.ingest.cell_reader import CellRead
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.pdf_tables import BoundingBox, TableCell, group_table_rows
from visual_agent.verification.text import contains_token, identifiers_in

_HEADING_LABELS = {"title", "section_header"}
_TEXT_LABELS = {"text", "paragraph", "list_item", "caption", "footnote", "formula"}
_CODE_LABELS = {"code"}
_TABLE_LABEL = "table"
_PAGE_HEADER_LABEL = "page_header"
_MAX_REREAD_CHARS = 16
"""Yeniden okunan hücre kısadır (ölçü, tolerans, kod); uzun metin hücreleri olduğu gibi kalır."""
_DIGIT_RE = re.compile(r"\d")

ReadCells = Callable[[int, Sequence[BoundingBox]], list[CellRead | None]]
"""Sayfa numarası ve hücre kutuları (nokta, sol-üst köşe) → okumalar; okunmayan hücre None."""


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


def _rereadable(cell: TableCell) -> bool:
    """Tek sütun ve tek satırlık kısa gövde hücresi; birleşik hücre hangi sütuna ait belirsizdir."""
    text = cell.text.strip()
    single = cell.column_end - cell.column_start == 1 and cell.row_end - cell.row_start == 1
    return (
        single and not cell.header and cell.bbox is not None and 0 < len(text) <= _MAX_REREAD_CHARS
    )


def _unsure_tokens(text: str) -> list[str]:
    return [token for token in text.split() if _DIGIT_RE.search(token)]


def reread_cells(
    cells: Sequence[TableCell],
    page: int,
    read_cells: ReadCells,
    page_uncertain: Sequence[str] = (),
) -> tuple[list[TableCell], list[str]]:
    """Kesinleşen okuma hücrenin yerine geçer; kesinleşmeyen hücrenin sayıları belirsizdir.

    Yeniden okunmayan hücrelerde (başlık, uzun metin) sayfanın iki okuma karşılaştırması geçerlidir.
    """
    targets = [index for index, cell in enumerate(cells) if _rereadable(cell)]
    boxes = [box for index in targets if (box := cells[index].bbox) is not None]
    reads = dict(zip(targets, read_cells(page, boxes), strict=True))
    updated, unsure = list(cells), []
    for index, cell in enumerate(cells):
        if index not in reads:
            unsure += [token for token in page_uncertain if contains_token(cell.text, token)]
            continue
        read = reads[index]
        if read is not None and read.confirmed:
            updated[index] = replace(cell, text=read.text)
        else:
            unsure += _unsure_tokens(cell.text)
    return updated, unsure


def _table_elements(
    item: Any,
    table_box: Box,
    read_cells: ReadCells | None = None,
    page_uncertain: Sequence[str] = (),
) -> list[Element]:
    data = getattr(item, "data", None)
    if data is None or not data.table_cells:
        return []
    cells = _table_cells(item, table_box.page_height)
    unsure: list[str] = []
    if read_cells is not None:
        cells, unsure = reread_cells(cells, table_box.page, read_cells, page_uncertain)
    elements = []
    for row in group_table_rows(cells):
        box = table_box
        if row.bbox is not None:
            left, top, right, bottom = row.bbox
            box = table_box.model_copy(
                update={"left": left, "top": top, "right": right, "bottom": bottom}
            )
        elements.append(
            Element(
                ElementKind.TABLE_ROW,
                row.text,
                SourceLocation(page=table_box.page, boxes=(box,)),
                from_ocr=read_cells is not None,
                ocr_uncertain=tuple(
                    dict.fromkeys(token for token in unsure if contains_token(row.text, token))
                ),
                ocr_checked=read_cells is not None,
            )
        )
    return elements


def _item_elements(
    document: Any,
    item: Any,
    read_cells: ReadCells | None,
    ocr_pages: Mapping[int, Sequence[str]],
) -> list[Element]:
    provenance = getattr(item, "prov", None) or []
    if not provenance:
        return []
    boxes = tuple(_box(document, entry) for entry in provenance)
    label = _label(item)
    if label == _TABLE_LABEL:
        page = boxes[0].page
        if page not in ocr_pages:
            return _table_elements(item, boxes[0])
        return _table_elements(item, boxes[0], read_cells, ocr_pages[page])
    text = (getattr(item, "text", "") or "").strip()
    if not text:
        return []
    if label in _HEADING_LABELS or (label == _PAGE_HEADER_LABEL and page_header_identifies(text)):
        return [Element(ElementKind.HEADING, text, _location(boxes))]
    if label in _CODE_LABELS:
        return [Element(ElementKind.CODE, text, _location(boxes))]
    if label in _TEXT_LABELS:
        return [Element(ElementKind.TEXT, text, _location(boxes))]
    return []


def parse_with_docling(
    path: Path,
    read_cells: ReadCells | None = None,
    ocr_pages: Mapping[int, Sequence[str]] | None = None,
) -> list[Element]:
    """read_cells verilirse OCR'lı sayfalardaki tablo hücreleri yeniden okunur.

    ocr_pages: OCR'lı sayfa → iki okumanın uyuşmadığı değerler.
    """
    pages = ocr_pages if read_cells is not None and ocr_pages is not None else {}
    document = _converter().convert(str(path)).document
    return [
        element
        for item, _level in document.iterate_items()
        for element in _item_elements(document, item, read_cells, pages)
    ]
