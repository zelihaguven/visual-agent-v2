"""Tablo hücrelerini "Başlık: değer | Başlık: değer" biçiminde satırlara çevirir."""

import re
from collections.abc import Sequence
from dataclasses import dataclass, replace

COLUMN_JOIN = " & "
_EDGE_ARTIFACTS = " |_"
_NUMERIC_RE = re.compile(r"^[\d.,\s%±/-]+$")
BoundingBox = tuple[float, float, float, float]


@dataclass(frozen=True)
class TableCell:
    row_start: int
    row_end: int
    column_start: int
    column_end: int
    text: str
    header: bool = False
    bbox: BoundingBox | None = None


@dataclass(frozen=True)
class TableRow:
    text: str
    bbox: BoundingBox | None


def _column_headers(cells: Sequence[TableCell]) -> dict[int, str]:
    headers: dict[int, str] = {}
    for cell in cells:
        if cell.header and cell.text.strip():
            for column in range(cell.column_start, cell.column_end):
                headers.setdefault(column, cell.text.strip())
    return headers


def _covers(cell: TableCell, row: int) -> bool:
    return cell.row_start <= row < cell.row_end


def _row_groups(body: Sequence[TableCell]) -> list[list[int]]:
    """Dikey birleşik ilk hücrenin kapladığı satırlar tek mantıksal satırdır."""
    rows = sorted({row for cell in body for row in range(cell.row_start, cell.row_end)})
    groups: list[tuple[TableCell, list[int]]] = []
    for row in rows:
        covering = [cell for cell in body if _covers(cell, row)]
        anchor = min(covering, key=lambda cell: (cell.column_start, cell.row_start))
        if groups and groups[-1][0] is anchor:
            groups[-1][1].append(row)
        else:
            groups.append((anchor, [row]))
    return [group for _, group in groups]


def _cell_part(cell: TableCell, headers: dict[int, str]) -> str:
    covered = range(cell.column_start, cell.column_end)
    names = list(dict.fromkeys(headers[column] for column in covered if column in headers))
    single_column = cell.column_end - cell.column_start == 1
    label = COLUMN_JOIN.join(names) if cell.column_start > 0 or single_column else ""
    text = cell.text.strip()
    return f"{label}: {text}" if label and label != text else text


def _union(boxes: Sequence[BoundingBox]) -> BoundingBox | None:
    if not boxes:
        return None
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def _with_label_first_row(cells: Sequence[TableCell]) -> list[TableCell]:
    """Başlık işaretlenmemişse etiketlerden oluşan ilk satır başlıktır."""
    if any(cell.header for cell in cells) or not cells:
        return list(cells)
    first_row = min(cell.row_start for cell in cells)
    first = [cell for cell in cells if cell.row_start == first_row and cell.text]
    has_body = any(cell.row_start > first_row for cell in cells)
    labels = [cell for cell in first if not _NUMERIC_RE.match(cell.text)]
    if not has_body or len(labels) * 2 <= len(first):
        return list(cells)
    return [replace(cell, header=cell.row_start == first_row) for cell in cells]


def group_table_rows(raw_cells: Sequence[TableCell]) -> list[TableRow]:
    cleaned = [replace(cell, text=cell.text.strip(_EDGE_ARTIFACTS)) for cell in raw_cells]
    cells = _with_label_first_row(cleaned)
    headers = _column_headers(cells)
    body = [cell for cell in cells if not cell.header and cell.text.strip()]
    rows = []
    for group in _row_groups(body):
        row_cells = sorted(
            (cell for cell in body if any(_covers(cell, row) for row in group)),
            key=lambda cell: (cell.column_start, cell.row_start),
        )
        text = " | ".join(_cell_part(cell, headers) for cell in row_cells)
        rows.append(TableRow(text, _union([c.bbox for c in row_cells if c.bbox is not None])))
    return rows
