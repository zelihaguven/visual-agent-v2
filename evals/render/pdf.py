"""Metin katmanlı PDF: kapak sayfası ve her blok için tek sayfa."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from evals.content import Block, CodeBlock, DocumentContent, TableBlock, TextBlock

FONT_DIR = Path(__file__).parent.parent / "assets" / "fonts"
_FONTS = {
    "DejaVu": "DejaVuSans.ttf",
    "DejaVu-Bold": "DejaVuSans-Bold.ttf",
    "DejaVu-Mono": "DejaVuSansMono.ttf",
}
_BODY = ParagraphStyle("body", fontName="DejaVu", fontSize=10, leading=14)
_HEADING = ParagraphStyle("heading", fontName="DejaVu-Bold", fontSize=13, leading=18)
_TITLE = ParagraphStyle("title", fontName="DejaVu-Bold", fontSize=22, leading=28)
_CODE = ParagraphStyle("code", fontName="DejaVu-Mono", fontSize=8, leading=12)
_TABLE_STYLE = TableStyle(
    [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]
)


def _register_fonts() -> None:
    registered = set(pdfmetrics.getRegisteredFontNames())
    for name, filename in _FONTS.items():
        if name not in registered:
            pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))


def _paragraph(text: str, style: ParagraphStyle = _BODY) -> Paragraph:
    return Paragraph(escape(text), style)


def _block_flowables(block: Block, document_title: str) -> list[Flowable]:
    heading: list[Flowable] = [
        _paragraph(document_title),
        Spacer(1, 6),
        _paragraph(block.title, _HEADING),
        Spacer(1, 10),
    ]
    if isinstance(block, TextBlock):
        return [*heading, _paragraph(block.text)]
    if isinstance(block, CodeBlock):
        return [*heading, Preformatted(block.code, _CODE)]
    return [*heading, _table(block)]


def _table(block: TableBlock) -> Table:
    rows = [block.headers, *block.rows]
    return Table([[_paragraph(cell) for cell in row] for row in rows], style=_TABLE_STYLE)


def render_pdf(content: DocumentContent, path: Path) -> None:
    _register_fonts()
    story: list[Flowable] = [
        _paragraph(content.title, _TITLE),
        Spacer(1, 16),
        _paragraph("Bu belge test amacıyla üretilmiş kurgusal içerik taşır."),
    ]
    for block in content.blocks:
        story += [PageBreak(), *_block_flowables(block, content.title)]
    SimpleDocTemplate(str(path), pagesize=A4, invariant=1, title=content.title).build(story)
