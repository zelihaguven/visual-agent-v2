"""Dış araçlar: LibreOffice, Tesseract, RapidOCR ve Docling. İşçide çalışır (yerel ya da imaj)."""

import logging
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterable
from functools import partial
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
from visual_agent.ingest.external import ExternalTools, locate_tools, tesseract_language
from visual_agent.ingest.images import (
    OcrSegment,
    group_lines,
    image_skip_reason,
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


def _soffice(path: Path, work: Path, target: str, executable: str) -> Path:
    profile = Path(tempfile.mkdtemp(prefix="lo-profile-", dir=work))
    command = [
        executable,
        f"-env:UserInstallation={profile.resolve().as_uri()}",
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


def office_to_pdf(path: Path, work: Path, external: ExternalTools) -> Path:
    return _soffice(path, work, "pdf", external.require_soffice())


def legacy_spreadsheet_to_xlsx(path: Path, work: Path, external: ExternalTools) -> Path:
    return _soffice(path, work, "xlsx", external.require_soffice())


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


def _run_ocrmypdf(
    source: Path, target: Path, flag: str, language: str, pages: list[int], env: dict[str, str]
) -> None:
    deskew = ["--deskew"] if flag == "--skip-text" else []
    command = [
        sys.executable,
        "-m",
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
    subprocess.run(command, check=True, capture_output=True, timeout=_OCR_TIMEOUT_SECONDS, env=env)


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


def run_ocr(
    path: Path, pages: list[PageInfo], language: str, work: Path, external: ExternalTools
) -> OcrOutcome:
    groups: dict[str, list[PageInfo]] = {}
    for info in pages:
        if info.kind in _OCR_FLAGS:
            groups.setdefault(_OCR_FLAGS[info.kind], []).append(info)
    if not groups:
        return OcrOutcome(pdf_path=path, ocr_pages={})
    ocr_language = tesseract_language(language)
    external.require_tesseract(ocr_language)
    environment = external.subprocess_environment()
    engine = _rapid_engine()
    result_path = work / f"{path.stem}.ocr.pdf"
    chosen: dict[int, Path] = {}
    uncertain: dict[int, tuple[str, ...]] = {}
    image_only: list[int] = []
    for index, (flag, infos) in enumerate(groups.items()):
        target = work / f"{path.stem}.group{index}.pdf"
        _run_ocrmypdf(path, target, flag, ocr_language, [info.page for info in infos], environment)
        for info in infos:
            choice, tokens = _decide_page(engine, path, target, info)
            if choice is LayerChoice.NEW:
                chosen[info.page] = target
                uncertain[info.page] = tokens
            elif choice is LayerChoice.IMAGE_ONLY:
                image_only.append(info.page)
    _merge_pages(path, chosen, result_path)
    return OcrOutcome(
        pdf_path=result_path, ocr_pages=uncertain, image_only_pages=tuple(sorted(image_only))
    )


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


def _skip_reason(box: Box) -> str | None:
    return image_skip_reason(box, _MIN_IMAGE_AREA_RATIO, _MIN_IMAGE_SIDE_POINTS)


def _is_meaningful_image(box: Box) -> bool:
    return _skip_reason(box) is None


def skipped_image_warnings(pages: list[PageInfo]) -> list[str]:
    """Boyut eşiğine takıldığı için okunmayan her görsel için bir uyarı."""
    return [
        f"Sayfa {info.page}: görsel okunmadı ({reason})."
        for info in pages
        if info.kind is PageKind.TEXT
        for box in info.image_boxes
        if (reason := _skip_reason(box)) is not None
    ]


def _tesseract_text(image: Image.Image, language: str, work: str, executable: str) -> str:
    """Tablolarda blok modu son sütunları kaçırır; seyrek mod da okunup birleştirilir."""
    source = Path(work) / "crop.png"
    image.save(source)
    readings = [
        subprocess.run(
            [executable, str(source), "stdout", "-l", language, "--psm", mode],
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


def _read_image(
    engine: Any, page_image: Image.Image, box: Box, language: str, tesseract: str
) -> list[Element]:
    crop = _crop(page_image, box)
    raw = _rapid_segments(engine, crop)
    if not raw:
        return []
    elements = lines_to_elements(group_lines(_segments_in_page_points(raw, box)), box)
    with tempfile.TemporaryDirectory() as work:
        second = _tesseract_text(crop, language, work, tesseract)
    first = " ".join(text for text, _ in raw)
    tokens = unconfirmed_tokens(first, second)
    return [with_uncertain_tokens(element, tokens) for element in elements]


def read_embedded_images(
    path: Path, pages: list[PageInfo], language: str, external: ExternalTools
) -> list[Element]:
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
    ocr_language = tesseract_language(language)
    tesseract = external.require_tesseract(ocr_language)
    engine = _rapid_engine()
    document = pypdfium2.PdfDocument(path)
    try:
        elements: list[Element] = []
        for page_number, box in targets:
            image = _render_page(document, page_number)
            elements += _read_image(engine, image, box, ocr_language, tesseract)
        return elements
    finally:
        document.close()


def recover_page_text(path: Path, page: int) -> list[Element]:
    text = _layer_text(path, page).strip()
    if not text:
        return []
    return [Element(ElementKind.TEXT, " ".join(text.split()), SourceLocation(page=page))]


def default_tools(external: ExternalTools | None = None) -> IngestTools:
    """Araç yolları verilmezse PATH'te aranır."""
    found = external if external is not None else locate_tools(None, None)
    return IngestTools(
        office_to_pdf=partial(office_to_pdf, external=found),
        legacy_spreadsheet_to_xlsx=partial(legacy_spreadsheet_to_xlsx, external=found),
        image_to_pdf=image_to_pdf,
        inspect_pdf=inspect_pdf,
        run_ocr=partial(run_ocr, external=found),
        parse_pdf=parse_pdf,
        read_embedded_images=partial(read_embedded_images, external=found),
        recover_page_text=recover_page_text,
        skipped_image_warnings=skipped_image_warnings,
    )
