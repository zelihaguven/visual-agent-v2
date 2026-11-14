"""Taranmış sayfadaki çizgili tablonun hücrelerini çizgilerden bulur.

OCR metin katmanında komşu sütunların yazısı birleşebiliyor, tablo yapısı çıkarıcı da sütunları
kaydırabiliyor: değer yanlış başlığın altına düşer. Çizgili tabloda hücre sınırı sayfanın
kendisinde yazılıdır; satır ve sütun çizgilerden alınır, her hücre ayrı okunur.

Çizgi: tablo genişliğinin (ya da yüksekliğinin) çoğunu kaplayan ince koyu şerit. Geniş şerit
gri zemindir (başlık satırı, öne çıkan sütun); kenarları sınırdır. Çizgi bulunamazsa None döner,
tablo eski yoldan okunur.
"""

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from PIL import Image

_INK = 235
"""Bundan koyu piksel boş değildir (çizgi, zemin, yazı)."""
_TEXT = 128
"""Bundan koyu piksel yazıdır."""
_LINE_COVERAGE = 0.6
_MAX_LINE_WIDTH = 8
_MERGE_DISTANCE = 12
_MIN_BAND = 20
_CELL_INSET = 5
_MIN_INK_PIXELS = 30
_MIN_LINES = 3
"""En az iki satır ve iki sütun: üç yatay ve üç dikey sınır."""
_LABEL_EMPTY_SHARE = 0.75
"""Hücrelerinin bu kadarı boş olan satır değer satırı değil, bölüm etiketi ya da nottur."""

Box = tuple[int, int, int, int]


@dataclass(frozen=True)
class GridCell:
    row: int
    column: int
    box: Box
    """Görüntüdeki piksel kutusu (sol, üst, sağ, alt)."""
    column_end: int = -1
    """Hücrenin bittiği sütun (dahil değil); satırda dikey çizgi yoksa komşularla birleşir."""


def _boundaries(coverage: np.ndarray) -> list[int]:
    """Çizgi ortaları; gri zemin şeridinin iki kenarı da sınırdır. Yakın sınırlar birleşir."""
    found: list[int] = []
    start: int | None = None
    for index, covered in enumerate([*(coverage > _LINE_COVERAGE), False]):
        if covered and start is None:
            start = index
        elif not covered and start is not None:
            width = index - start
            found += [(start + index - 1) // 2] if width <= _MAX_LINE_WIDTH else [start, index - 1]
            start = None
    merged: list[int] = []
    for position in found:
        if not merged or position - merged[-1] > _MERGE_DISTANCE:
            merged.append(position)
    return merged


def find_grid(image: Image.Image) -> tuple[list[int], list[int]] | None:
    """Yatay ve dikey sınırların piksel konumları; çizgili tablo değilse None."""
    pixels = np.asarray(image.convert("L"))
    ink = pixels < _INK
    rows = _boundaries(ink.mean(axis=1))
    if len(rows) < _MIN_LINES:
        return None
    columns = _boundaries(ink[rows[0] : rows[-1]].mean(axis=0))
    if len(columns) < _MIN_LINES:
        return None
    return rows, columns


def _has_divider(ink: np.ndarray, top: int, bottom: int, x: int) -> bool:
    """Satır bandında x'te dikey çizgi var mı: yoksa iki yan tek hücredir (birleşik hücre)."""
    band = ink[top + _CELL_INSET : bottom - _CELL_INSET, max(0, x - 2) : x + 3]
    return band.size > 0 and float(band.mean(axis=0).max()) > _LINE_COVERAGE


def grid_cells(image: Image.Image, rows: Sequence[int], columns: Sequence[int]) -> list[GridCell]:
    """Sınırlar arasındaki hücreler; çok ince bantlar (çift çizgi) atlanır. Satırda dikey çizgi
    olmayan yerde komşu hücreler birleşir (alt bilgi, bölüm etiketi, birleşik başlık)."""
    ink = np.asarray(image.convert("L")) < _INK
    row_bands = [(a, b) for a, b in zip(rows, rows[1:], strict=False) if b - a >= _MIN_BAND]
    column_bands = [
        (a, b) for a, b in zip(columns, columns[1:], strict=False) if b - a >= _MIN_BAND
    ]
    cells = []
    for row, (top, bottom) in enumerate(row_bands):
        start = 0
        for column in range(1, len(column_bands) + 1):
            last = column == len(column_bands)
            if not last and not _has_divider(ink, top, bottom, column_bands[column][0]):
                continue
            left, right = column_bands[start][0], column_bands[column - 1][1]
            box = (left + _CELL_INSET, top + _CELL_INSET, right - _CELL_INSET, bottom - _CELL_INSET)
            cells.append(GridCell(row, start, box, column))
            start = column
    return cells


def has_text(image: Image.Image, cell: GridCell) -> bool:
    crop = np.asarray(image.convert("L").crop(cell.box))
    return int((crop < _TEXT).sum()) > _MIN_INK_PIXELS


def label_rows(texts: dict[tuple[int, int], str], columns: int) -> set[int]:
    """Hücrelerinin çoğu boş satırlar: bölüm etiketi ("Tall") ya da tablo notu."""
    rows = {row for row, _ in texts}
    filled = {row: sum(1 for (r, _), text in texts.items() if r == row and text) for row in rows}
    return {
        row for row in rows if row > 0 and 0 < filled[row] <= columns * (1 - _LABEL_EMPTY_SHARE)
    }
