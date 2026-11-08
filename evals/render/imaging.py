"""Görsel üretimi: ekran görüntüsü, tarama ve telefon fotoğrafı."""

import io
from collections.abc import Sequence
from pathlib import Path
from random import Random

import pypdfium2
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from evals.content import TableBlock
from evals.render.pdf import FONT_DIR

_SCAN_SCALE = 1.7
_CELL_PADDING = 12
_ROW_HEIGHT = 34
_BLOCK_PAGE_INDEX = 1


def table_png(block: TableBlock) -> bytes:
    """Tabloyu seçilemeyen metinli bir ekran görüntüsü olarak çizer."""
    font = ImageFont.truetype(str(FONT_DIR / "DejaVuSans.ttf"), 18)
    rows = [block.headers, *block.rows]
    widths = [
        int(max(font.getlength(row[column]) for row in rows)) + 2 * _CELL_PADDING
        for column in range(len(block.headers))
    ]
    image = Image.new("RGB", (sum(widths) + 1, _ROW_HEIGHT * len(rows) + 1), "white")
    draw = ImageDraw.Draw(image)
    for row_index, row in enumerate(rows):
        left = 0
        top = row_index * _ROW_HEIGHT
        fill = "#d9d9d9" if row_index == 0 else "white"
        for width, cell in zip(widths, row, strict=True):
            draw.rectangle((left, top, left + width, top + _ROW_HEIGHT), fill=fill, outline="black")
            draw.text((left + _CELL_PADDING, top + 6), cell, fill="black", font=font)
            left += width
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _render_pages(pdf_path: Path) -> list[Image.Image]:
    document = pypdfium2.PdfDocument(pdf_path)
    try:
        return [page.render(scale=_SCAN_SCALE).to_pil().convert("RGB") for page in document]
    finally:
        document.close()


def _scanned(page: Image.Image, angle: float) -> Image.Image:
    rotated = page.convert("L").rotate(angle, fillcolor=255, resample=Image.Resampling.BICUBIC)
    return rotated.filter(ImageFilter.GaussianBlur(0.5)).convert("RGB")


def write_scan(pdf_path: Path, output: Path, rng: Random) -> None:
    """Metin katmanı olmayan, hafif eğri bir tarama PDF'i yazar."""
    pages: Sequence[Image.Image] = [
        _scanned(page, rng.uniform(-1.5, 1.5)) for page in _render_pages(pdf_path)
    ]
    pages[0].save(output, format="PDF", save_all=True, append_images=list(pages[1:]))


def write_photo(pdf_path: Path, output: Path, rng: Random) -> None:
    """Blok sayfasını eğik ve loş çekilmiş bir fotoğraf olarak yazar."""
    page = _render_pages(pdf_path)[_BLOCK_PAGE_INDEX]
    tilted = page.rotate(
        rng.uniform(-3.0, 3.0), fillcolor="#8a8a80", resample=Image.Resampling.BICUBIC
    )
    dim = ImageEnhance.Brightness(tilted.filter(ImageFilter.GaussianBlur(0.7))).enhance(0.86)
    dim.save(output, format="JPEG", quality=72)
