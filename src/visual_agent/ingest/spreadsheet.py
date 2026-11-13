"""Excel: sayfa, başlık ve satır yapısını koruyarak okur; sayılar gösterildiği biçimde yazılır."""

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from visual_agent.domain.document import SourceLocation
from visual_agent.ingest.elements import (
    NUMERIC_TEXT_RE,
    SECTION_SEPARATOR,
    Element,
    ElementKind,
    labeled_row,
)

_HEADER_SEARCH_ROWS = 15
_DECIMAL = ","
_THOUSANDS = "."
"""Excel sayıyı açan bilgisayarın bölge ayarıyla gösterir; dosyada bölge yazmaz. Belgeler Türkçe
bölge ayarıyla açılıyor sayılır: ondalık virgül, binlik nokta."""
_GENERAL = "general"
_SEGMENT_RE = re.compile(
    r'"(?P<quoted>[^"]*)"|\\(?P<escaped>.)|(?P<skip>_.|\*.|\[[^\]]*\])|(?P<code>[^"\\_*\[]+)'
)
_DIGITS_RE = re.compile(r"[0#?][0#?,.]*")
_UNSUPPORTED_CODE_RE = re.compile(r"[A-Za-z/@]")

Grid = list[list[str]]


@dataclass(frozen=True)
class _Pattern:
    prefix: str
    suffix: str
    decimals: int
    min_integer: int
    thousands: bool
    percent: bool


def _general(value: float) -> str:
    text = str(value) if isinstance(value, int) else format(value, ".15g")
    return text.replace(".", _DECIMAL)


def _code_and_visible(section: str) -> tuple[str, str] | None:
    """Biçim bölümünün kod kısmı ve görünen yazısı; desteklenmeyen kodda None.

    Tırnaklı ve kaçışlı karakterler yazıdır; renk, dil, hizalama boşluğu ve dolgu kodları
    görünmez. Kod kısmında yazı karakterleri boşlukla tutulur, konumlar iki tarafta aynıdır.
    """
    code, visible = "", ""
    for match in _SEGMENT_RE.finditer(section):
        if match.group("code"):
            if _UNSUPPORTED_CODE_RE.search(match.group("code")):
                return None
            code += match.group("code")
            visible += match.group("code")
        elif match.group("skip") is None:
            literal = match.group("quoted") or match.group("escaped") or ""
            code += " " * len(literal)
            visible += literal
    return code, visible


def _pattern(number_format: str) -> _Pattern | None:
    """Biçimin ilk bölümü; tarih, kesir, bilimsel gösterim gibi desteklenmeyen biçimde None."""
    section = number_format.split(";")[0]
    if not section or section.lower() == _GENERAL:
        return None
    parts = _code_and_visible(section)
    match = _DIGITS_RE.search(parts[0]) if parts else None
    if parts is None or match is None or match.group().endswith(","):
        return None
    code, visible = parts
    integer, _, fraction = match.group().partition(".")
    return _Pattern(
        prefix=visible[: match.start()],
        suffix=visible[match.end() :],
        decimals=len(fraction),
        min_integer=integer.count("0"),
        thousands="," in integer,
        percent="%" in code,
    )


def display_number(value: float, number_format: str) -> str:
    """Sayının Excel'de gösterilen yazılışı.

    Eksi değer her zaman eksi işaretiyle yazılır: biçimin eksi bölümü (parantez, yalnız renk)
    kullanılmaz, işaret kaybolup değer değişmesin diye.
    """
    pattern = _pattern(number_format)
    if pattern is None:
        return _general(value)
    scaled = value * 100 if pattern.percent else value
    rounded = f"{abs(scaled):.{pattern.decimals}f}"
    integer, _, fraction = rounded.partition(".")
    if pattern.thousands:
        integer = f"{int(integer):,}".replace(",", _THOUSANDS)
    integer = integer.zfill(pattern.min_integer)
    sign = "-" if scaled < 0 and float(rounded) != 0 else ""
    number = f"{integer}{_DECIMAL}{fraction}" if fraction else integer
    return f"{sign}{pattern.prefix}{number}{pattern.suffix}".strip()


def _cell_text(cell: Any) -> str:
    value = cell.value
    if value is None:
        return ""
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, int | float) and not isinstance(value, bool):
        return display_number(value, str(cell.number_format))
    return str(value).strip()


def _read_grid(sheet: Worksheet) -> Grid:
    """Birleşik hücrelerin değerini kapladıkları bütün hücrelere yayar."""
    grid = [[_cell_text(cell) for cell in row] for row in sheet.iter_rows()]
    for merged in sheet.merged_cells.ranges:
        value = _cell_text(sheet.cell(merged.min_row, merged.min_col))
        for row in range(merged.min_row - 1, merged.max_row):
            for column in range(merged.min_col - 1, merged.max_col):
                grid[row][column] = value
    return grid


def _label_score(row: list[str]) -> int:
    return len({cell for cell in row if cell and not NUMERIC_TEXT_RE.match(cell)})


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


def _parse_sheet(sheet: Worksheet) -> list[Element]:
    grid = _read_grid(sheet)
    if not any(any(row) for row in grid):
        return []
    header_index = _find_header(grid)
    labels = _labels(grid, header_index)
    section = SECTION_SEPARATOR.join([sheet.title, *_title_rows(grid, header_index)])
    # Her sayfa en üst düzey başlıktır: önceki sayfanın adı bu sayfanın bölüm yoluna girmez.
    heading = Element(ElementKind.HEADING, section, SourceLocation(sheet=sheet.title), level=1)
    elements = [heading]
    for offset, row in enumerate(grid[header_index + 1 :], start=header_index + 2):
        text = labeled_row(labels, row)
        if text:
            location = SourceLocation(sheet=sheet.title, row=offset)
            elements.append(Element(ElementKind.TABLE_ROW, text, location))
    return elements


def _formulas_without_value(path: Path, values: Any) -> list[str]:
    """Kayıtlı sonucu olmayan formül hücreleri: değer okunamaz, uyarı olarak bildirilir."""
    formulas = load_workbook(path, data_only=False)
    try:
        return [
            f"{sheet.title} sayfası {cell.coordinate}: formülün kayıtlı değeri yok, okunamadı."
            for sheet in formulas.worksheets
            for row in sheet.iter_rows()
            for cell in row
            if cell.data_type == "f" and values[sheet.title][cell.coordinate].value is None
        ]
    finally:
        formulas.close()


def parse_workbook(path: Path) -> tuple[list[Element], list[str]]:
    """Öğeler ve uyarılar; uyarı, okunamayan hücrenin yerini söyler."""
    workbook = load_workbook(path, data_only=True)
    try:
        elements = [element for sheet in workbook.worksheets for element in _parse_sheet(sheet)]
        return elements, _formulas_without_value(path, workbook)
    finally:
        workbook.close()
