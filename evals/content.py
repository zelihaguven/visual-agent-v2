"""Belgelerin biçimden bağımsız içeriği ve kaynak konumu hesabı."""

from collections.abc import Sequence
from dataclasses import dataclass, field

from evals.gold import Carrier, GoldDocument, GoldQuestion, GoldSource

EXCEL_FIRST_DATA_ROW = 4
PDF_FIRST_BLOCK_PAGE = 2


@dataclass(frozen=True)
class TextBlock:
    title: str
    text: str


@dataclass(frozen=True)
class TableBlock:
    title: str
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    group_header: str | None = None


@dataclass(frozen=True)
class CodeBlock:
    title: str
    code: str


Block = TextBlock | TableBlock | CodeBlock


@dataclass(frozen=True)
class DocumentContent:
    title: str
    blocks: tuple[Block, ...]

    def full_text(self) -> str:
        parts = [self.title]
        for block in self.blocks:
            parts.append(block.title)
            if isinstance(block, TextBlock):
                parts.append(block.text)
            elif isinstance(block, CodeBlock):
                parts.append(block.code)
            else:
                parts.extend(block.headers)
                parts.extend(cell for row in block.rows for cell in row)
        return "\n".join(parts)


@dataclass(frozen=True)
class ScenarioDocument:
    gold: GoldDocument
    content: DocumentContent


@dataclass(frozen=True)
class Scenario:
    documents: Sequence[ScenarioDocument]
    questions: Sequence[GoldQuestion] = field(default_factory=tuple)


def source_for(document: ScenarioDocument, block_index: int, row_index: int = 0) -> GoldSource:
    """Bir bloğun, üretilen dosyadaki kesin konumu."""
    doc_id = document.gold.doc_id
    carrier = document.gold.carrier
    if carrier in (Carrier.PDF, Carrier.SCAN):
        return GoldSource(doc_id=doc_id, page=block_index + PDF_FIRST_BLOCK_PAGE)
    if carrier is Carrier.PHOTO:
        return GoldSource(doc_id=doc_id, page=1)
    if carrier is Carrier.XLSX:
        sheet = document.content.blocks[block_index].title
        return GoldSource(doc_id=doc_id, sheet=sheet, row=row_index + EXCEL_FIRST_DATA_ROW)
    return GoldSource(doc_id=doc_id)
