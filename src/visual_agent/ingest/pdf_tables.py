"""Tablo hücrelerini "Başlık: değer | Başlık: değer" biçiminde satırlara çevirir."""

from collections.abc import Sequence
from dataclasses import dataclass, replace

from visual_agent.ingest.elements import NUMERIC_TEXT_RE, header_fits, with_empty_cells_marked

COLUMN_JOIN = " & "
_EDGE_ARTIFACTS = " |_"
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
    context: str = ""
    """Satırın bağlı olduğu tablo notları: üstündeki bölüm etiketi ve tablonun alt bilgisi."""


_MIN_LABEL_SPAN = 0.8
"""Tablonun bu kadarını tek hücreyle kaplayan satır değer değil, etiket ya da nottur."""


def _column_headers(cells: Sequence[TableCell]) -> dict[int, str]:
    headers: dict[int, str] = {}
    for cell in cells:
        if cell.header and cell.text.strip():
            for column in range(cell.column_start, cell.column_end):
                headers.setdefault(column, cell.text.strip())
    return headers


@dataclass(frozen=True)
class _HeaderSpan:
    left: float
    right: float
    name: str


def _header_spans(cells: Sequence[TableCell]) -> list[_HeaderSpan]:
    """En alttaki başlık satırının yatay aralıkları: komşu başlıkların ortası sınırdır.

    Tablo yapısı çıkarılırken sütun numarası kayabiliyor (taranmış sayfa); hücrenin sayfadaki
    yeri kaymaz. Başlık kutusu eksikse boş döner, sütun numarası kullanılır.
    """
    headers = [cell for cell in cells if cell.header and cell.text.strip()]
    if not headers:
        return []
    lowest = max(cell.row_start for cell in headers)
    row = sorted(
        (cell for cell in headers if cell.row_start == lowest),
        key=lambda cell: cell.column_start,
    )
    if any(cell.bbox is None for cell in row) or len(row) < 2:
        return []
    centers = [(cell.bbox[0] + cell.bbox[2]) / 2 for cell in row if cell.bbox is not None]
    if centers != sorted(centers):
        return []
    bounds = [
        float("-inf"),
        *((a + b) / 2 for a, b in zip(centers, centers[1:], strict=False)),
        float("inf"),
    ]
    return [
        _HeaderSpan(bounds[index], bounds[index + 1], cell.text.strip())
        for index, cell in enumerate(row)
    ]


def _placed_name(cell: TableCell, spans: Sequence[_HeaderSpan]) -> str | None:
    """Tek sütunluk hücrenin, sayfada altına düştüğü başlık."""
    if not spans or cell.bbox is None or cell.column_end - cell.column_start != 1:
        return None
    center = (cell.bbox[0] + cell.bbox[2]) / 2
    return next((span.name for span in spans if span.left <= center < span.right), None)


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


def _cell_part(cell: TableCell, headers: dict[int, str], spans: Sequence[_HeaderSpan] = ()) -> str:
    covered = range(cell.column_start, cell.column_end)
    placed = _placed_name(cell, spans)
    names = (
        [placed]
        if placed is not None
        else list(dict.fromkeys(headers[column] for column in covered if column in headers))
    )
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
    """Başlık işaretlenmemişse etiketlerden oluşan ilk satır başlıktır; ama yalnız her veri
    satırıyla aynı sayıda dolu hücre taşıyorsa. Docling boş hücreyi hiç vermiyor: form
    tablosunda ilk satırın boş hücresi düşünce etiketler kayıyor ve değer yanlış etiketi
    alıyordu ("Material Description: Fit Approved")."""
    if any(cell.header for cell in cells) or not cells:
        return list(cells)
    first_row = min(cell.row_start for cell in cells)
    first = [cell for cell in cells if cell.row_start == first_row and cell.text]
    width = max(cell.column_end for cell in cells) - min(cell.column_start for cell in cells)
    body = [
        row
        for start in sorted({cell.row_start for cell in cells if cell.row_start > first_row})
        if (row := [cell for cell in cells if cell.row_start == start and cell.text])
        and not _spans_table(row, width)
    ]
    labels = [cell for cell in first if not NUMERIC_TEXT_RE.match(cell.text)]
    if not body or len(labels) * 2 <= len(first) or not header_fits(first, body):
        return list(cells)
    return [replace(cell, header=cell.row_start == first_row) for cell in cells]


def _texts_with_gaps(row_cells: Sequence[TableCell], first_column: int) -> list[str]:
    """Başlıksız satırın hücreleri; aradaki boş sütun "(boş)" olur (docling boş hücre vermez)."""
    texts: list[str] = []
    column = first_column
    for cell in row_cells:
        texts += [""] * max(cell.column_start - column, 0)
        texts.append(cell.text.strip())
        column = max(column, cell.column_end)
    return with_empty_cells_marked(texts)


def group_table_rows(raw_cells: Sequence[TableCell], infer_header: bool = True) -> list[TableRow]:
    """infer_header kapalıysa başlık kararı çağırana aittir: işaretsiz ilk satır başlık yapılmaz."""
    cleaned = [replace(cell, text=cell.text.strip(_EDGE_ARTIFACTS)) for cell in raw_cells]
    cells = _with_label_first_row(cleaned) if infer_header else cleaned
    headers = _column_headers(cells)
    spans = _header_spans(cells)
    body = [cell for cell in cells if not cell.header and cell.text.strip()]
    first_column = min((cell.column_start for cell in cells), default=0)
    width = max((cell.column_end for cell in cells), default=0) - first_column
    rows: list[TableRow] = []
    labels: list[bool] = []
    for group in _row_groups(body):
        row_cells = sorted(
            (cell for cell in body if any(_covers(cell, row) for row in group)),
            key=lambda cell: (cell.column_start, cell.row_start),
        )
        label = _spans_table(row_cells, width)
        # Etiket ve not satırı bir sütunun değeri değildir; sütun başlığı almaz.
        if label:
            parts = [cell.text.strip() for cell in row_cells]
        elif headers or spans:
            parts = [_cell_part(cell, headers, spans) for cell in row_cells]
        else:
            parts = _texts_with_gaps(row_cells, first_column)
        text = " | ".join(parts)
        rows.append(TableRow(text, _union([c.bbox for c in row_cells if c.bbox is not None])))
        labels.append(label)
    return _with_table_context(rows, labels)


_MAX_LABEL_CELLS = 2


def _spans_table(row_cells: Sequence[TableCell], width: int) -> bool:
    """Tabloyu en çok iki geniş hücreyle kaplayan satır: bölüm etiketi ya da tablo notu."""
    spans = [cell.column_end - cell.column_start for cell in row_cells]
    return (
        width > 1
        and len(row_cells) <= _MAX_LABEL_CELLS
        and (len(spans) == 1 or min(spans) > 1)
        and sum(spans) >= _MIN_LABEL_SPAN * width
    )


def _with_table_context(rows: Sequence[TableRow], labels: Sequence[bool]) -> list[TableRow]:
    """Tabloyu kaplayan satırlar değer satırı değildir: ortadaki, altındaki satırların bölüm
    etiketidir ("Tall"); sondakiler bütün tablonun notudur ("Grade Rule Display: Increment").
    Etiket satırları ayrı satır olarak kalmaz, bağlandıkları satırların bağlamına girer.
    """
    if not any(labels) or all(labels):
        return list(rows)
    last_value = max(index for index, label in enumerate(labels) if not label)
    note = " ".join(
        row.text
        for row, label in zip(rows[last_value + 1 :], labels[last_value + 1 :], strict=True)
    )
    result, section = [], ""
    for row, label in zip(rows[: last_value + 1], labels[: last_value + 1], strict=True):
        if label:
            section = row.text
            continue
        context = " · ".join(part for part in (section, note) if part)
        result.append(replace(row, context=context))
    return result
