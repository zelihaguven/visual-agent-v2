from PIL import Image, ImageDraw

from visual_agent.ingest.ruled_table import find_grid, grid_cells, has_text, label_rows

LINE = 200  # açık gri çizgi (taranmış föylerdeki gibi)


def ruled_table(shaded_column: bool = False) -> Image.Image:
    """4 sütun, 4 satır (başlık, iki değer, çizgisiz alt bilgi) ve yazılar."""
    image = Image.new("L", (800, 400), 255)
    draw = ImageDraw.Draw(image)
    xs, ys = [20, 220, 420, 620, 780], [20, 100, 180, 260, 340]
    if shaded_column:
        draw.rectangle((420, 20, 620, 260), fill=225)
    for y in ys:
        draw.line((xs[0], y, xs[-1], y), fill=LINE, width=3)
    for x in xs:
        # Alt bilgi satırında (260-340) iç dikey çizgi yok: tek hücredir.
        bottom = ys[-1] if x in (xs[0], xs[-1]) else ys[-2]
        draw.line((x, ys[0], x, bottom), fill=LINE, width=3)
    for row, y in enumerate(ys[:3]):
        for column, x in enumerate(xs[:4]):
            draw.rectangle((x + 40, y + 30, x + 90, y + 50), fill=0)  # yazı
    draw.rectangle((60, 290, 400, 310), fill=0)  # alt bilgi yazısı
    return image


def test_rows_and_columns_come_from_the_lines() -> None:
    grid = find_grid(ruled_table())

    assert grid is not None
    rows, columns = grid
    assert len(rows) == 5 and len(columns) == 5


def test_shaded_column_edges_are_boundaries_too() -> None:
    grid = find_grid(ruled_table(shaded_column=True))

    assert grid is not None
    assert len(grid[1]) >= 5


def test_row_without_dividers_is_one_merged_cell() -> None:
    image = ruled_table()
    grid = find_grid(image)
    assert grid is not None

    cells = grid_cells(image, *grid)

    footer = [cell for cell in cells if cell.row == 3]
    assert len(footer) == 1 and (footer[0].column, footer[0].column_end) == (0, 4)
    assert len([cell for cell in cells if cell.row == 1]) == 4
    assert all(has_text(image, cell) for cell in cells)


def test_page_without_lines_is_not_a_ruled_table() -> None:
    image = Image.new("L", (600, 300), 255)
    ImageDraw.Draw(image).rectangle((50, 50, 300, 70), fill=0)

    assert find_grid(image) is None


def test_mostly_empty_rows_are_labels() -> None:
    texts = {(0, c): f"B{c}" for c in range(8)}
    texts |= {(1, c): str(c) for c in range(8)}
    texts |= {(2, 0): "Tall"} | {(2, c): "" for c in range(1, 8)}

    assert label_rows(texts, 8) == {2}
