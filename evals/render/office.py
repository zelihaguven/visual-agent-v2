"""Word, Excel ve düz SQL dosyaları."""

import io
from pathlib import Path

import docx
from docx.shared import Inches
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from evals.content import (
    EXCEL_FIRST_DATA_ROW,
    CodeBlock,
    DocumentContent,
    TableBlock,
    TextBlock,
)
from evals.render.imaging import table_png

_EXCEL_NOTES_SHEET = "Notlar"
_EXCEL_TITLE_ROW = 1
_EXCEL_GROUP_ROW = 2
_EXCEL_HEADER_ROW = 3


def _add_word_table(document: docx.document.Document, block: TableBlock) -> None:
    table = document.add_table(rows=1 + len(block.rows), cols=len(block.headers))
    table.style = "Table Grid"
    for row_index, row in enumerate((block.headers, *block.rows)):
        for column_index, cell in enumerate(row):
            table.cell(row_index, column_index).text = cell


def render_docx(content: DocumentContent, path: Path, tables_as_images: bool = False) -> None:
    document = docx.Document()
    document.add_heading(content.title, level=0)
    for block in content.blocks:
        document.add_heading(block.title, level=1)
        if isinstance(block, TextBlock):
            document.add_paragraph(block.text)
        elif isinstance(block, CodeBlock):
            document.add_paragraph(block.code)
        elif tables_as_images:
            document.add_picture(io.BytesIO(table_png(block)), width=Inches(5.5))
        else:
            _add_word_table(document, block)
    document.save(str(path))


def _fill_sheet(sheet: Worksheet, title: str, block: TableBlock) -> None:
    last_column = len(block.headers)
    sheet.cell(_EXCEL_TITLE_ROW, 1, title)
    sheet.cell(_EXCEL_GROUP_ROW, 2, block.group_header or block.title)
    if last_column > 2:
        sheet.merge_cells(
            start_row=_EXCEL_GROUP_ROW,
            start_column=2,
            end_row=_EXCEL_GROUP_ROW,
            end_column=last_column if block.group_width is None else 1 + block.group_width,
        )
    for column, header in enumerate(block.headers, start=1):
        sheet.cell(_EXCEL_HEADER_ROW, column, header)
    for row_offset, row in enumerate(block.rows):
        for column, value in enumerate(row, start=1):
            sheet.cell(EXCEL_FIRST_DATA_ROW + row_offset, column, value)


def render_xlsx(content: DocumentContent, path: Path) -> None:
    workbook = Workbook()
    workbook.remove(workbook.active)
    notes = [block for block in content.blocks if not isinstance(block, TableBlock)]
    for block in content.blocks:
        if isinstance(block, TableBlock):
            _fill_sheet(workbook.create_sheet(block.title), content.title, block)
    if notes:
        sheet = workbook.create_sheet(_EXCEL_NOTES_SHEET)
        for row, block in enumerate(notes, start=1):
            sheet.cell(row, 1, block.title)
    workbook.save(path)


def render_sql_text(content: DocumentContent, path: Path) -> None:
    lines = [f"-- {content.title}"]
    for block in content.blocks:
        if isinstance(block, CodeBlock):
            lines += [f"-- {block.title}", block.code]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
