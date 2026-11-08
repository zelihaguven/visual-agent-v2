"""Kaynak sayfayı vurgulu görsel olarak çizer."""

import io
from collections.abc import Sequence
from pathlib import Path

import pypdfium2
from PIL import Image, ImageDraw

from visual_agent.domain.document import Box

_DPI = 130
_POINTS_PER_INCH = 72
_FILL = (255, 214, 0, 80)
_OUTLINE = (214, 158, 0, 255)
_OUTLINE_WIDTH = 3


def render_highlighted_page(pdf_path: Path, page: int, boxes: Sequence[Box]) -> bytes:
    scale = _DPI / _POINTS_PER_INCH
    document = pypdfium2.PdfDocument(pdf_path)
    try:
        image: Image.Image = document[page - 1].render(scale=scale).to_pil().convert("RGBA")
    finally:
        document.close()
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for box in boxes:
        if box.page == page:
            draw.rectangle(
                (box.left * scale, box.top * scale, box.right * scale, box.bottom * scale),
                fill=_FILL,
                outline=_OUTLINE,
                width=_OUTLINE_WIDTH,
            )
    output = io.BytesIO()
    Image.alpha_composite(image, overlay).convert("RGB").save(output, format="PNG")
    return output.getvalue()
