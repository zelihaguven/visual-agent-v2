"""Dış araçlar: LibreOffice, Tesseract, RapidOCR ve Docling. Yalnız işçi imajında çalışır."""

import logging
import shutil
import subprocess
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pikepdf
import pypdfium2
import pypdfium2.raw as pdfium_c
from PIL import Image, ImageOps

from visual_agent.domain.document import Box, SourceLocation
from visual_agent.ingest.docling_parser import parse_with_docling
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.images import (
    OcrSegment,
    group_lines,
    lines_to_elements,
    with_uncertain_tokens,
)
from visual_agent.ingest.pipeline import IngestTools, OcrOutcome, PageInfo
from visual_agent.ingest.text_layer import (
    PageKind,
    classify_page,
    junk_score,
    quality_score,
)
from visual_agent.ingest.two_reading import (
    LayerChoice,
    choose_layer,
    page_ranges,
    unconfirmed_tokens,
)

logger = logging.getLogger(__name__)

_CONVERT_TIMEOUT_SECONDS = 180
_OCR_TIMEOUT_SECONDS = 600
_TESSERACT_LANGUAGES = {"tr": "tur", "en": "eng", "fr": "fra", "es": "spa", "de": "deu"}
_OCR_FLAGS = {
    PageKind.NONE: "--skip-text",
    PageKind.SCANNED: "--redo-ocr",
    PageKind.WEAK: "--force-ocr",
}
_RENDER_DPI = 300
_POINTS_PER_INCH = 72
_MIN_IMAGE_AREA_RATIO = 0.02
_MIN_IMAGE_SIDE_POINTS = 50.0
_IMAGE_PAGE_DPI = 150
_TESSERACT_PAGE_MODES = ("6", "11")


def _soffice(path: Path, work: Path, target: str) -> Path:
    profile = tempfile.mkdtemp(prefix="lo-profile-", dir=work)
    command = [
        "soffice",
        f"-env:UserInstallation=file://{profile}",
        "--headless",
        "--convert-to",
        target,
        "--outdir",
        str(work),
        str(path),
    ]
    subprocess.run(command, check=True, capture_output=True, timeout=_CONVERT_TIMEOUT_SECONDS)
    shutil.rmtree(profile, ignore_errors=True)
    return work / f"{path.stem}.{target}"


def office_to_pdf(path: Path, work: Path) -> Path:
    return _soffice(path, work, "pdf")


def legacy_spreadsheet_to_xlsx(path: Path, work: Path) -> Path:
    return _soffice(path, work, "xlsx")


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
            result.append(PageInfo(page=number, kind=kind, chars=chars, image_boxes=boxes))
        return result
    finally:
        document.close()


def _run_ocrmypdf(source: Path, target: Path, flag: str, language: str, pages: list[int]) -> None:
    deskew = ["--deskew"] if flag == "--skip-text" else []
    command = [
        "ocrmypdf",
        "-l",
        language,
        flag,
        *deskew,
        "--pages",
        page_ranges(pages),
        "--rotate-pages",
        "--rasterizer",
        "pypdfium",
        "--output-type",
        "pdf",
        "--pdfa-backend",
        "internal",
        "-q",
        str(source),
        str(target),
    ]
    subprocess.run(command, check=True, capture_output=True, timeout=_OCR_TIMEOUT_SECONDS)


def _rapid_engine() -> Any:
    from rapidocr import RapidOCR

    return RapidOCR()


def _rapid_segments(engine: Any, image: Image.Image) -> list[tuple[str, tuple[float, ...]]]:
    output = engine(np.asarray(image.convert("RGB")))
    if output.txts is None:
        return []
    return [
        (
            str(text),
            (
                float(min(point[0] for point in box)),
                float(min(point[1] for point in box)),
                float(max(point[0] for point in box)),
                float(max(point[1] for point in box)),
            ),
        )
        for text, box in zip(output.txts, output.boxes, strict=True)
    ]


def _render_page(document: Any, page_number: int) -> Image.Image:
    bitmap = document[page_number - 1].render(scale=_RENDER_DPI / _POINTS_PER_INCH)
    image: Image.Image = bitmap.to_pil().convert("RGB")
    return image


def _layer_text(path: Path, page_number: int) -> str:
    document = pypdfium2.PdfDocument(path)
    try:
        return _page_text(document[page_number - 1])
    finally:
        document.close()


def _rapid_page_text(engine: Any, path: Path, page_number: int) -> str:
    document = pypdfium2.PdfDocument(path)
    try:
        return " ".join(
            text for text, _ in _rapid_segments(engine, _render_page(document, page_number))
        )
    finally:
        document.close()


def _decide_page(
    engine: Any, source: Path, output: Path, info: PageInfo
) -> tuple[LayerChoice, tuple[str, ...]]:
    old = _layer_text(source, info.page)
    new = _layer_text(output, info.page)
    choice = choose_layer(info.kind, junk_score(old), junk_score(new))
    if choice is not LayerChoice.NEW:
        return choice, ()
    second = _rapid_page_text(engine, source, info.page) if info.kind is PageKind.NONE else old
    return choice, tuple(unconfirmed_tokens(new, second))


def run_ocr(path: Path, pages: list[PageInfo], language: str, work: Path) -> OcrOutcome:
    groups: dict[str, list[PageInfo]] = {}
    for info in pages:
        if info.kind in _OCR_FLAGS:
            groups.setdefault(_OCR_FLAGS[info.kind], []).append(info)
    if not groups:
        return OcrOutcome(pdf_path=path, ocr_pages={})
    tesseract_language = _TESSERACT_LANGUAGES.get(language, "eng")
    engine = _rapid_engine()
    result_path = work / f"{path.stem}.ocr.pdf"
    chosen: dict[int, Path] = {}
    uncertain: dict[int, tuple[str, ...]] = {}
    for index, (flag, infos) in enumerate(groups.items()):
        target = work / f"{path.stem}.group{index}.pdf"
        _run_ocrmypdf(path, target, flag, tesseract_language, [info.page for info in infos])
        for info in infos:
            choice, tokens = _decide_page(engine, path, target, info)
            if choice is LayerChoice.NEW:
                chosen[info.page] = target
                uncertain[info.page] = tokens
    _merge_pages(path, chosen, result_path)
    return OcrOutcome(pdf_path=result_path, ocr_pages=uncertain)


def _merge_pages(source: Path, chosen: dict[int, Path], target: Path) -> None:
    with pikepdf.open(source) as result:
        opened = {path: pikepdf.open(path) for path in set(chosen.values())}
        try:
            for page_number, path in chosen.items():
                result.pages[page_number - 1] = opened[path].pages[page_number - 1]
            result.save(target)
        finally:
            for document in opened.values():
                document.close()


def parse_pdf(path: Path) -> list[Element]:
    return parse_with_docling(path)


def _is_meaningful_image(box: Box) -> bool:
    width, height = box.right - box.left, box.bottom - box.top
    area_ratio = width * height / (box.page_width * box.page_height or 1.0)
    return area_ratio >= _MIN_IMAGE_AREA_RATIO and min(width, height) >= _MIN_IMAGE_SIDE_POINTS


def _tesseract_text(image: Image.Image, language: str, work: str) -> str:
    """Tablolarda blok modu son sütunları kaçırır; seyrek mod da okunup birleştirilir."""
    source = Path(work) / "crop.png"
    image.save(source)
    readings = [
        subprocess.run(
            ["tesseract", str(source), "stdout", "-l", language, "--psm", mode],
            check=True,
            capture_output=True,
            timeout=_OCR_TIMEOUT_SECONDS,
        ).stdout.decode("utf-8", errors="replace")
        for mode in _TESSERACT_PAGE_MODES
    ]
    return " ".join(readings)


def _crop(page_image: Image.Image, box: Box) -> Image.Image:
    scale = _RENDER_DPI / _POINTS_PER_INCH
    return page_image.crop(
        (
            int(box.left * scale),
            int(box.top * scale),
            int(box.right * scale),
            int(box.bottom * scale),
        )
    )


def _segments_in_page_points(
    raw: Iterable[tuple[str, tuple[float, ...]]], box: Box
) -> list[OcrSegment]:
    scale = _POINTS_PER_INCH / _RENDER_DPI
    return [
        OcrSegment(
            text=text,
            left=box.left + left * scale,
            top=box.top + top * scale,
            right=box.left + right * scale,
            bottom=box.top + bottom * scale,
        )
        for text, (left, top, right, bottom) in raw
    ]


def _read_image(engine: Any, page_image: Image.Image, box: Box, language: str) -> list[Element]:
    crop = _crop(page_image, box)
    raw = _rapid_segments(engine, crop)
    if not raw:
        return []
    elements = lines_to_elements(group_lines(_segments_in_page_points(raw, box)), box)
    with tempfile.TemporaryDirectory() as work:
        second = _tesseract_text(crop, language, work)
    first = " ".join(text for text, _ in raw)
    tokens = unconfirmed_tokens(first, second)
    return [with_uncertain_tokens(element, tokens) for element in elements]


def read_embedded_images(path: Path, pages: list[PageInfo], language: str) -> list[Element]:
    """Metinli sayfalardaki gömülü görselleri okur; tamamı taranmış sayfalar OCR yolundan geçer."""
    targets = [
        (info.page, box)
        for info in pages
        if info.kind is PageKind.TEXT
        for box in info.image_boxes
        if _is_meaningful_image(box)
    ]
    if not targets:
        return []
    tesseract_language = _TESSERACT_LANGUAGES.get(language, "eng")
    engine = _rapid_engine()
    document = pypdfium2.PdfDocument(path)
    try:
        elements: list[Element] = []
        for page_number, box in targets:
            image = _render_page(document, page_number)
            elements += _read_image(engine, image, box, tesseract_language)
        return elements
    finally:
        document.close()


def recover_page_text(path: Path, page: int) -> list[Element]:
    text = _layer_text(path, page).strip()
    if not text:
        return []
    return [Element(ElementKind.TEXT, " ".join(text.split()), SourceLocation(page=page))]


def default_tools() -> IngestTools:
    return IngestTools(
        office_to_pdf=office_to_pdf,
        legacy_spreadsheet_to_xlsx=legacy_spreadsheet_to_xlsx,
        image_to_pdf=image_to_pdf,
        inspect_pdf=inspect_pdf,
        run_ocr=run_ocr,
        parse_pdf=parse_pdf,
        read_embedded_images=read_embedded_images,
        recover_page_text=recover_page_text,
    )
