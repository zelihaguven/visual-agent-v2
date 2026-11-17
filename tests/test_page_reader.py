"""Sayfa okuyucusu: ölçülmüş kodun kopyası set A kaydıyla aynı sonucu verir; okuyucu yoksa
belge bekler."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from PIL import Image, ImageDraw

from evals import ocr_score, ocr_truth
from visual_agent.ingest import page_reader
from visual_agent.ingest.elements import ElementKind
from visual_agent.ingest.external import ReaderUnavailable
from visual_agent.ingest.page_reader import (
    PaddleVlReader,
    ReaderConfig,
    page_elements,
    parse_reader_setting,
    read_scanned_pages,
)

RECORD = Path(__file__).parent.parent / "evals/results/2026-11-16-set-a-benzetim/paddle"
RESULTS = sorted(RECORD.glob("*/s*_res.json"))
"""Set A benzetiminde PaddleOCR-VL'nin 42 sayfalık ham okuması ve ölçümde Tesseract'la
hesaplanan gizleme işaretleri (`*_uncertain.json`). Sayfa görüntüleri ve Tesseract'ın ham
metni kayıtta yoktur; set A'ya yeniden okuyucu çalıştırılmaz."""


def _recorded(result: Path) -> tuple[dict[str, Any], dict[int, list[str]]]:
    data = json.loads(result.read_text(encoding="utf-8"))
    marks = json.loads(result.with_name(result.name.replace("_res", "_uncertain")).read_text())
    return data, {int(block): tokens for block, tokens in marks.items()}


def _block_texts(data: dict[str, Any]) -> Iterator[tuple[int, str, str]]:
    for block in data["parsing_res_list"]:
        yield int(block["block_id"]), block["block_label"], str(block.get("block_content") or "")


def test_the_record_is_complete() -> None:
    assert len(RESULTS) == 42


@pytest.mark.parametrize("result", RESULTS, ids=lambda path: f"{path.parent.name}/{path.stem}")
def test_copied_rules_match_the_measured_code_on_every_recorded_block(result: Path) -> None:
    data, _ = _recorded(result)

    for _, label, content in _block_texts(data):
        assert page_reader.canonical(content) == ocr_truth.canonical(content)
        assert page_reader.value_tokens(content) == ocr_score.value_tokens(content)
        if label == "table":
            assert page_reader.html_rows(content) == ocr_score.html_rows(content)


def _replayed_second_reading(data: dict[str, Any]) -> list[str]:
    """Her blok için sahte ikinci okuma: birinci okumanın her üçüncü parçası eksik, bir parça
    fazla. İki kopya aynı girdiyle çağrılır; gerçek Tesseract metni kayıtta yok."""
    readings = []
    for _, label, content in _block_texts(data):
        text = content
        if label == "table":
            text = " ".join(cell for row in ocr_score.html_rows(content) for cell in row)
        tokens = ocr_score.value_tokens(text)
        if tokens:
            kept = [token for index, token in enumerate(tokens) if index % 3 != 1]
            readings.append(" ".join([*kept, "999/7"]))
    return readings


@pytest.mark.parametrize("result", RESULTS, ids=lambda path: f"{path.parent.name}/{path.stem}")
def test_copied_counting_gives_the_same_marks_as_the_measured_code(result: Path) -> None:
    data, _ = _recorded(result)
    image = Image.new("L", (data["width"] // 8, data["height"] // 8), 255)
    measured_reads = iter(_replayed_second_reading(data))
    copied_reads = iter(_replayed_second_reading(data))

    measured = ocr_score.second_reading_marks(result, image, lambda _: next(measured_reads))
    copied = page_reader.second_reading_marks(data, image, lambda _: next(copied_reads))

    assert copied == measured
    assert copied, "sahte okuma en az bir bloğu işaretlemeli"


@pytest.mark.parametrize("result", RESULTS, ids=lambda path: f"{path.parent.name}/{path.stem}")
def test_recorded_marks_are_reproduced_and_reach_the_elements(result: Path) -> None:
    """Ölçümdeki işaretler: (1) uygulama kopyasının parçalarıyla tutarlı, (2) ölçümün gizlediği
    hücrelerdeki değerlerin hepsi uygulamanın öğelerinde belirsiz."""
    data, marks = _recorded(result)
    texts = {block: (label, content) for block, label, content in _block_texts(data)}

    for block, tokens in marks.items():
        label, content = texts[block]
        if label == "table":
            content = " ".join(cell for row in page_reader.html_rows(content) for cell in row)
        # İkinci okuma boşsa her parça uyuşmaz: ölçümdeki işaretler bu kümenin içinde olmalı.
        assert set(tokens) <= set(page_reader.count_mismatches(content, ""))
        assert tokens == sorted(tokens)

    measured_page = ocr_score.paddle_vl_page(result, 1, marks)
    hidden_by_measurement = {
        token
        for row in measured_page.rows
        for cell in row.cells
        if cell.uncertain
        for token in ocr_score.value_tokens(cell.text)
        if any(token in tokens for tokens in marks.values())
    }
    elements = page_elements(data, 1, (data["width"] * 0.24, data["height"] * 0.24), marks)
    hidden_by_application = {token for element in elements for token in element.ocr_uncertain}

    assert hidden_by_application == hidden_by_measurement


def _page(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"width": 1000, "height": 2000, "parsing_res_list": blocks}


def _block(block_id: int, label: str, content: str) -> dict[str, Any]:
    return {
        "block_id": block_id,
        "block_label": label,
        "block_content": content,
        "block_bbox": [100, 200, 500, 400],
    }


def test_table_rows_carry_headers_boxes_and_only_their_own_uncertain_values() -> None:
    table = (
        "<table><tr><td>Kod</td><td>S</td><td>M</td></tr>"
        "<tr><td>BL010</td><td>27½</td><td>28</td></tr>"
        "<tr><td>BL020</td><td>14⅞</td><td>15</td></tr></table>"
    )

    rows = page_elements(_page([_block(3, "table", table)]), 2, (500.0, 1000.0), {3: ["7/8"]})

    assert [row.kind for row in rows] == [ElementKind.TABLE_ROW, ElementKind.TABLE_ROW]
    assert rows[0].text == "Kod: BL010 | S: 27 1/2 | M: 28"
    assert rows[1].text == "Kod: BL020 | S: 14 7/8 | M: 15"
    assert (rows[0].ocr_uncertain, rows[1].ocr_uncertain) == ((), ("7/8",))
    assert all(row.from_ocr and row.ocr_checked for row in rows)
    box = rows[0].location.boxes[0]
    assert (box.page, box.left, box.top, box.right, box.bottom) == (2, 50.0, 100.0, 250.0, 200.0)


def test_single_row_table_keeps_its_values() -> None:
    table = "<table><tr><td>Tork</td><td>210 Nm</td></tr></table>"

    rows = page_elements(_page([_block(0, "table", table)]), 1, (500.0, 1000.0), {})

    assert [row.text for row in rows] == ["Tork | 210 Nm"]


def test_text_and_title_blocks_become_text_and_heading_and_empty_blocks_are_dropped() -> None:
    blocks = [
        _block(0, "paragraph_title", "Bakım"),
        _block(1, "text", "Filtre 750 saatte\ndeğişir."),
        _block(2, "image", ""),
    ]

    elements = page_elements(_page(blocks), 1, (500.0, 1000.0), {1: ["750"]})

    assert [(e.kind, e.text) for e in elements] == [
        (ElementKind.HEADING, "Bakım"),
        (ElementKind.TEXT, "Filtre 750 saatte değişir."),
    ]
    assert elements[1].ocr_uncertain == ("750",)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ("  ", None),
        ("local", ReaderConfig("local")),
        (
            "mlx-vlm-server@http://localhost:8111/",
            ReaderConfig("mlx-vlm-server", "http://localhost:8111/"),
        ),
    ],
)
def test_reader_setting_is_one_value(value: str | None, expected: ReaderConfig | None) -> None:
    assert parse_reader_setting(value) == expected


@pytest.mark.parametrize("value", ["mlx-vlm-server", "local@http://x/", "@http://x/", "a@ftp://x"])
def test_malformed_reader_setting_is_refused(value: str) -> None:
    with pytest.raises(ValueError, match="VA_PAGE_READER"):
        parse_reader_setting(value)


def _scan(path: Path, blank: bool = False, dpi: float = 72.0) -> Path:
    image = Image.new("RGB", (600, 800), "white")
    if not blank:
        ImageDraw.Draw(image).rectangle((100, 100, 300, 160), fill="black")
    image.save(path, "PDF", resolution=dpi)
    return path


@pytest.mark.parametrize("dpi", [72.0, 120.0, 300.0])
def test_scan_is_read_at_its_own_resolution_not_resampled(tmp_path: Path, dpi: float) -> None:
    sizes: list[tuple[int, int]] = []

    def read_page(image: Path) -> dict[str, Any]:
        sizes.append(Image.open(image).size)
        return {"width": 600, "height": 800, "parsing_res_list": []}

    read_scanned_pages(_scan(tmp_path / "t.pdf", dpi=dpi), [1], tmp_path, read_page, lambda _: "")

    assert sizes == [(600, 800)]


def test_scanned_page_is_read_and_checked_by_the_second_reading(tmp_path: Path) -> None:
    seen: list[Path] = []

    def read_page(image: Path) -> dict[str, Any]:
        seen.append(image)
        width, height = Image.open(image).size
        block = _block(0, "text", "Basınç 185 bar, kod ZP-4471")
        return {"width": width, "height": height, "parsing_res_list": [block]}

    elements = read_scanned_pages(
        _scan(tmp_path / "t.pdf"), [1], tmp_path, read_page, lambda _: "Basınç 135 bar ZP-4471"
    )

    assert len(seen) == 1
    assert [e.text for e in elements] == ["Basınç 185 bar, kod ZP-4471"]
    assert elements[0].ocr_uncertain == ("185",)
    assert elements[0].location.page == 1


def test_document_waits_when_no_reader_is_configured(tmp_path: Path) -> None:
    with pytest.raises(ReaderUnavailable, match="VA_PAGE_READER"):
        read_scanned_pages(_scan(tmp_path / "t.pdf"), [1], tmp_path, None, lambda _: "")


def test_blank_page_needs_no_reader(tmp_path: Path) -> None:
    blank = _scan(tmp_path / "bos.pdf", blank=True)

    assert read_scanned_pages(blank, [1], tmp_path, None, lambda _: "") == []


def test_unreachable_server_means_waiting_not_failure(tmp_path: Path) -> None:
    reader = PaddleVlReader(ReaderConfig("mlx-vlm-server", "http://127.0.0.1:9/"))

    with pytest.raises(ReaderUnavailable, match="ulaşılamadı"):
        reader.read(tmp_path / "s1.png")
