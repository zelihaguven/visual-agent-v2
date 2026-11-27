"""Sayfa okuyucusu: ölçülmüş kodun kopyası set A kaydıyla aynı sonucu verir; okuyucu yoksa
belge bekler."""

import base64
import io
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pypdfium2
import pytest
from PIL import Image, ImageDraw
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from evals import ocr_score, ocr_truth
from visual_agent.domain.document import Box
from visual_agent.ingest import page_reader
from visual_agent.ingest.elements import (
    CLOUD_OUTAGE,
    INGEST_PROGRESS,
    CloudOutage,
    ElementKind,
)
from visual_agent.ingest.external import ReaderUnavailable
from visual_agent.ingest.page_reader import (
    PaddleVlReader,
    ReaderConfig,
    is_ocr_layer,
    page_elements,
    parse_reader_setting,
    read_embedded_images,
    read_scanned_pages,
)

RECORD = Path(__file__).parent.parent / "evals/results/2026-11-16-set-a-benzetim/paddle"
RESULTS = sorted(RECORD.glob("*/s*_res.json"))
"""Set A benzetiminde PaddleOCR-VL'nin 42 sayfalık ham okuması ve ölçümde Tesseract'la
hesaplanan gizleme işaretleri (`*_uncertain.json`). Sayfa görüntüleri ve Tesseract'ın ham
metni kayıtta yoktur; set A'ya yeniden okuyucu çalıştırılmaz."""


def _recorded(result: Path) -> tuple[dict[str, Any], dict[int, list[str]]]:
    data = json.loads(result.read_text(encoding="utf-8"))
    uncertain = result.with_name(result.name.replace("_res", "_uncertain"))
    marks = json.loads(uncertain.read_text(encoding="utf-8"))
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


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1\\frac{{1}}{{8}}", "1 1/8"),  # çift parantezli argüman (6026417 s.13)
        ("$ 12\\frac{{5}}{{8}} $", "12 5/8"),
        ("$ -{1\\frac{1}{4}} $", "-1 1/4"),  # kesri saran grup parantezi (6026411 s.16)
        ("-{3\\frac{1}{8}}", "-3 1/8"),
        ("$ 23\\frac{1}{2} $", "23 1/2"),  # tek parantez eskisi gibi
        ("$ -^{1}/_{4} $", "-^{1}/_{4}"),  # kesir olmayan parantez dokunulmaz
        ("{x} ve {1}", "{x} ve {1}"),
        ("1\\frac{1}{8}}2", "1 1/8}2"),  # kesre ait olmayan parantez yutulmaz ("1/82" olmaz)
        ("1\\frac{{1}}{8}", "1 1/8"),  # argümanlar ayrı ayrı dengeli
    ],
)
def test_latex_fractions_with_double_or_group_braces_become_fractions(
    text: str, expected: str
) -> None:
    assert page_reader.canonical(text) == expected


@pytest.mark.parametrize(
    ("primary", "second", "expected"),
    [
        ("İç paça 77.0", "İç paça 77,0", ["77.0"]),  # virgül ve nokta farklı okumadır (0008)
        ("Ölçü 812", "Ölçü B12", ["812"]),  # harf-rakam eşdeğerliği yok
        ("Beden XS-AXL", "Beden XS-4XL", ["XS-AXL"]),  # rakamsız kod da karşılaştırılır
        ("Tolerans 10", "Tolerans 1,0 ölçü 104,5", ["10"]),  # başka sayının parçası onaylamaz
        ("Uzunluk 59", "Uzunluk | 59|", []),  # tablo çizgisi değeri belirsiz yapmaz
        ("12", "12 12", ["12"]),  # geçiş sayısı da tutmalı
        ("Değer 112 cm", "Değer /12 cm", ["112"]),  # eğik çizgi "1" sayılmaz
        ("Kol 318 ölçü", "Kol 3/8 ölçü", ["318"]),  # kesir çizgisi "1" okuması değildir
        ("Tolerans ±1/2", "Tolerans +1/2", ["±1/2"]),
        ("40lbs yük", "40 lbs yük", ["40lbs"]),  # farklı bölünen parça da uyuşmaz
        ("43-3/8 ölçü", "43.3/8 ölçü", ["43-3/8"]),
    ],
)
def test_second_reading_confirms_a_value_only_with_the_same_token(
    primary: str, second: str, expected: list[str]
) -> None:
    assert page_reader.count_mismatches(primary, second) == expected
    assert ocr_score.count_mismatches(primary, second) == expected  # dondurulmuş kopyayla aynı


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
    assert all(row.from_ocr for row in rows)
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


def _rows(html: str) -> list[str]:
    return [
        e.text for e in page_elements(_page([_block(0, "table", html)]), 1, (500.0, 1000.0), {})
    ]


def test_table_whose_header_lost_a_cell_is_written_as_read() -> None:
    """Fotoğraf kaydı (2026-11-17): başlığın ilk hücresi düştü, "Bel" satırı "S: Bel | M: 38,0"
    diye yazıldı (doğrusu S 38,0, M 40,0). Değer yanlış sütunun adını almamalı."""
    html = (
        "<table><tr><td>S</td><td>M</td><td>L</td><td>Tolerans (cm)</td></tr>"
        "<tr><td>Bel</td><td>38,0</td><td>40,0</td><td>42,0</td><td>1,0</td></tr>"
        "<tr><td>Kalça</td><td>47,0</td><td>49,0</td><td>51,0</td><td>1,0</td></tr></table>"
    )

    assert _rows(html) == [
        "S | M | L | Tolerans (cm)",
        "Bel | 38,0 | 40,0 | 42,0 | 1,0",
        "Kalça | 47,0 | 49,0 | 51,0 | 1,0",
    ]


def test_table_with_a_short_data_row_is_written_as_read() -> None:
    html = (
        "<table><tr><td>Ölçü</td><td>S</td><td>M</td></tr>"
        "<tr><td>Bel</td><td>38,0</td><td>40,0</td></tr>"
        "<tr><td>Kalça</td><td>49,0</td></tr></table>"
    )

    assert _rows(html) == ["Ölçü | S | M", "Bel | 38,0 | 40,0", "Kalça | 49,0"]


def test_table_with_equal_rows_keeps_its_header() -> None:
    html = (
        "<table><tr><td>Ölçü</td><td>S</td><td>M</td></tr>"
        "<tr><td>Bel</td><td>38,0</td><td>40,0</td></tr>"
        "<tr><td>Kalça</td><td>47,0</td><td>49,0</td></tr></table>"
    )

    assert _rows(html) == ["Ölçü: Bel | S: 38,0 | M: 40,0", "Ölçü: Kalça | S: 47,0 | M: 49,0"]


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


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8111/",
        "http://192.168.1.20:8111/",
        "http://10.0.0.5:8111/",
        "http://mac-studio.local:8111/",
        "http://[::1]:8111/",
    ],
)
def test_reader_server_on_this_machine_or_local_network_is_accepted(url: str) -> None:
    assert parse_reader_setting(f"mlx-vlm-server@{url}") == ReaderConfig("mlx-vlm-server", url)


@pytest.mark.parametrize(
    "url", ["https://ocr.example.com/", "http://8.8.8.8:8111/", "http://reader:8111/"]
)
def test_remote_reader_server_is_refused(url: str) -> None:
    """Sayfa görüntüsü bütün sayfadır; ZDR denetimi olmayan uzak sunucuya gitmez (kural 4)."""
    with pytest.raises(ValueError, match="yerel ağ"):
        parse_reader_setting(f"mlx-vlm-server@{url}")


def _scan_pages(path: Path, count: int) -> Path:
    pages = [Image.new("RGB", (600, 800), "white") for _ in range(count)]
    for page in pages:
        ImageDraw.Draw(page).rectangle((100, 100, 300, 160), fill="black")
    pages[0].save(path, "PDF", resolution=72.0, save_all=True, append_images=pages[1:])
    return path


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


def _region(left: float, top: float, right: float, bottom: float) -> Box:
    return Box(
        page=1, left=left, top=top, right=right, bottom=bottom, page_width=600, page_height=800
    )


def test_embedded_image_is_cropped_read_and_placed_back_on_its_page(tmp_path: Path) -> None:
    """Karar 0028: gömülü görsel kendi pikselleriyle kırpılıp okunur; kutular sayfaya taşınır."""
    sizes: list[tuple[int, int]] = []

    def read_page(image: Path) -> dict[str, Any]:
        sizes.append(Image.open(image).size)
        block = {**_block(0, "text", "Basınç 185 bar"), "block_bbox": [50, 20, 250, 80]}
        return {"width": 300, "height": 100, "parsing_res_list": [block]}

    [element] = read_embedded_images(
        _scan(tmp_path / "t.pdf"),
        [_region(50, 80, 350, 180)],
        tmp_path,
        read_page,
        lambda _: "Basınç 135 bar",
    )

    assert sizes == [(300, 100)]
    assert (element.text, element.from_ocr, element.ocr_uncertain) == (
        "Basınç 185 bar",
        True,
        ("185",),
    )
    box = element.location.boxes[0]
    assert (box.left, box.top, box.right, box.bottom, box.page_width) == (100, 100, 300, 160, 600)


def _two_images(path: Path, rotate: int = 0) -> Path:
    """Sayfada iki görsel: biri 2 kat, öbürü 0,5 kat çözünürlükte; biri sayfadan taşar."""
    canvas = Canvas(str(path), pagesize=(600, 800))
    canvas.setPageRotation(rotate)
    for size, at, drawn in [
        ((600, 200), (0, 600), (300, 100)),
        ((100, 50), (-100, 300), (200, 100)),
    ]:
        image = Image.new("RGB", size, "white")  # işaret görselin sağında: sayfada görünür
        ImageDraw.Draw(image).rectangle((size[0] * 0.6, 10, size[0] - 5, 30), fill="black")
        canvas.drawImage(ImageReader(image), *at, *drawn)
    canvas.drawString(100, 100, "Metinli sayfa " * 6)
    canvas.save()
    return path


def test_each_embedded_image_is_read_at_its_own_resolution_within_limits(tmp_path: Path) -> None:
    from visual_agent.ingest.tools import inspect_pdf

    sizes: list[tuple[int, int]] = []

    def read_page(image: Path) -> dict[str, Any]:
        sizes.append(Image.open(image).size)
        return {"width": 1, "height": 1, "parsing_res_list": []}

    pdf = _two_images(tmp_path / "iki.pdf")
    [page] = inspect_pdf(pdf)
    boxes = sorted(page.image_boxes, key=lambda box: box.top)
    # Sayfadan taşan görselin kutusu sayfayla kesişir; 0,5 kat çözünürlük 72 dpi'ye çıkar.
    assert [(box.left, box.top, box.right, box.bottom) for box in boxes] == [
        (0, 100, 300, 200),
        (0, 400, 100, 500),
    ]
    read_embedded_images(pdf, boxes, tmp_path, read_page, str)
    assert sizes == [(600, 200), (100, 100)]


def test_image_on_a_rotated_text_page_sends_the_whole_page_to_the_reader(tmp_path: Path) -> None:
    from visual_agent.ingest.text_layer import PageKind
    from visual_agent.ingest.tools import inspect_pdf

    [page] = inspect_pdf(_two_images(tmp_path / "doner.pdf", rotate=90))

    assert page.kind is PageKind.SCANNED


def test_heading_inside_an_embedded_image_opens_no_section() -> None:
    region = _region(100, 100, 300, 300)
    [element] = page_elements(
        _page([_block(0, "paragraph_title", "PNT-1162 etiketi")]),
        1,
        (600.0, 800.0),
        {},
        region=region,
    )

    assert element.kind is ElementKind.TEXT


def test_embedded_image_waits_for_the_reader_unless_it_is_blank(tmp_path: Path) -> None:
    scan = _scan(tmp_path / "t.pdf")
    with pytest.raises(ReaderUnavailable):
        read_embedded_images(scan, [_region(50, 80, 350, 180)], tmp_path, None, lambda _: "")
    assert read_embedded_images(scan, [_region(400, 400, 500, 500)], tmp_path, None, str) == []


def test_unreachable_server_means_waiting_not_failure(tmp_path: Path) -> None:
    reader = PaddleVlReader(ReaderConfig("mlx-vlm-server", "http://127.0.0.1:9/"))

    with pytest.raises(ReaderUnavailable, match="ulaşılamadı"):
        reader.read(tmp_path / "s1.png")


def test_blocks_go_to_the_server_one_at_a_time(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Aynı anda giden istekleri sunucu birlikte işler; çıktı isteklerin denk gelişine göre
    değişir (2026-11-18: aynı fotoğrafta başlık hücresi bir okumada düştü, değerler kaydı)."""
    seen: dict[str, Any] = {}

    class FakePipeline:
        def __init__(self, **kwargs: Any) -> None:
            seen.update(kwargs)

        def predict(self, _: str) -> list[Any]:
            return [type("Result", (), {"json": {"res": {"parsing_res_list": []}}})()]

    monkeypatch.setitem(
        __import__("sys").modules, "paddleocr", type("M", (), {"PaddleOCRVL": FakePipeline})
    )
    monkeypatch.setattr("httpx.get", lambda *_, **__: None)

    PaddleVlReader(ReaderConfig("mlx-vlm-server", "http://127.0.0.1:8111/")).read(
        tmp_path / "s.png"
    )

    assert seen["vl_rec_max_concurrency"] == 1


def test_image_file_is_read_with_its_own_pixels_and_orientation(tmp_path: Path) -> None:
    photo = Image.new("RGB", (900, 500), "white")
    ImageDraw.Draw(photo).rectangle((50, 50, 400, 120), fill="black")
    source = tmp_path / "foto.png"
    photo.save(source)
    converted = tmp_path / "foto.pdf"
    photo.resize((300, 167)).save(converted, "PDF", resolution=150.0)  # küçültülmüş kopya
    sizes: list[tuple[int, int]] = []

    def read_page(image: Path) -> dict[str, Any]:
        sizes.append(Image.open(image).size)
        block = _block(0, "text", "Tork 210 Nm")
        return {"width": 900, "height": 500, "parsing_res_list": [block]}

    elements = read_scanned_pages(converted, [1], tmp_path, read_page, lambda _: "210", source)

    assert sizes == [(900, 500)]
    box = elements[0].location.boxes[0]
    assert box.page_width == pytest.approx(144.0) and box.left == pytest.approx(16.0)


def _layered_pdf(path: Path, order: str, invisible: bool, cover: bool = True) -> Any:
    """order: "image-text" (metin üstte) ya da "text-image" (metin görüntünün altında)."""
    canvas = Canvas(str(path), pagesize=(400, 600))
    scan = ImageReader(Image.new("RGB", (40, 60), "white"))

    def draw_image() -> None:
        size = (400, 600) if cover else (80, 80)
        canvas.drawImage(scan, 0, 0, *size)

    def draw_text() -> None:
        for line in range(3):
            text = canvas.beginText(40, 500 - 40 * line)
            if invisible:
                text.setTextRenderMode(3)
            text.textLine("Bel 38,0 cm tolerans 1,0")
            canvas.drawText(text)

    for step in order.split("-"):
        draw_image() if step == "image" else draw_text()
    canvas.save()
    return pypdfium2.PdfDocument(path)[0]


@pytest.mark.parametrize(
    ("order", "invisible", "cover", "expected"),
    [
        ("image-text", True, True, True),  # ocrmypdf: görüntünün üstünde görünmez metin
        ("text-image", False, True, True),  # metin görüntünün altında kalmış
        ("image-text", False, True, False),  # dijital sayfa: arka plan görüntüsü, görünür metin
        ("image-text", True, False, False),  # küçük görsel: sayfa taranmış değil
        ("text", False, True, False),  # yalnız metin
        ("image", False, True, False),  # yalnız görüntü: zaten metin katmanı yok
    ],
)
def test_text_hidden_under_a_page_covering_image_is_an_ocr_layer(
    tmp_path: Path, order: str, invisible: bool, cover: bool, expected: bool
) -> None:
    page = _layered_pdf(tmp_path / "s.pdf", order, invisible, cover)

    assert is_ocr_layer(page, 400.0 * 600.0) is expected


COVER_FORM = (
    "<table><tr><td>Sample Status</td><td>Fit Approved, Hold Sampling</td>"
    "<td>Main Material #</td><td>KNT-222888</td><td>Modified By</td><td>Eunbi Kim</td></tr>"
    '<tr><td colspan="2">Supplier Request Round</td><td>Material Description</td>'
    "<td>PacMan - Fleece - Solid</td><td></td><td></td></tr>"
    "<tr><td>Regional Fit</td><td>US</td><td>Created By</td><td>Christianah Owolabi</td>"
    "<td></td><td></td></tr></table>"
)
"""6013448 kapak sayfasının okuyucudan gelen ham tablosu: etiket ile değeri aynı satırda."""


def _table_texts(html: str) -> list[str]:
    elements = page_elements(_page([_block(0, "table", html)]), 1, (500.0, 1000.0), {})
    return [element.text for element in elements]


def test_form_table_rows_stay_as_read_and_keep_label_next_to_its_value() -> None:
    texts = _table_texts(COVER_FORM)

    assert texts[0].startswith("Sample Status | Fit Approved, Hold Sampling | Main Material #")
    # Etiketin değeri boş: yeri korunur, bir sonraki etiket onun değeri sanılmaz (sınır seti C2).
    assert (
        texts[1]
        == "Supplier Request Round | (boş) | Material Description | PacMan - Fleece - Solid"
    )
    assert texts[2] == "Regional Fit | US | Created By | Christianah Owolabi"
    assert not any("Sample Status: Regional Fit" in text for text in texts)


def test_form_table_whose_first_value_is_a_number_is_not_a_header_table() -> None:
    form = (
        "<table><tr><td>Style #</td><td>6013448</td><td>Product Family</td><td>Fleece</td></tr>"
        "<tr><td>Style Name</td><td>UA Rival Flc Hoodie</td><td>Fit Type</td><td>Regular</td></tr>"
        "<tr><td>Sub Category</td><td>Sportstyle</td><td>Size Range</td>"
        "<td>XS-4XL, SMT-4XLT</td></tr>"
        "<tr><td>Product Team</td><td>Mens</td><td>Actual Sizes</td><td>XS-4XLT</td></tr></table>"
    )

    texts = _table_texts(form)

    assert texts[0] == "Style # | 6013448 | Product Family | Fleece"
    assert texts[2] == "Sub Category | Sportstyle | Size Range | XS-4XL, SMT-4XLT"


def test_measurement_table_with_numbered_size_names_keeps_its_header() -> None:
    table = (
        "<table><tr><td>Dim</td><td>Description</td><td>Tol (-)</td><td>XS</td><td>3XL</td></tr>"
        "<tr><td>BL005</td><td>Front Length</td><td>-3/8</td><td>24</td><td>29</td></tr>"
        "<tr><td>SL005</td><td>Sleeve Length</td><td>-1/4</td><td>25 1/2</td><td>30</td></tr>"
        "</table>"
    )

    texts = _table_texts(table)

    assert texts[0] == "Dim: BL005 | Description: Front Length | Tol (-): -3/8 | XS: 24 | 3XL: 29"
    assert len(texts) == 2


def test_text_only_table_has_no_header_evidence_and_stays_as_read() -> None:
    table = (
        "<table><tr><td>Kolon</td><td>Tip</td></tr><tr><td>ADI</td><td>VARCHAR</td></tr></table>"
    )

    assert _table_texts(table) == ["Kolon | Tip", "ADI | VARCHAR"]


def test_empty_cells_keep_their_place_only_inside_rows_read_as_is() -> None:
    form = (
        "<table><tr><td>Gender</td><td>Mens</td><td>Graphic Fit Block Reference</td><td></td></tr>"
        "<tr><td>Division</td><td></td><td>Season</td><td>FW27</td></tr>"
        "<tr><td></td><td></td><td>Fit Type</td><td>Regular</td></tr></table>"
    )
    measure = (
        "<table><tr><td>Dim</td><td>S</td><td>M</td></tr>"
        "<tr><td>BL005</td><td></td><td>25</td></tr><tr><td>SL005</td><td>26</td><td>27</td></tr>"
        "</table>"
    )

    assert _table_texts(form) == [
        "Gender | Mens | Graphic Fit Block Reference",
        "Division | (boş) | Season | FW27",
        "(boş) | (boş) | Fit Type | Regular",
    ]
    # Başlıklı tabloda boş hücre zaten yazılmaz; biçim değişmez.
    assert _table_texts(measure) == ["Dim: BL005 | M: 25", "Dim: SL005 | S: 26 | M: 27"]


def _heading_page(title: str) -> dict[str, Any]:
    return {
        "width": 600,
        "height": 800,
        "parsing_res_list": [
            {
                "block_id": 0,
                "block_label": "paragraph_title",
                "block_content": title,
                "block_bbox": [0, 0, 300, 20],
            }
        ],
    }


def test_reader_heading_that_carries_a_value_stays_searchable_as_text() -> None:
    """B7: docling yolundaki kural okuyucu yolunda da: değer taşıyan başlık yalnız bölüm adı
    olursa aranamaz ve alıntılanamazdı."""
    elements = page_reader.page_elements(
        _heading_page('1. Hood crossover should be 7/8"'), 1, (600.0, 800.0), {}
    )

    assert [element.kind for element in elements] == [ElementKind.HEADING, ElementKind.TEXT]
    assert elements[1].text == elements[0].text
    assert elements[1].from_ocr


def test_reader_heading_with_only_a_list_number_stays_a_heading() -> None:
    elements = page_reader.page_elements(_heading_page("3. Kurulum"), 1, (600.0, 800.0), {})

    assert [element.kind for element in elements] == [ElementKind.HEADING]


def _html(rows: list[list[str]]) -> str:
    cells = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table>{cells}</table>"


# İlk sayfada değerler rakamlı: başlık yapıdan kabul edilir. Sonraki sayfada renk yolu sütununun
# değerleri rakamsız ("As Artwork"): rakamlı başlık hücresi karşı kanıt sayılıyordu.
_FIRST = _html(
    [
        ["Material", "Qty", "100: White // Red"],
        ["Shell", "1", "White 100"],
        ["Lining", "2", "Red 690"],
    ]
)
_REPEAT = [
    ["Material", "Qty", "100: White / / Red"],
    ["Label", "1", "As Artwork"],
    ["Tag", "2", "N/A"],
]


def _texts_with(
    html: str, known: frozenset[tuple[str, ...]] = frozenset(), learned: set[Any] | None = None
) -> list[str]:
    page = _page([_block(0, "table", html)])
    return [e.text for e in page_elements(page, 1, (500.0, 1000.0), {}, known, learned)]


def test_header_accepted_on_an_earlier_page_labels_the_repeated_table() -> None:
    learned: set[Any] = set()
    _texts_with(_FIRST, learned=learned)

    texts = _texts_with(_html(_REPEAT), frozenset(learned))

    assert texts[0] == "Material: Label | Qty: 1 | 100: White / / Red: As Artwork"
    assert _texts_with(_html(_REPEAT))[0] == "Material | Qty | 100: White / / Red"


def test_repeated_header_must_match_every_cell_and_fit_the_rows() -> None:
    learned: set[Any] = set()
    _texts_with(_FIRST, learned=learned)
    known = frozenset(learned)
    other = [["Material", "Quantity", "100: White // Red"], *_REPEAT[1:]]
    shifted = [_REPEAT[0], ["Label", "1", "As Artwork", "x"], ["Tag", "2", "N/A", "y"]]

    assert _texts_with(_html(other), known)[0].startswith("Material | Quantity")
    assert _texts_with(_html(shifted), known)[0].startswith("Material | Qty")


def test_only_structurally_accepted_headers_are_learned() -> None:
    """Tekrardan kabul edilen başlık öğrenilmez: kabul zincirlenmez."""
    learned: set[Any] = set()
    _texts_with(_FIRST, learned=learned)
    again: set[Any] = set()

    _texts_with(_html(_REPEAT), frozenset(learned), again)

    assert again == set()


def test_header_from_the_same_page_is_not_used() -> None:
    """Yalnız önceki sayfalar: aynı sayfadaki tablolar birbirinin başlığını taşımaz."""
    page = _page([_block(0, "table", _FIRST), _block(1, "table", _html(_REPEAT))])

    texts = [e.text for e in page_elements(page, 1, (500.0, 1000.0), {}, frozenset(), set())]

    assert "Material | Qty | 100: White / / Red" in texts


def test_header_learned_on_a_page_labels_the_next_pages_only(tmp_path: Path) -> None:
    """Sayfalar okuma sırasıyla: önce kabul edilen başlık sonraki sayfada tekrar başlıktır;
    sonraki sayfada öğrenilen başlık önceki sayfaya geri uygulanmaz."""
    tables = {1: _FIRST, 2: _html(_REPEAT)}

    def read_two(order: list[int]) -> list[str]:
        pages = iter(order)

        def read_page(image: Path) -> dict[str, Any]:
            width, height = Image.open(image).size
            block = _block(0, "table", tables[next(pages)])
            return {"width": width, "height": height, "parsing_res_list": [block]}

        scan = _scan_pages(tmp_path / f"iki{order[0]}.pdf", 2)
        return [e.text for e in read_scanned_pages(scan, [1, 2], tmp_path, read_page, str)]

    forward = read_two([1, 2])
    backward = read_two([2, 1])

    assert "Material: Label | Qty: 1 | 100: White / / Red: As Artwork" in forward
    assert "Material | Qty | 100: White / / Red" in backward


def _empty_read(image: Path) -> dict[str, Any]:
    width, height = Image.open(image).size
    return {"width": width, "height": height, "parsing_res_list": []}


def test_reading_reports_progress_after_every_image_and_page(tmp_path: Path) -> None:
    from visual_agent.ingest.tools import inspect_pdf

    reported: list[tuple[str, int, int]] = []
    token = INGEST_PROGRESS.set(lambda kind, done, total: reported.append((kind, done, total)))
    try:
        pdf = _two_images(tmp_path / "iki.pdf")
        [page] = inspect_pdf(pdf)
        read_embedded_images(pdf, list(page.image_boxes), tmp_path, _empty_read, str)
        read_scanned_pages(_scan(tmp_path / "t.pdf"), [1], tmp_path, _empty_read, str)
    finally:
        INGEST_PROGRESS.reset(token)

    assert reported == [
        ("images", 0, 2),
        ("images", 1, 2),
        ("images", 2, 2),
        ("pages", 0, 1),
        ("pages", 1, 1),
    ]


def test_reading_without_a_progress_sink_reads_the_same(tmp_path: Path) -> None:
    """İlerleme dinleyicisi okumayı etkilemez; kurulmadığında da aynı öğeler çıkar."""

    def read_page(image: Path) -> dict[str, Any]:
        width, height = Image.open(image).size
        return {
            "width": width,
            "height": height,
            "parsing_res_list": [_block(0, "text", "Kod ZP-4471")],
        }

    scan = _scan(tmp_path / "t.pdf")
    quiet = read_scanned_pages(scan, [1], tmp_path, read_page, lambda _: "Kod ZP-4471")
    token = INGEST_PROGRESS.set(lambda *_: None)
    try:
        heard = read_scanned_pages(scan, [1], tmp_path, read_page, lambda _: "Kod ZP-4471")
    finally:
        INGEST_PROGRESS.reset(token)
    assert heard == quiet


# --- Bulut okuması (karar 0035) ---

QWEN = "qwen/qwen3-vl-30b-a3b-instruct"
GEMMA = "google/gemma-4-26b-a4b-it"


class _OpenRouter:
    """Sahte OpenRouter: ZDR dizini ve sohbet tamamlama; istekleri sayar."""

    def __init__(self, reply: str | list[str] = "", fail: bool = False) -> None:
        """reply: her isteğe aynı cevap ya da sırayla verilecek cevaplar."""
        self.replies = reply if isinstance(reply, list) else None
        self.reply, self.fail = reply, fail
        self.bodies: list[dict[str, Any]] = []
        self.requests = 0

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests += 1
        if self.fail:
            raise httpx.ConnectError("ulaşılamadı", request=request)
        if request.url.path.endswith("/endpoints/zdr"):
            entries = [
                {"model_id": model, "tag": "zdr-saglayici", "safety_retention": False}
                for model in (QWEN, GEMMA)
            ]
            return httpx.Response(200, json={"data": entries})
        self.bodies.append(json.loads(request.content))
        content = self.replies.pop(0) if self.replies is not None else self.reply
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    def config(self, cache: Path) -> page_reader.CloudConfig:
        return page_reader.CloudConfig(
            base_url="https://openrouter.test/api/v1",
            api_key="test",
            cache=cache,
            reader_model=QWEN,
            figure_check_model=GEMMA,
            transport=httpx.MockTransport(self.handle),
        )


def _qwen_check(server: _OpenRouter, cache: Path) -> page_reader.SecondReader:
    config = server.config(cache)
    return page_reader.cloud_reader(
        config, config.reader_model, page_reader.CHECK_PROMPT, page_reader.CHECK_MAX_TOKENS
    )


def _paddle(content: str, label: str = "text") -> Any:
    def read_page(image: Path) -> dict[str, Any]:
        width, height = Image.open(image).size
        block = {**_block(0, label, content), "block_bbox": [100, 100, 300, 160]}
        return {"width": width, "height": height, "parsing_res_list": [block]}

    return read_page


def _unavailable(_: Image.Image) -> str:
    raise page_reader.CloudUnavailable("ulaşılamadı")


def _cloud(
    check: page_reader.SecondReader,
    figure_read: page_reader.SecondReader = _unavailable,
    figure_check: page_reader.SecondReader = _unavailable,
) -> page_reader.CloudReaders:
    return page_reader.CloudReaders(check, figure_read, figure_check)


def _read(
    tmp_path: Path,
    read_page: Any,
    second: page_reader.SecondReader,
    cloud: page_reader.CloudReaders | None,
) -> list[Any]:
    """600x800 piksellik tek sayfalık tarama, (100, 100)–(300, 160) arası dolu."""
    scan = _scan(tmp_path / "t.pdf")
    return read_scanned_pages(scan, [1], tmp_path, read_page, second, cloud=cloud)


def test_qwen_check_hides_a_value_paddle_read_differently(tmp_path: Path) -> None:
    """İkinci okuma Qwen3-VL: buluta yalnız bloğun kırpıntısı gider, yalnız ZDR sağlayıcıyla."""
    server = _OpenRouter(reply="Basınç 135 bar, kod ZP-4471")
    tesseract_calls: list[Image.Image] = []

    def tesseract(image: Image.Image) -> str:
        tesseract_calls.append(image)
        return "Basınç 185 bar, kod ZP-4471"

    cloud = _cloud(_qwen_check(server, tmp_path / "onbellek"))
    [element] = _read(tmp_path, _paddle("Basınç 185 bar, kod ZP-4471"), tesseract, cloud)

    assert element.ocr_uncertain == ("185",)
    assert tesseract_calls == []
    [body] = server.bodies
    assert body["model"] == QWEN
    assert body["provider"]["zdr"] is True
    assert body["provider"]["only"] == ["zdr-saglayici"]
    image_part = body["messages"][0]["content"][1]["image_url"]["url"]
    sent = Image.open(io.BytesIO(base64.b64decode(image_part.split(",", 1)[1])))
    assert sent.size == (208, 68)  # blok + 4 piksel kenar, bütün sayfa (600x800) değil


def test_unreachable_qwen_falls_back_to_tesseract_and_reading_completes(tmp_path: Path) -> None:
    server = _OpenRouter(fail=True)
    cloud = _cloud(_qwen_check(server, tmp_path / "onbellek"))

    [element] = _read(tmp_path, _paddle("Basınç 185 bar"), lambda _: "Basınç 135 bar", cloud)

    assert element.text == "Basınç 185 bar"
    assert element.ocr_uncertain == ("185",)  # Tesseract'ın okumasıyla denetlendi


def _two_blocks(image: Path) -> dict[str, Any]:
    width, height = Image.open(image).size
    blocks = [
        {**_block(0, "text", "Basınç 185 bar"), "block_bbox": [100, 100, 300, 130]},
        {**_block(1, "text", "Tork 12 Nm"), "block_bbox": [100, 130, 300, 160]},
    ]
    return {"width": width, "height": height, "parsing_res_list": blocks}


def test_after_the_first_cloud_failure_the_document_asks_the_cloud_no_more(
    tmp_path: Path,
) -> None:
    """Devre kesici: ilk hatadan (ZDR dizini bile alınamadı) sonra ikinci blokta istek gitmez;
    iki blok da Tesseract'la denetlenir, belge raporu için tek satır kalır."""
    server = _OpenRouter(fail=True)
    tesseract = lambda _: "Basınç 135 bar Tork 12 Nm"  # noqa: E731
    cloud = _cloud(_qwen_check(server, tmp_path / "onbellek"))
    outage = CloudOutage()
    token = CLOUD_OUTAGE.set(outage)
    try:
        elements = _read(tmp_path, _two_blocks, tesseract, cloud)
    finally:
        CLOUD_OUTAGE.reset(token)

    assert server.requests == 1
    assert [e.ocr_uncertain for e in elements] == [("185",), ()]
    assert outage.fallback_blocks == 2
    warning = outage.warning()
    assert warning is not None and warning.startswith("2 blok Tesseract'la denetlendi; bulut")


def _whole(content: str, label: str = "text") -> Any:
    """Okuyucunun bütün görüntüyü tek blok saydığı sonuç."""

    def read_page(image: Path) -> dict[str, Any]:
        width, height = Image.open(image).size
        block = {**_block(0, label, content), "block_bbox": [0, 0, width, height]}
        return {"width": width, "height": height, "parsing_res_list": [block]}

    return read_page


def test_a_block_covering_the_page_is_read_by_the_cloud_like_any_block(tmp_path: Path) -> None:
    """Şirket onayı (2026-11-27): sayfayı kaplayan blok da buluta gider. Metin bloğunu Qwen
    denetler (Tesseract değil); şekil bloğunu Qwen okur, Gemma denetler."""
    sizes: list[tuple[int, int]] = []

    def qwen(crop: Image.Image) -> str:
        sizes.append(crop.size)
        return "Basınç 185 bar"

    cloud = _cloud(
        qwen, figure_read=lambda _: _json("Tork 12 Nm"), figure_check=lambda _: _json("Tork 12 Nm")
    )
    tesseract = lambda _: "Basınç 135 bar"  # noqa: E731

    [element] = _read(tmp_path, _whole("Basınç 185 bar"), tesseract, cloud)
    [figure] = _read(tmp_path, _whole("", label="image"), tesseract, cloud)

    assert element.ocr_uncertain == ()
    assert sizes == [(600, 800)]
    assert (figure.text, figure.ocr_uncertain) == ("Tork 12 Nm", ())


def test_same_crop_is_paid_once_even_by_a_new_reader(tmp_path: Path) -> None:
    server = _OpenRouter(reply="Basınç 185 bar")
    crop = Image.new("RGB", (40, 20), "white")
    ImageDraw.Draw(crop).rectangle((5, 5, 30, 15), fill="black")

    first = _qwen_check(server, tmp_path)(crop)
    again = _qwen_check(server, tmp_path)(crop.copy())  # yeniden işleme: yeni okuyucu

    assert first == again == "Basınç 185 bar"
    assert len(server.bodies) == 1


class _Failing(_OpenRouter):
    """İlk sohbet isteğine verilen HTTP durumunu döner, sonrakilere cevap verir."""

    def __init__(self, status: int) -> None:
        super().__init__(reply="Basınç 135 bar Tork 12 Nm")
        self.status: int | None = status

    def handle(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/chat/completions") and self.status is not None:
            status, self.status = self.status, None
            self.requests += 1
            return httpx.Response(status, json={"error": "hata"})
        return super().handle(request)


@pytest.mark.parametrize(
    ("status", "opens"), [(413, False), (400, False), (500, True), (401, True)]
)
def test_only_errors_beyond_the_block_open_the_circuit(
    tmp_path: Path, status: int, opens: bool
) -> None:
    """Bloğa özgü 4xx (çok büyük ya da bozuk görüntü) yalnız o bloğu Tesseract'a düşürür; 5xx ve
    kimlik hatası belgenin devresini açar."""
    server = _Failing(status)
    tesseract = lambda _: ""  # noqa: E731
    cloud = _cloud(_qwen_check(server, tmp_path / "onbellek"))
    outage = CloudOutage()
    token = CLOUD_OUTAGE.set(outage)
    try:
        elements = _read(tmp_path, _two_blocks, tesseract, cloud)
    finally:
        CLOUD_OUTAGE.reset(token)

    assert (QWEN in outage.reasons) is opens
    assert len(server.bodies) == (0 if opens else 1)  # ikinci blok buluta gitti mi
    assert elements[0].ocr_uncertain == ("185",)  # ilk blok Tesseract'la (boş okuma) denetlendi
    assert elements[1].ocr_uncertain == (("12",) if opens else ())


class _Limited(_OpenRouter):
    """İlk `limited` sohbet isteğine 429 döner (Retry-After başlığı isteğe bağlı)."""

    def __init__(self, limited: int, retry_after: str | None) -> None:
        super().__init__(reply="Basınç 185 bar")
        self.limited, self.retry_after = limited, retry_after

    def handle(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/chat/completions") and self.limited:
            self.limited -= 1
            self.requests += 1
            headers = {"Retry-After": self.retry_after} if self.retry_after else {}
            return httpx.Response(429, headers=headers, json={"error": "rate limited"})
        return super().handle(request)


def _limited_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, limited: int, retry_after: str | None
) -> tuple[_Limited, list[float], CloudOutage, str | None]:
    waits: list[float] = []

    async def sleep(seconds: float) -> None:
        waits.append(seconds)

    monkeypatch.setattr(page_reader, "_sleep", sleep)
    server = _Limited(limited, retry_after)
    crop = Image.new("RGB", (40, 20), "white")
    outage = CloudOutage()
    token = CLOUD_OUTAGE.set(outage)
    try:
        text: str | None = _qwen_check(server, tmp_path)(crop)
    except page_reader.CloudUnavailable:
        text = None
    finally:
        CLOUD_OUTAGE.reset(token)
    return server, waits, outage, text


def test_rate_limit_waits_as_told_and_does_not_open_the_circuit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    server, waits, outage, text = _limited_read(tmp_path, monkeypatch, 2, "7")

    assert text == "Basınç 185 bar"
    assert waits == [7.0, 7.0]
    assert outage.reasons == {}
    assert len(server.bodies) == 1


def test_rate_limit_without_header_backs_off_within_a_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, waits, outage, text = _limited_read(tmp_path, monkeypatch, 3, None)
    _, capped, _, _ = _limited_read(tmp_path / "b", monkeypatch, 1, "3600")

    assert (text, waits, outage.reasons) == ("Basınç 185 bar", [2.0, 4.0, 8.0], {})
    assert capped == [60.0]


def test_rate_limit_opens_the_circuit_only_when_retries_run_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    server, waits, outage, text = _limited_read(tmp_path, monkeypatch, 10, "1")

    assert text is None
    assert waits == [1.0, 1.0, 1.0]
    assert server.requests == 1 + 4  # ZDR dizini + dört okuma denemesi
    assert QWEN in outage.reasons


def test_cache_key_separates_models_and_prompts(tmp_path: Path) -> None:
    """Önbellek anahtarı model + istem + görüntü: aynı kırpıntıyı başka model ya da başka istem
    önbellekten okumaz."""
    server = _OpenRouter(reply="Basınç 185 bar")
    config = server.config(tmp_path)
    crop = Image.new("RGB", (40, 20), "white")
    ImageDraw.Draw(crop).rectangle((5, 5, 30, 15), fill="black")

    def reader(model: str, prompt: str) -> page_reader.SecondReader:
        return page_reader.cloud_reader(config, model, prompt, 100)

    reader(QWEN, page_reader.CHECK_PROMPT)(crop)
    reader(GEMMA, page_reader.CHECK_PROMPT)(crop)
    assert [body["model"] for body in server.bodies] == [QWEN, GEMMA]
    assert len(list(tmp_path.glob("*.json"))) == 2

    reader(QWEN, page_reader.FIGURE_PROMPT)(crop)
    reader(QWEN, page_reader.CHECK_PROMPT)(crop)  # önbellekte
    assert len(server.bodies) == 3
    assert len(list(tmp_path.glob("*.json"))) == 3


def test_empty_answer_is_not_cached_and_a_broken_cache_file_is_asked_again(
    tmp_path: Path,
) -> None:
    server = _OpenRouter(reply=["", "Basınç 185 bar", "Basınç 185 bar"])
    crop = Image.new("RGB", (40, 20), "white")
    ImageDraw.Draw(crop).rectangle((5, 5, 30, 15), fill="black")

    assert _qwen_check(server, tmp_path)(crop) == ""
    assert not list(tmp_path.glob("*.json"))
    assert _qwen_check(server, tmp_path)(crop) == "Basınç 185 bar"
    [cached] = tmp_path.glob("*.json")
    cached.write_text('{"content": "Bas', encoding="utf-8")  # yarım yazılmış dosya

    assert _qwen_check(server, tmp_path)(crop) == "Basınç 185 bar"
    assert len(server.bodies) == 3
    assert _qwen_check(server, tmp_path)(crop) == "Basınç 185 bar"  # yeniden yazıldı
    assert len(server.bodies) == 3


def _json(*lines: str) -> str:
    return json.dumps({"lines": list(lines), "tables": []})


def _read_figure(
    tmp_path: Path, qwen: page_reader.SecondReader, gemma: page_reader.SecondReader
) -> list[Any]:
    cloud = _cloud(_unavailable, figure_read=qwen, figure_check=gemma)
    return _read(tmp_path, _paddle("", label="image"), str, cloud)


def test_figure_block_values_are_shown_only_when_qwen_and_gemma_agree(tmp_path: Path) -> None:
    agree = _read_figure(tmp_path, lambda _: _json("Tork 12 Nm"), lambda _: _json("Tork 12 Nm"))
    differ = _read_figure(tmp_path, lambda _: _json("Tork 12 Nm"), lambda _: _json("Tork 13 Nm"))
    unchecked = _read_figure(tmp_path, lambda _: _json("Tork 12 Nm"), _unavailable)

    assert [(e.text, e.ocr_uncertain, e.from_ocr) for e in agree] == [("Tork 12 Nm", (), True)]
    assert [e.ocr_uncertain for e in differ] == [("12",)]
    assert [e.ocr_uncertain for e in unchecked] == [("12",)]
    box = agree[0].location.boxes[0]
    assert (box.left, box.top, box.right, box.bottom) == (100, 100, 300, 160)


def test_figure_block_is_skipped_when_qwen_fails_or_no_cloud(tmp_path: Path) -> None:
    assert _read_figure(tmp_path, _unavailable, lambda _: _json("Tork 12 Nm")) == []
    no_cloud = read_scanned_pages(
        _scan(tmp_path / "t.pdf"), [1], tmp_path, _paddle("", label="image"), str
    )
    assert no_cloud == []


def _figure_with_tools(server: _OpenRouter, tmp_path: Path) -> list[Any]:
    from visual_agent.ingest.tools import _cloud_readers

    cloud = _cloud_readers(server.config(tmp_path / "onbellek"))
    return _read(tmp_path, _paddle("", label="image"), str, cloud)


def test_broken_figure_json_is_asked_once_more_and_not_cached(tmp_path: Path) -> None:
    truncated = '{"lines": ["Tork 12 Nm", "Bas'
    server = _OpenRouter(reply=[truncated, _json("Tork 12 Nm"), _json("Tork 12 Nm")])

    elements = _figure_with_tools(server, tmp_path)

    assert [(e.text, e.ocr_uncertain) for e in elements] == [("Tork 12 Nm", ())]
    assert [body["model"] for body in server.bodies] == [QWEN, QWEN, GEMMA]
    assert _figure_with_tools(server, tmp_path) == elements  # iyi cevaplar önbellekte
    assert len(server.bodies) == 3


def test_figure_is_skipped_when_both_readings_are_broken(tmp_path: Path) -> None:
    server = _OpenRouter(reply=["okunamadı", '{"lines": ['])

    assert _figure_with_tools(server, tmp_path) == []
    assert [body["model"] for body in server.bodies] == [QWEN, QWEN]
    assert not list((tmp_path / "onbellek").glob("*.json"))


def test_figure_table_is_read_as_a_table() -> None:
    content = json.dumps({"lines": ["Ölçü"], "tables": [{"rows": [["A", "B"], ["1 <2", ""]]}]})

    assert page_reader.figure_parts(content) == [
        ("text", "Ölçü"),
        ("table", "<table><tr><td>A</td><td>B</td></tr><tr><td>1 &lt;2</td><td></td></tr></table>"),
    ]
    assert page_reader.figure_parts("okunamadı") is None


def _no_blocks(image: Path) -> dict[str, Any]:
    width, height = Image.open(image).size
    return {"width": width, "height": height, "parsing_res_list": []}


def _counting_cloud(calls: list[str]) -> page_reader.CloudReaders:
    def figure(crop: Image.Image) -> str:
        calls.append(f"{crop.width}x{crop.height}")
        return _json("Tork 12 Nm")

    return _cloud(lambda _: "", figure_read=figure, figure_check=lambda _: _json("Tork 12 Nm"))


def test_page_without_layout_blocks_is_read_as_one_figure(tmp_path: Path) -> None:
    """Metin katmanı olmayan sayfada düzen modeli blok bulamazsa sayfa tek şekil bloğudur."""
    calls: list[str] = []

    [element] = _read(tmp_path, _no_blocks, str, _counting_cloud(calls))

    assert calls == ["600x800"]
    assert (element.text, element.ocr_uncertain, element.from_ocr) == ("Tork 12 Nm", (), True)
    box = element.location.boxes[0]
    assert (box.left, box.top, box.right, box.bottom) == (0, 0, 600, 800)


def test_whole_page_figure_only_when_the_layout_found_nothing(tmp_path: Path) -> None:
    calls: list[str] = []

    elements = _read(tmp_path, _paddle("Basınç 185 bar"), str, _counting_cloud(calls))
    no_cloud = _read(tmp_path, _no_blocks, str, None)

    assert [e.text for e in elements] == ["Basınç 185 bar"]
    assert calls == []
    assert no_cloud == []


def test_embedded_image_on_a_text_page_is_not_read_as_a_whole_page(tmp_path: Path) -> None:
    calls: list[str] = []
    scan = _scan(tmp_path / "t.pdf")

    elements = read_embedded_images(
        scan, [_region(50, 80, 350, 180)], tmp_path, _no_blocks, str, _counting_cloud(calls)
    )

    assert (elements, calls) == ([], [])


class _ZdrLimited(_OpenRouter):
    """ZDR dizini isteğine bir kez 429 döner."""

    def __init__(self) -> None:
        super().__init__(reply="Basınç 185 bar")
        self.limited = True

    def handle(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/endpoints/zdr") and self.limited:
            self.limited = False
            self.requests += 1
            return httpx.Response(429, headers={"Retry-After": "5"}, json={"error": "limit"})
        return super().handle(request)


def test_zdr_index_rate_limit_is_waited_out_like_a_reading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    waits: list[float] = []

    async def sleep(seconds: float) -> None:
        waits.append(seconds)

    monkeypatch.setattr(page_reader, "_sleep", sleep)
    server = _ZdrLimited()
    outage = CloudOutage()
    token = CLOUD_OUTAGE.set(outage)
    try:
        text = _qwen_check(server, tmp_path)(Image.new("RGB", (40, 20), "white"))
    finally:
        CLOUD_OUTAGE.reset(token)

    assert (text, waits, outage.reasons) == ("Basınç 185 bar", [5.0], {})
    assert server.requests == 3  # ZDR 429, ZDR, okuma


def test_outage_counts_skipped_and_unchecked_figure_blocks(tmp_path: Path) -> None:
    def count(qwen: page_reader.SecondReader, gemma: page_reader.SecondReader) -> CloudOutage:
        outage = CloudOutage(reasons={"model": "hata"})
        token = CLOUD_OUTAGE.set(outage)
        try:
            _read_figure(tmp_path, qwen, gemma)
        finally:
            CLOUD_OUTAGE.reset(token)
        return outage

    skipped = count(_unavailable, lambda _: _json("Tork 12 Nm"))
    unchecked = count(lambda _: _json("Tork 12 Nm"), _unavailable)

    assert (skipped.skipped_figures, skipped.unchecked_figures) == (1, 0)
    assert (unchecked.skipped_figures, unchecked.unchecked_figures) == (0, 1)
    assert (
        unchecked.warning() == "1 şekil bloğunun değerleri gizlendi; bulut alınamadı (model: hata)."
    )


@pytest.mark.parametrize("header", ["nan", "inf", "-inf"])
def test_retry_after_that_is_not_a_finite_number_is_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, header: str
) -> None:
    _, waits, outage, text = _limited_read(tmp_path, monkeypatch, 1, header)

    assert (text, waits, outage.reasons) == ("Basınç 185 bar", [2.0], {})
