"""Excel: sayfa, başlık ve satır yapısını koruyarak okur."""

import re
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from visual_agent.domain.document import SourceLocation
from visual_agent.ingest.elements import Element, ElementKind

_NUMERIC_TEXT_RE = re.compile(r"^[\d.,\s%±/-]+$")
_HEADER_SEARCH_ROWS = 15
_SECTION_SEPARATOR = " · "

Grid = list[list[str]]


def _cell_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime | date):
        return value.isoformat()
    return str(value).strip()


def _read_grid(sheet: Worksheet) -> Grid:
    """Birleşik hücrelerin değerini kapladıkları bütün hücrelere yayar."""
    grid = [[_cell_text(cell) for cell in row] for row in sheet.iter_rows(values_only=True)]
    for merged in sheet.merged_cells.ranges:
        value = _cell_text(sheet.cell(merged.min_row, merged.min_col).value)
        for row in range(merged.min_row - 1, merged.max_row):
            for column in range(merged.min_col - 1, merged.max_col):
                grid[row][column] = value
    return grid


def _label_score(row: list[str]) -> int:
    return len({cell for cell in row if cell and not _NUMERIC_TEXT_RE.match(cell)})


def _find_header(grid: Grid) -> int:
    scores = [_label_score(row) for row in grid[:_HEADER_SEARCH_ROWS]]
    return scores.index(max(scores))


def _labels(grid: Grid, header_index: int) -> list[str]:
    header = grid[header_index]
    above = grid[header_index - 1] if header_index > 0 else [""] * len(header)
    is_group = 0 < _label_score(above) < _label_score(header)
    return [
        f"{above[column]} {label}".strip() if is_group and label else label
        for column, label in enumerate(header)
    ]


def _title_rows(grid: Grid, header_index: int) -> list[str]:
    header = grid[header_index]
    above_is_group = header_index > 0 and 0 < _label_score(grid[header_index - 1]) < _label_score(
        header
    )
    last_title = header_index - 1 if above_is_group else header_index
    return [cell for row in grid[:last_title] for cell in row if cell]


def _row_text(labels: list[str], row: list[str]) -> str:
    parts = [
        f"{label}: {value}" if label else value
        for label, value in zip(labels, row, strict=True)
        if value
    ]
    return " | ".join(parts)


def _parse_sheet(sheet: Worksheet) -> list[Element]:
    grid = _read_grid(sheet)
    if not any(any(row) for row in grid):
        return []
    header_index = _find_header(grid)
    labels = _labels(grid, header_index)
    section = _SECTION_SEPARATOR.join([sheet.title, *_title_rows(grid, header_index)])
    elements = [Element(ElementKind.HEADING, section, SourceLocation(sheet=sheet.title))]
    for offset, row in enumerate(grid[header_index + 1 :], start=header_index + 2):
        text = _row_text(labels, row)
        if text:
            location = SourceLocation(sheet=sheet.title, row=offset)
            elements.append(Element(ElementKind.TABLE_ROW, text, location))
    return elements


def parse_workbook(path: Path) -> list[Element]:
    workbook = load_workbook(path, data_only=True)
    try:
        return [element for sheet in workbook.worksheets for element in _parse_sheet(sheet)]
    finally:
        workbook.close()
