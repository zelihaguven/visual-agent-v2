"""Ayrıştırıcıların ürettiği ortak öğe biçimi."""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from visual_agent.domain.document import SourceLocation

SECTION_SEPARATOR = " · "
"""Bölüm yolundaki başlıkların ayırıcısı (Excel sayfası · başlık satırı, başlık · alt başlık)."""
NUMERIC_TEXT_RE = re.compile(r"^[\d.,\s%±/-]+$")
"""Yalnız sayıdan oluşan hücre: tablo başlığı sayılmaz."""


class ElementKind(StrEnum):
    HEADING = "heading"
    TEXT = "text"
    TABLE_ROW = "table_row"
    CODE = "code"
    FIGURE = "figure"


@dataclass(frozen=True)
class Element:
    kind: ElementKind
    text: str
    location: SourceLocation
    from_ocr: bool = False
    ocr_uncertain: tuple[str, ...] = ()
    level: int | None = None
    """Başlığın düzeyi (1 en üst); biçim düzeyi bildirmiyorsa None."""


def labeled_row(labels: Sequence[str], values: Sequence[str]) -> str:
    """Tablo satırı "Başlık: değer | Başlık: değer"; boş hücre atlanır, başlıksız hücre yalındır."""
    return " | ".join(
        f"{label}: {value}" if label else value
        for label, value in zip(labels, values, strict=True)
        if value
    )
