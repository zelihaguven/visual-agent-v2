"""Ayrıştırıcıların ürettiği ortak öğe biçimi."""

from dataclasses import dataclass
from enum import StrEnum

from visual_agent.domain.document import SourceLocation


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
    generated: str = ""
