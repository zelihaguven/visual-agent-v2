"""Sayfa okuyucusu: ölçülmüş kodun kopyası set A kaydıyla aynı sonucu verir; okuyucu yoksa
belge bekler."""

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pypdfium2
import pytest
from PIL import Image, ImageDraw
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

from evals import ocr_score, ocr_truth
from visual_agent.ingest import page_reader
from visual_agent.ingest.elements import ElementKind
from visual_agent.ingest.external import ReaderUnavailable
from visual_agent.ingest.page_reader import (
    PaddleVlReader,
    ReaderConfig,
    is_ocr_layer,
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
    ("primary", "second", "expected"),
    [
        ("İç paça 77.0", "İç paça 77,0", ["77.0"]),  # virgül ve nokta farklı okumadır (0008)
        ("Ölçü 812", "Ölçü B12", ["812"]),  # harf-rakam eşdeğerliği yok
        ("Beden XS-AXL", "Beden XS-4XL", ["XS-AXL"]),  # rakamsız kod da karşılaştırılır
        ("Tolerans 10", "Tolerans 1,0 ölçü 104,5", ["10"]),  # başka sayının parçası onaylamaz
        ("Uzunluk 59", "Uzunluk | 59|", []),  # tablo çizgisi değeri belirsiz yapmaz
        ("12", "12 12", ["12"]),  # geçiş sayısı da tutmalı
    ],
)
def test_second_reading_confirms_a_value_only_with_the_same_token(
    primary: str, second: str, expected: list[str]
) -> None:
    assert page_reader.count_mismatches(primary, second) == expected


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
