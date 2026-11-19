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
EMPTY_CELL = "(boş)"
"""Boş hücre işareti. Tire ya da çizgi gerçek belgelerde kendisi bir değer olabilir ("—", "-");
açık bir sözcük hücrenin boş olduğunu söyler (ürün sahibi kararı, 2026-11-17)."""


def with_empty_cells_marked(row: Sequence[str]) -> list[str]:
    """Başlıksız yazılan satırda aradaki boş hücre yerini korur: atılırsa etiket bir sonraki
    hücreyle yan yana kalır ve onun değeri sanılır ("Supplier Request Round | Material
    Description | …"). Satır sonundaki boş hücreler yazılmaz. Bütün tablo yolları kullanır."""
    filled = len(row)
    while filled and not row[filled - 1].strip():
        filled -= 1
    return [cell if cell.strip() else EMPTY_CELL for cell in row[:filled]]


def header_fits(header: Sequence[object], rows: Sequence[Sequence[object]]) -> bool:
    """Başlık satırı her veri satırıyla aynı sayıda hücre taşımalı. Bir hücre düşmüşse başlıklar
    bir sütun kayar ve değer yanlış sütunun adını alır; o zaman tablo başlıksız yazılır. İkinci
    okuma bunu yakalamaz, sayılar doğrudur. Bütün tablo yolları kullanır."""
    return all(len(row) == len(header) for row in rows)


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
    ocr_checked: bool = False
    """Belirsiz değerler okuyucu yolunda öğenin kendisinde belirlendi; sayfa düzeyi karşılaştırma
    uygulanmaz."""
    level: int | None = None
    """Başlığın düzeyi (1 en üst); biçim düzeyi bildirmiyorsa None."""
    context: str = ""
    """Bölüme eklenen öğeye özgü bağlam (tablo satırının bölüm etiketi ve tablo notu)."""


def labeled_row(labels: Sequence[str], values: Sequence[str]) -> str:
    """Tablo satırı "Başlık: değer | Başlık: değer"; boş hücre atlanır, başlıksız hücre yalındır.
    Hiç başlığı olmayan satırda aradaki boş hücre "(boş)" yazılır (etiket kayması)."""
    if not any(labels):
        return " | ".join(with_empty_cells_marked(values))
    return " | ".join(
        f"{label}: {value}" if label else value
        for label, value in zip(labels, values, strict=True)
        if value
    )
