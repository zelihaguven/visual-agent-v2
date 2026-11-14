import json
from collections.abc import Callable, Sequence
from pathlib import Path

import httpx
import pytest
from PIL import Image

from visual_agent.ingest.cell_reader import (
    CellRead,
    CellReader,
    VisionModelReader,
    canonical,
    same_reading,
    unconfirmed_numbers,
)
from visual_agent.ingest.docling_parser import reread_cells
from visual_agent.ingest.pdf_tables import BoundingBox, TableCell


def image(shade: int = 0) -> Image.Image:
    return Image.new("L", (20, 10), shade)


class Reader:
    """Sabit okuma döndürür ve kaç kez çağrıldığını sayar."""

    def __init__(self, text: str | None) -> None:
        self.text = text
        self.calls = 0

    def __call__(self, _image: Image.Image) -> str | None:
        self.calls += 1
        return self.text


def reader(
    local: str | None, primary: str | None, referee: str | None, limit: int = 10
) -> tuple[CellReader, tuple[Reader, Reader, Reader]]:
    readers = Reader(local), Reader(primary), Reader(referee)
    return CellReader(*readers, max_cells=limit, workers=2), readers


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("27½", "27 1/2"),
        ("21³/4", "21 3/4"),
        ("  -3/8 ", "-3/8"),
        ("20 ⁷⁄₈", "20 7/8"),
        ("?", ""),
        (None, ""),
    ],
)
def test_readings_are_written_the_same_way(text: str | None, expected: str) -> None:
    assert canonical(text) == expected


def test_spacing_does_not_separate_two_readings() -> None:
    assert same_reading("271/2", "27 1/2")
    assert not same_reading("612", "6 1/2")
    assert not same_reading("", "")


def test_value_is_confirmed_when_local_ocr_and_model_agree() -> None:
    cell_reader, (_, _, referee) = reader("27 1/2", "27½", "99")

    assert cell_reader.read([image()]) == [CellRead("27 1/2", confirmed=True)]
    assert referee.calls == 0


def test_referee_decides_when_local_ocr_disagrees() -> None:
    cell_reader, (_, _, referee) = reader("612", "6 1/2", "6 1/2")

    assert cell_reader.read([image()]) == [CellRead("6 1/2", confirmed=True)]
    assert referee.calls == 1


def test_local_ocr_and_referee_agree_when_the_model_misreads() -> None:
    """Qwen "BLO05" (O harfi) okudu; yerel OCR ile hakem "BL005" üzerinde uyuştu."""
    cell_reader, _ = reader("BL005", "BLO05", "BL005")

    assert cell_reader.read([image()]) == [CellRead("BL005", confirmed=True)]


def test_value_stays_unconfirmed_when_no_two_readings_agree() -> None:
    cell_reader, _ = reader("318", "3/8", "-3/8")

    assert cell_reader.read([image()]) == [CellRead("", confirmed=False, seen="3/8", second="318")]


@pytest.mark.parametrize("text", ["1 1", "24 25", "-1/2 1", "1/2 3/8"])
def test_two_values_in_one_cell_are_never_confirmed(text: str) -> None:
    """Komşu iki hücre tek hücre sanıldıysa iki okuyucu da iki değeri okur."""
    cell_reader, _ = reader(text, text, text)

    assert cell_reader.read([image()]) == [CellRead("", confirmed=False, seen=text, second=text)]


def test_whole_number_with_fraction_is_one_value() -> None:
    cell_reader, _ = reader("27 1/2", "27 1/2", "x")

    assert cell_reader.read([image()]) == [CellRead("27 1/2", confirmed=True)]


def test_unreadable_readings_never_confirm_each_other() -> None:
    cell_reader, _ = reader("?", "?", "?")

    assert cell_reader.read([image()]) == [CellRead("", confirmed=False)]


def test_cells_over_the_document_limit_are_not_sent() -> None:
    cell_reader, (_, primary, _) = reader("5", "5", "5", limit=2)

    reads = cell_reader.read([image(), image(), image()])

    assert reads == [CellRead("5", True), CellRead("5", True), None]
    assert primary.calls == 2


def cell(text: str, column: int, header: bool = False, box: bool = True) -> TableCell:
    return TableCell(
        row_start=1,
        row_end=2,
        column_start=column,
        column_end=column + 1,
        text=text,
        header=header,
        bbox=(column * 10.0, 0.0, column * 10.0 + 9, 9.0) if box else None,
    )


def test_merged_cells_are_not_reread() -> None:
    merged = TableCell(1, 2, 9, 11, "1 1", bbox=(0.0, 0.0, 30.0, 9.0))
    asked: list[int] = []

    def read_cells(page: int, boxes: Sequence[BoundingBox]) -> list[CellRead | None]:
        asked.append(len(boxes))
        return []

    updated, unsure = reread_cells([merged], 27, read_cells, page_uncertain=("1",))

    assert asked == [0]
    assert updated == [merged]
    assert unsure == ["1"]


def test_confirmed_cells_replace_ocr_text_and_others_are_marked_uncertain() -> None:
    cells = [
        cell("Front Length", 0, header=True),
        cell("27 a", 1),
        cell("2%", 2),
        cell("Sleeve Length from Shoulder - LS", 3),
        cell("VA", 4),
        cell("28", 5, box=False),
    ]
    asked: list[int] = []

    def read_cells(page: int, boxes: Sequence[BoundingBox]) -> list[CellRead | None]:
        asked.append(len(boxes))
        return [CellRead("27 1/2", True), CellRead("", False), None]

    updated, unsure = reread_cells(cells, 24, read_cells, page_uncertain=("28", "99"))

    assert asked == [3]  # başlık, uzun metin ve kutusuz hücre sorulmaz
    assert [c.text for c in updated] == [
        "Front Length",
        "27 1/2",
        "2%",
        "Sleeve Length from Shoulder - LS",
        "VA",
        "28",
    ]
    # Sayı taşımayan "VA" gizlenecek değer içermez; sorulmayan "28" sayfanın kararıyla belirsiz.
    assert unsure == ["2%", "28"]


def vision_reader(
    tmp_path: Path, handler: Callable[[httpx.Request], httpx.Response]
) -> VisionModelReader:
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return VisionModelReader("model/vl", "anahtar", "https://example.test/api/v1", tmp_path, client)


def test_model_reads_are_cached_and_requests_require_zdr(tmp_path: Path) -> None:
    bodies: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": " 25 7/8\n"}}]})

    read = vision_reader(tmp_path, handler)

    assert read(image()) == "25 7/8"
    assert read(image()) == "25 7/8"
    assert len(bodies) == 1
    assert bodies[0]["provider"] == {"zdr": True, "data_collection": "deny"}
    assert bodies[0]["model"] == "model/vl"


def test_failed_model_request_is_not_cached(tmp_path: Path) -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(503, json={"error": "meşgul"})

    read = vision_reader(tmp_path, handler)

    assert read(image()) is None
    assert read(image()) is None
    assert len(calls) == 2
    assert not any(tmp_path.rglob("*.txt"))


def test_longer_reading_is_kept_when_the_model_drops_lines() -> None:
    """Model çok satırlı hücrenin ilk satırını atlayabiliyor; içerik kaybolmasın."""
    full = 'KNT-222890/PacMan Fleece - Complete/325.0g/98% Cotton, 2% Elastane/49.0"'
    cell_reader, _ = reader(full, 'Complete/325.0g/98% Cotton, 2% Elastane/49.0"', "x")

    [read] = cell_reader.read([image()])

    assert read is not None and not read.confirmed and read.seen == full


def test_numbers_in_long_text_are_confirmed_one_by_one() -> None:
    text = "Development Complete/230.0g/80% Cotton, 20% Polyester/58.6 3/8"
    other = "Development Complete/230.0g/80% Cotton 20% Polyester/58.6 318"

    assert unconfirmed_numbers(text, other) == ["3/8"]
