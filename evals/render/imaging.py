"""Görsel üretimi: ekran görüntüsü, tarama ve telefon fotoğrafı."""

import io
import time
from collections.abc import Sequence
from pathlib import Path
from random import Random

import pypdfium2
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

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


_SCAN_DPI = 300
_FIXED_DATE = time.strptime("2026-11-16", "%Y-%m-%d")
_PHOTO_DPI = 220
_POINTS_PER_INCH = 72


def _page_at(pdf_path: Path, index: int, dpi: int) -> Image.Image:
    document = pypdfium2.PdfDocument(pdf_path)
    try:
        image: Image.Image = document[index].render(scale=dpi / _POINTS_PER_INCH).to_pil()
        return image.convert("L")
    finally:
        document.close()


def _noisy(image: Image.Image, sigma: float, rng: Random) -> Image.Image:
    """Tohumdan türetilen Gauss gürültüsü (Pillow'un gürültüsü tohuma bağlı değil)."""
    import numpy as np

    noise = np.random.default_rng(rng.randrange(2**32)).normal(
        0, sigma, (image.height, image.width)
    )
    pixels = np.asarray(image, dtype=np.float32) + noise
    return Image.fromarray(np.clip(pixels, 0, 255).astype("uint8"), mode="L")


def scan_page(page: Image.Image, rng: Random) -> Image.Image:
    """300 dpi masaüstü tarayıcı: hafif eğik, biraz bulanık, gürültülü, kontrastı oynak."""
    rotated = page.rotate(rng.uniform(-1.5, 1.5), fillcolor=255, resample=Image.Resampling.BICUBIC)
    blurred = rotated.filter(ImageFilter.GaussianBlur(rng.uniform(0.4, 0.8)))
    return ImageEnhance.Contrast(_noisy(blurred, 6, rng)).enhance(rng.uniform(0.85, 1.05))


def _perspective(size: tuple[int, int], corners: Sequence[tuple[float, float]]) -> list[float]:
    """Çıktı köşelerini (sol-üst, sağ-üst, sağ-alt, sol-alt) girdi köşelerine eşleyen katsayılar."""
    import numpy as np

    width, height = size
    target = [(0, 0), (width, 0), (width, height), (0, height)]
    rows, values = [], []
    for (x, y), (u, v) in zip(target, corners, strict=True):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        values += [u, v]
    return [float(c) for c in np.linalg.solve(np.array(rows), np.array(values))]


def _light(size: tuple[int, int], rng: Random) -> Image.Image:
    """Bir yandan gelen ışık: rastgele yönde düzgün geçiş, en karanlık yer %67 parlaklık."""
    import math

    import numpy as np

    width, height = size
    angle = rng.uniform(0, 2 * math.pi)
    ys, xs = np.mgrid[0:height, 0:width]
    along = xs / width * math.cos(angle) + ys / height * math.sin(angle)
    span = (along - along.min()) / (along.max() - along.min())
    return Image.fromarray((170 + span * 85).astype("uint8"), mode="L")


def photograph_page(page: Image.Image, rng: Random) -> Image.Image:
    """Telefonla çekilmiş sayfa: masa zemini, perspektif ve dönme (tek dönüşüm), eşit olmayan
    ışık, bulanıklık, gürültü. Küçük yazı iki kez yeniden örneklenmesin diye dönüşüm tektir."""
    width, height = page.size
    margin = int(0.06 * width)
    desk = Image.new("L", (width + 2 * margin, height + 2 * margin), rng.randint(95, 140))
    desk.paste(page, (margin, margin))
    w, h = desk.size
    jitter = 0.03
    corners = [
        (rng.uniform(-jitter, jitter) * w, rng.uniform(-jitter, jitter) * h),
        (w + rng.uniform(-jitter, jitter) * w, rng.uniform(-jitter, jitter) * h),
        (w + rng.uniform(-jitter, jitter) * w, h + rng.uniform(-jitter, jitter) * h),
        (rng.uniform(-jitter, jitter) * w, h + rng.uniform(-jitter, jitter) * h),
    ]
    shot = desk.transform(
        desk.size,
        Image.Transform.PERSPECTIVE,
        _perspective(desk.size, corners),
        resample=Image.Resampling.BICUBIC,
        fillcolor=rng.randint(60, 90),
    )
    lit = ImageChops.multiply(shot, _light(shot.size, rng))
    blurred = lit.filter(ImageFilter.GaussianBlur(rng.uniform(0.6, 1.0)))
    return _noisy(blurred, 8, rng)


def degrade_set(set_dir: Path, output: Path, seed: int, photos_per_type: int = 2) -> list[str]:
    """Kilitli setin her belgesini 300 dpi taranmış PDF'e (`synN_tarama.pdf`), her sayfa
    türünden belirli sayıda sayfayı telefon fotoğrafına (`synN_sM_foto.jpg`) çevirir.
    Yazılan dosyaların adlarını döner."""
    import json

    rng = Random(seed)
    output.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    by_type: dict[str, list[tuple[Path, int]]] = {}
    for pdf in sorted(set_dir.glob("syn*.pdf")):
        truth = json.loads(pdf.with_suffix(".json").read_text(encoding="utf-8"))
        pages = [scan_page(_page_at(pdf, i, _SCAN_DPI), rng) for i in range(len(truth["pages"]))]
        target = output / f"{pdf.stem}_tarama.pdf"
        pages[0].save(
            target,
            format="PDF",
            save_all=True,
            append_images=pages[1:],
            resolution=_SCAN_DPI,
            creationDate=_FIXED_DATE,  # tarih sabit: aynı tohum aynı dosya
            modDate=_FIXED_DATE,
        )
        written.append(target.name)
        for page in truth["pages"]:
            by_type.setdefault(page["page_type"], []).append((pdf, int(page["page"])))
    for page_type in sorted(by_type):
        for pdf, number in rng.sample(by_type[page_type], k=photos_per_type):
            target = output / f"{pdf.stem}_s{number}_foto.jpg"
            photo = photograph_page(_page_at(pdf, number - 1, _PHOTO_DPI), rng)
            photo.save(target, format="JPEG", quality=rng.randint(70, 85))
            written.append(target.name)
    return written
