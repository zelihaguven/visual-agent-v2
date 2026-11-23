"""Dış araçlar: LibreOffice, Tesseract, sayfa okuyucusu ve Docling. İşçide çalışır."""

from functools import partial
from pathlib import Path
from typing import Any

import pypdfium2
import pypdfium2.raw as pdfium_c
from PIL import Image, ImageOps

from visual_agent.domain.document import Box, SourceLocation
from visual_agent.ingest.docling_parser import parse_with_docling
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.external import ExternalTools, locate_tools
from visual_agent.ingest.page_reader import (
    ReadPage,
    SecondReader,
    is_ocr_layer,
    read_embedded_images,
    read_scanned_pages,
    tesseract_reader,
)
from visual_agent.ingest.pipeline import IngestTools, PageInfo
from visual_agent.ingest.text_layer import PageKind, classify_page, quality_score

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
        boxes.append(
            Box(
                page=number,
                left=left,
                top=height - top,
                right=right,
                bottom=height - bottom,
                page_width=width,
                page_height=height,
            )
        )
    return tuple(boxes)


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
    """İkinci okuma ölçümdeki gibi Tesseract tur+eng; Tesseract yoksa belge bunu söyler.
    Okuyucu yoksa boş olmayan görüntü zaten okunamaz; Tesseract aranmaz."""
    if read_page is None:
        return lambda _: ""
    return tesseract_reader(external.require_tesseract("tur+eng"))


def _read_scanned(
    path: Path,
    pages: list[int],
    work: Path,
    image: Path | None,
    external: ExternalTools,
    read_page: ReadPage | None,
) -> list[Element]:
    second = _second_reader(external, read_page)
    return read_scanned_pages(path, pages, work, read_page, second, image)


def _read_images(
    path: Path, images: list[Box], work: Path, external: ExternalTools, read_page: ReadPage | None
) -> list[Element]:
    second = _second_reader(external, read_page)
    return read_embedded_images(path, images, work, read_page, second)


def default_tools(
    external: ExternalTools | None = None, read_page: ReadPage | None = None
) -> IngestTools:
    """Araç yolları verilmezse PATH'te aranır. Sayfa okuyucusu yoksa yalnız metinli olmayan
    sayfası (metin katmansız, zayıf ya da taranmış katmanlı) olan belge okuyucuyu bekler."""
    found = external if external is not None else locate_tools(None, None)
    return IngestTools(
        read_scanned_pages=partial(_read_scanned, external=found, read_page=read_page),
        office_to_pdf=partial(office_to_pdf, external=found),
        legacy_spreadsheet_to_xlsx=partial(legacy_spreadsheet_to_xlsx, external=found),
        image_to_pdf=image_to_pdf,
        inspect_pdf=inspect_pdf,
        parse_pdf=parse_pdf,
        recover_page_text=recover_page_text,
        read_embedded_images=partial(_read_images, external=found, read_page=read_page),
    )
