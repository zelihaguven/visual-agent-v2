from dataclasses import replace
from pathlib import Path

import pytest

from visual_agent.domain.answer import ModelItem, PromptSource, Quote
from visual_agent.domain.document import Box, ChunkKind, DocumentMeta, SourceLocation
from visual_agent.ingest.chunking import build_chunks
from visual_agent.ingest.elements import (
    CLOUD_OUTAGE,
    INGEST_PROGRESS,
    CloudOutage,
    Element,
    ElementKind,
    carries_value,
)
from visual_agent.ingest.external import ReaderUnavailable
from visual_agent.ingest.pipeline import (
    IngestTools,
    PageInfo,
    ingest_document,
    pages_missing_text,
    promote_code_elements,
    with_images_in_place,
)
from visual_agent.ingest.text_layer import PageKind
from visual_agent.ingest.tools import page_header_identifies
from visual_agent.verification.answer import verify_item

META = DocumentMeta(doc_id="d", title="Belge")


def box(page: int = 1) -> Box:
    return Box(page=page, left=0, top=0, right=100, bottom=20, page_width=600, page_height=800)


def test_missed_page_detection_compares_parsed_text_with_text_layer() -> None:
    pages = [
        PageInfo(page=1, kind=PageKind.TEXT, chars=1000, image_boxes=()),
        PageInfo(page=2, kind=PageKind.TEXT, chars=1000, image_boxes=()),
        PageInfo(page=3, kind=PageKind.NONE, chars=0, image_boxes=()),
    ]
    elements = [
        Element(ElementKind.TEXT, "x" * 900, SourceLocation(page=1)),
        Element(ElementKind.TEXT, "x" * 100, SourceLocation(page=2)),
    ]

    assert pages_missing_text(elements, pages) == [2]


def _fake_tools(calls: list[str], page_kind: PageKind = PageKind.TEXT) -> IngestTools:
    def office_to_pdf(path: Path, work: Path) -> Path:
        calls.append("office")
        return work / "converted.pdf"

    def image_to_pdf(path: Path, work: Path) -> Path:
        calls.append("image")
        return work / "image.pdf"

    def inspect(path: Path) -> list[PageInfo]:
        calls.append("inspect")
        return [PageInfo(page=1, kind=page_kind, chars=500, image_boxes=(box(),))]

    def parse(path: Path) -> list[Element]:
        calls.append(f"parse:{path.name}")
        return [
            Element(ElementKind.HEADING, "Başlık", SourceLocation(page=1)),
            Element(ElementKind.TEXT, "Değer 99 cm " * 40, SourceLocation(page=1, boxes=(box(),))),
        ]

    def read_scanned(path: Path, pages: list[int], work: Path, image: Path | None) -> list[Element]:
        calls.append(f"image:{image.name}") if image is not None else None
        calls.append(f"reader:{pages}")
        return [
            Element(
                ElementKind.TEXT,
                "Taranmış sayfa 42 mm",
                SourceLocation(page=page),
                from_ocr=True,
                ocr_uncertain=("42",),
            )
            for page in pages
        ]

    def read_images(path: Path, images: list[Box], work: Path) -> list[Element]:
        calls.append("images")
        return []

    return IngestTools(
        read_scanned_pages=read_scanned,
        office_to_pdf=office_to_pdf,
        legacy_spreadsheet_to_xlsx=lambda path, work: path,
        image_to_pdf=image_to_pdf,
        inspect_pdf=inspect,
        parse_pdf=parse,
        recover_page_text=lambda path, page: [],
        read_embedded_images=read_images,
    )


def test_word_file_goes_through_pdf_and_a_tiny_image_is_skipped_with_a_warning(
    tmp_path: Path,
) -> None:
    path = tmp_path / "belge.docx"
    path.write_bytes(b"PK\x03\x04x")
    calls: list[str] = []

    result = ingest_document(path, META, _fake_tools(calls), tmp_path)

    assert calls == ["office", "inspect", "parse:converted.pdf"]  # 20 pt'lik görsel okunmaz
    assert result.display_pdf == tmp_path / "converted.pdf"
    assert result.report.warnings == (
        "Sayfa 1: görsel okunmadı (kısa kenarı 20 pt, en az 50 pt gerekir).",
    )


def _at(kind: ElementKind, text: str, top: float, **fields: object) -> Element:
    at = Box(page=1, left=0, top=top, right=200, bottom=top + 80, page_width=600, page_height=800)
    return Element(kind, text, SourceLocation(page=1, boxes=(at,)), **fields)  # type: ignore[arg-type]


def test_embedded_image_is_read_by_the_page_reader_in_its_own_section(tmp_path: Path) -> None:
    """Karar 0028: görsel okuyucudan geçer, değeri taramadan okunmuş sayılır ("Taramadan
    okundu"); öğesi sayfadaki yerine girer, iki ürünlü sayfada kendi ürününün bölümünde kalır."""
    path = tmp_path / "belge.pdf"
    path.write_bytes(b"%PDF-x")
    image = _at(ElementKind.TABLE_ROW, "Bel | M: 40,5", 120)
    read: list[list[Box]] = []

    def images(path: Path, boxes: list[Box], work: Path) -> list[Element]:
        read.append(boxes)
        return [_at(ElementKind.TABLE_ROW, "Bel | M: 40,5", 120, from_ocr=True)]

    def inspect(path: Path) -> list[PageInfo]:
        return [PageInfo(page=1, kind=PageKind.TEXT, chars=50, image_boxes=image.location.boxes)]

    def parse(path: Path) -> list[Element]:
        return [
            _at(ElementKind.HEADING, "PNT-1162 ölçü föyü", 10),
            _at(ElementKind.HEADING, "CKT-7308 ölçü föyü", 400),
            _at(ElementKind.TEXT, "Kalça ölçüleri aşağıda.", 420),
        ]

    tools = replace(_fake_tools([]), inspect_pdf=inspect, parse_pdf=parse)
    result = ingest_document(path, META, replace(tools, read_embedded_images=images), tmp_path)

    assert read == [list(image.location.boxes)]
    [row] = [chunk for chunk in result.chunks if chunk.kind is ChunkKind.TABLE_ROW]
    assert (row.section, row.from_ocr) == ("PNT-1162 ölçü föyü", True)
    assert result.report.warnings == ()


def test_image_elements_keep_the_order_of_pages_and_go_last_when_nothing_is_below() -> None:
    page_one = [_at(ElementKind.TEXT, "Üst", 10), _at(ElementKind.TEXT, "Alt", 300)]
    no_box = Element(ElementKind.TEXT, "Kutusuz", SourceLocation(page=1))
    next_page = Element(ElementKind.TEXT, "İkinci", SourceLocation(page=2))
    bottom = _at(ElementKind.TABLE_ROW, "En alt", 600)
    middle = _at(ElementKind.TABLE_ROW, "Orta", 100)

    placed = with_images_in_place([*page_one, no_box, next_page], [bottom, middle])

    assert [element.text for element in placed] == [
        "Üst",
        "Orta",
        "Alt",
        "Kutusuz",
        "En alt",
        "İkinci",
    ]


def test_document_with_an_image_waits_for_the_page_reader(tmp_path: Path) -> None:
    path = tmp_path / "belge.pdf"
    path.write_bytes(b"%PDF-x")

    def unavailable(path: Path, boxes: list[Box], work: Path) -> list[Element]:
        raise ReaderUnavailable("okuyucu yok")

    def inspect(path: Path) -> list[PageInfo]:
        big = Box(page=1, left=0, top=0, right=300, bottom=200, page_width=600, page_height=800)
        return [PageInfo(page=1, kind=PageKind.TEXT, chars=500, image_boxes=(big,))]

    tools = replace(_fake_tools([]), inspect_pdf=inspect, read_embedded_images=unavailable)
    with pytest.raises(ReaderUnavailable):
        ingest_document(path, META, tools, tmp_path)


def test_text_page_without_images_has_no_image_warning(tmp_path: Path) -> None:
    path = tmp_path / "belge.pdf"
    path.write_bytes(b"%PDF-x")
    tools = _fake_tools([])

    def inspect(path: Path) -> list[PageInfo]:
        return [PageInfo(page=1, kind=PageKind.TEXT, chars=500, image_boxes=())]

    result = ingest_document(path, META, replace(tools, inspect_pdf=inspect), tmp_path)

    assert result.report.warnings == ()


@pytest.mark.parametrize("kind", [PageKind.WEAK, PageKind.SCANNED, PageKind.NONE])
def test_pages_that_are_not_plain_text_go_to_the_page_reader(
    tmp_path: Path, kind: PageKind
) -> None:
    """Karar 0028: zayıf ya da taranmış metin katmanlı sayfa da okuyucudan geçer; Docling'in
    o sayfadaki metni alınmaz, görseli için uyarı çıkmaz (okuyucu sayfanın tamamını okur)."""
    path = tmp_path / "tarama.pdf"
    path.write_bytes(b"%PDF-x")
    calls: list[str] = []

    def recover(path: Path, page: int) -> list[Element]:
        calls.append(f"recover:{page}")
        return [Element(ElementKind.TEXT, "Bozuk katman 99", SourceLocation(page=page))]

    tools = replace(_fake_tools(calls, page_kind=kind), recover_page_text=recover)
    result = ingest_document(path, META, tools, tmp_path)

    assert "reader:[1]" in calls
    assert not any(call.startswith("recover:") for call in calls)  # katmanın metni alınmaz
    assert [chunk.text for chunk in result.chunks] == ["Taranmış sayfa 42 mm"]
    assert result.report.ocr_pages == (1,)
    assert result.report.warnings == ()


def test_report_summarizes_what_was_read(tmp_path: Path) -> None:
    path = tmp_path / "belge.pdf"
    path.write_bytes(b"%PDF-x")

    report = ingest_document(path, META, _fake_tools([], page_kind=PageKind.NONE), tmp_path).report

    assert report.doc_id == "d"
    assert report.page_count == 1
    assert report.page_kinds == {"none": 1}
    assert report.ocr_pages == (1,)
    assert report.uncertain_values == 1
    assert report.chunks_by_kind == {"text": 1}


def test_report_counts_a_heading_value_once_not_in_every_chunk(tmp_path: Path) -> None:
    """Başlıkta belirsiz okunan değer altındaki her parçaya taşınır (doğrulama için); belgenin
    "net okunamadı" sayısı onu bir kez sayar."""
    path = tmp_path / "tarama.pdf"
    path.write_bytes(b"%PDF-x")

    def read_scanned(path: Path, pages: list[int], work: Path, image: Path | None) -> list[Element]:
        location = SourceLocation(page=1)
        heading = Element(
            ElementKind.HEADING,
            "Föy -603186",
            location,
            from_ocr=True,
            ocr_uncertain=("-603186",),
        )
        rows = [
            Element(ElementKind.TABLE_ROW, f"Bel: {n}", location, from_ocr=True)
            for n in (70, 72, 74)
        ]
        # Okuyucu değer taşıyan başlığı metin olarak da yazar (page_reader.page_elements).
        return [heading, replace(heading, kind=ElementKind.TEXT), *rows]

    tools = replace(_fake_tools([], page_kind=PageKind.NONE), read_scanned_pages=read_scanned)
    result = ingest_document(path, META, tools, tmp_path)

    rows = [chunk for chunk in result.chunks if chunk.kind is ChunkKind.TABLE_ROW]
    assert [chunk.ocr_uncertain for chunk in rows] == [("-603186",)] * 3
    assert result.report.uncertain_values == 1


def test_unreadable_document_is_reported_as_a_warning(tmp_path: Path) -> None:
    path = tmp_path / "notlar.txt"
    path.write_text("   \n", encoding="utf-8")

    result = ingest_document(path, META, _fake_tools([]), tmp_path)

    assert result.chunks == ()
    assert "içerik" in result.report.warnings[0]


def test_excel_keeps_no_pdf(tmp_path: Path) -> None:
    import openpyxl

    workbook = openpyxl.Workbook()
    workbook.active.append(["Kolon", "Değer"])
    workbook.active.append(["A", "1"])
    path = tmp_path / "x.xlsx"
    workbook.save(path)

    result = ingest_document(path, META, _fake_tools([]), tmp_path)

    assert result.display_pdf is None
    assert result.chunks[0].location.row == 2


@pytest.mark.parametrize("name", ["a.exe"])
def test_unsupported_file_raises(tmp_path: Path, name: str) -> None:
    from visual_agent.ingest.formats import UnsupportedFormat

    path = tmp_path / name
    path.write_bytes(b"MZ")

    with pytest.raises(UnsupportedFormat):
        ingest_document(path, META, _fake_tools([]), tmp_path)


def test_sql_statement_in_text_becomes_code() -> None:
    elements = [
        Element(ElementKind.TEXT, "ALTER TABLE A RENAME COLUMN B TO C;", SourceLocation(page=1)),
        Element(ElementKind.TEXT, "Select your report from the menu.", SourceLocation(page=1)),
    ]

    promoted = promote_code_elements(elements)

    assert [element.kind for element in promoted] == [ElementKind.CODE, ElementKind.TEXT]


def test_page_header_with_a_code_is_kept_as_identifying_context() -> None:
    assert page_header_identifies("MNT-8598 ölçü föyü")
    assert not page_header_identifies("Şirket Gizli Belgesi")


def test_table_row_context_is_added_to_its_chunk_section() -> None:
    meta = DocumentMeta(doc_id="d", title="Föy", language="en")
    elements = [
        Element(ElementKind.HEADING, "POMs", SourceLocation(page=1)),
        Element(
            ElementKind.TABLE_ROW, "Dim: SL095 | MD: 10 3/4", SourceLocation(page=1), context="Tall"
        ),
        Element(ElementKind.TABLE_ROW, "Dim: SL100 | MD: 7 1/4", SourceLocation(page=1)),
    ]

    chunks = build_chunks(elements, meta)

    assert [chunk.section for chunk in chunks] == ["POMs · Tall", "POMs"]
    # Tablo notu ayrıca saklanır: başlık (POMs) not değildir.
    assert [chunk.table_note for chunk in chunks] == ["Tall", ""]


@pytest.mark.parametrize(
    ("heading", "expected"),
    [
        ('1. Hood crossover should be 7/8"', True),
        ("PNT-1162 ölçü föyü", True),
        ("3. Kurulum ve bakım", False),
        ("a) Genel", False),
        ("CONSTRUCTION/WORKMANSHIP:", False),
    ],
)
def test_headings_carrying_a_value_are_kept_as_text_too(heading: str, expected: bool) -> None:
    assert carries_value(heading) is expected


def test_only_pages_without_a_text_layer_go_to_the_page_reader(tmp_path: Path) -> None:
    path = tmp_path / "karisik.pdf"
    path.write_bytes(b"%PDF-x")
    calls: list[str] = []
    tools = _fake_tools(calls)

    def inspect(path: Path) -> list[PageInfo]:
        return [
            PageInfo(page=1, kind=PageKind.TEXT, chars=500, image_boxes=()),
            PageInfo(page=2, kind=PageKind.NONE, chars=0, image_boxes=(box(),)),
        ]

    result = ingest_document(path, META, replace(tools, inspect_pdf=inspect), tmp_path)

    assert "reader:[2]" in calls
    assert result.report.ocr_pages == (2,)
    scanned = [chunk for chunk in result.chunks if chunk.location.page == 2]
    assert [chunk.text for chunk in scanned] == ["Taranmış sayfa 42 mm"]
    assert all(chunk.from_ocr for chunk in scanned)


def test_unavailable_reader_stops_the_document(
    tmp_path: Path,
) -> None:
    path = tmp_path / "tarama.pdf"
    path.write_bytes(b"%PDF-x")
    calls: list[str] = []

    def unavailable(path: Path, pages: list[int], work: Path, image: Path | None) -> list[Element]:
        raise ReaderUnavailable("okuyucu yok")

    tools = replace(_fake_tools(calls, page_kind=PageKind.NONE), read_scanned_pages=unavailable)

    with pytest.raises(ReaderUnavailable):
        ingest_document(path, META, tools, tmp_path)

    assert not any(call.startswith("parse") for call in calls)


def test_blocks_rejected_by_the_cloud_get_their_own_warning(tmp_path: Path) -> None:
    """Bloğa özgü 4xx devreyi açmaz ama içerik kaybı sessiz kalmaz (kural 3)."""
    path = tmp_path / "tarama.pdf"
    path.write_bytes(b"%PDF-x")

    def reject(path: Path, pages: list[int], work: Path, image: Path | None) -> list[Element]:
        outage = CLOUD_OUTAGE.get()
        assert outage is not None
        outage.rejected_blocks, outage.rejected_status, outage.fallback_blocks = 2, 413, 1
        return []

    tools = replace(_fake_tools([], page_kind=PageKind.NONE), read_scanned_pages=reject)
    warnings = ingest_document(path, META, tools, tmp_path).report.warnings

    assert (
        "2 blok bulutça reddedildi (HTTP 413); Tesseract'la denetlendi ya da şekil bloğu okunmadı."
        in warnings
    )
    assert not any("bulut alınamadı" in warning for warning in warnings)


def test_cloud_outage_is_one_warning_per_document(tmp_path: Path) -> None:
    """Devre kesicinin durumu belge başınadır: bir belgenin kesintisi sonrakine geçmez."""
    path = tmp_path / "tarama.pdf"
    path.write_bytes(b"%PDF-x")
    outages: list[CloudOutage | None] = []

    def cut(path: Path, pages: list[int], work: Path, image: Path | None) -> list[Element]:
        outage = CLOUD_OUTAGE.get()
        outages.append(outage)
        if outage is not None and len(outages) == 1:
            outage.reasons["qwen"] = "ConnectError()"
            outage.fallback_blocks = 3
        return []

    tools = replace(_fake_tools([], page_kind=PageKind.NONE), read_scanned_pages=cut)
    first = ingest_document(path, META, tools, tmp_path)
    second = ingest_document(path, META, tools, tmp_path)

    assert (
        "3 blok Tesseract'la denetlendi; bulut alınamadı (qwen: ConnectError())."
        in first.report.warnings
    )
    assert not any("Tesseract" in warning for warning in second.report.warnings)
    assert outages[0] is not outages[1]


def test_image_file_itself_is_given_to_the_page_reader(tmp_path: Path) -> None:
    path = tmp_path / "foto.jpg"
    path.write_bytes(b"\xff\xd8\xffx")
    calls: list[str] = []

    ingest_document(path, META, _fake_tools(calls, page_kind=PageKind.NONE), tmp_path)

    assert "image:foto.jpg" in calls


def test_pdf_pages_are_rendered_not_read_from_an_image_file(tmp_path: Path) -> None:
    path = tmp_path / "tarama.pdf"
    path.write_bytes(b"%PDF-x")
    calls: list[str] = []

    ingest_document(path, META, _fake_tools(calls, page_kind=PageKind.NONE), tmp_path)

    assert not any(call.startswith("image:") for call in calls)


def _uncertain_heading_page() -> list[Element]:
    page = SourceLocation(page=1)
    return [
        Element(
            ElementKind.HEADING,
            "iGML-6473 ölçü föyü",
            page,
            from_ocr=True,
            ocr_uncertain=("iGML-6473",),
        ),
        Element(
            ElementKind.TABLE_ROW,
            "Beden: M | Etiket kodu: ETK-3392",
            page,
            from_ocr=True,
        ),
    ]


def test_uncertain_heading_value_reaches_the_chunks_of_its_section() -> None:
    """B1, 2. adım: başlık parça değil, bölüm adı olur; belirsiz işareti de parçaya geçmeli."""
    meta = DocumentMeta(doc_id="d", title="föy", language="tr")
    [row] = build_chunks(_uncertain_heading_page(), meta)

    assert row.section == "iGML-6473 ölçü föyü"
    assert row.ocr_uncertain == ("iGML-6473",)


def test_sentence_with_the_uncertain_heading_code_is_hidden_but_the_value_is_shown() -> None:
    meta = DocumentMeta(doc_id="d", title="föy", language="tr")
    [row] = build_chunks(_uncertain_heading_page(), meta)
    sources = {
        1: PromptSource(
            number=1,
            text=row.text,
            context=row.section,
            ocr_uncertain=row.ocr_uncertain,
            from_ocr=True,
            is_table_row=True,
        )
    }

    def check(text: str) -> bool:
        item = ModelItem(text=text, quotes=(Quote(source_no=1, text="Etiket kodu: ETK-3392"),))
        return verify_item(item, sources, "tr").ok

    assert not check("iGML-6473 M beden etiket kodu ETK-3392.")
    assert check("M beden etiket kodu ETK-3392.")


def _steps_while_ingesting(path: Path, tools: IngestTools, work: Path) -> list[str]:
    steps: list[str] = []
    token = INGEST_PROGRESS.set(lambda step, done, total: steps.append(step))
    try:
        ingest_document(path, META, tools, work)
    finally:
        INGEST_PROGRESS.reset(token)
    return steps


def test_ingest_reports_its_steps_in_order(tmp_path: Path) -> None:
    """Arayüzdeki genel çubuk için: hazırlık, metin, parçalama sırayla bildirilir."""
    pdf = tmp_path / "belge.pdf"
    pdf.write_bytes(b"%PDF-x")
    text = tmp_path / "notlar.md"
    text.write_text("# Başlık\n\nMetin.", encoding="utf-8")

    assert _steps_while_ingesting(pdf, _fake_tools([]), tmp_path) == ["prepare", "text", "chunks"]
    assert _steps_while_ingesting(text, _fake_tools([]), tmp_path) == [
        "prepare",
        "text",
        "chunks",
    ]


def _placed(kind: ElementKind, text: str, left: float, top: float, right: float) -> Element:
    box = Box(
        page=1, left=left, top=top, right=right, bottom=top + 9, page_width=612, page_height=792
    )
    return Element(kind, text, SourceLocation(page=1, boxes=(box,)))


_RIGHT_TABLE = [
    _placed(ElementKind.TABLE_ROW, "%: 0-0.99 | Score: 5", 133, 533, 184),
    _placed(ElementKind.TABLE_ROW, "%: 1-1.99 | Score: 4", 133, 546, 184),
]
_LEFT_TABLE = [
    _placed(ElementKind.TABLE_ROW, "%: 95-100 | Score: 5", 42, 533, 98),
    _placed(ElementKind.TABLE_ROW, "%: 90-94.99 | Score: 4", 42, 546, 98),
]


def _sections(elements: list[Element]) -> dict[str, str]:
    meta = DocumentMeta(doc_id="d", title="Belge", language="en")
    return {chunk.text: chunk.section for chunk in build_chunks(elements, meta)}


def test_side_by_side_tables_take_the_heading_above_them() -> None:
    """Yan yana iki tablo: okuma sırası başlıkları önce, sonra sağ tabloyu, sonra sol tabloyu
    verir (docling'in QM s.16'daki sırası). Her satır kendi üstündeki başlığın bölümünde olmalı;
    sağdaki başlık soldaki tablonun satırlarına geçmemeli."""
    elements = [
        _placed(ElementKind.HEADING, "PTH", 45, 487, 70),
        _placed(ElementKind.HEADING, "OQL/SQL", 145, 487, 179),
        *_RIGHT_TABLE,
        *_LEFT_TABLE,
    ]

    sections = _sections(elements)

    assert sections["%: 95-100 | Score: 5"].endswith("PTH")
    assert sections["%: 90-94.99 | Score: 4"].endswith("PTH")
    assert sections["%: 0-0.99 | Score: 5"].endswith("OQL/SQL")


def test_table_without_a_heading_above_it_does_not_take_the_neighbours_heading() -> None:
    """Okuyucu sol tablonun başlığını düşürdü ("PTH"): sol tablo sağdakinin başlığını
    ("OQL/SQL") almaz; sayfadaki genel başlıkta ya da önceki bölümde kalır."""
    general = _placed(ElementKind.HEADING, "Supplier Scorecard", 40, 100, 570)
    right = _placed(ElementKind.HEADING, "OQL/SQL", 145, 487, 179)

    alone = _sections([right, *_RIGHT_TABLE, *_LEFT_TABLE])
    under = _sections([general, right, *_RIGHT_TABLE, *_LEFT_TABLE])

    assert alone["%: 0-0.99 | Score: 5"].endswith("OQL/SQL")
    assert "OQL/SQL" not in alone["%: 95-100 | Score: 5"]
    assert under["%: 90-94.99 | Score: 4"] == "Supplier Scorecard"
    assert under["%: 1-1.99 | Score: 4"].endswith("OQL/SQL")


def test_rows_without_boxes_keep_the_last_heading() -> None:
    """Konum kutusu olmayan öğelerde (Markdown, Excel) bölüm okuma sırasındaki son başlıktır."""
    heading = Element(ElementKind.HEADING, "Ölçüler", SourceLocation(), level=1)
    row = Element(ElementKind.TABLE_ROW, "Bel: 38", SourceLocation())

    assert _sections([heading, row])["Bel: 38"] == "Ölçüler"


def _heading(text: str, level: int | None = None) -> Element:
    return Element(ElementKind.HEADING, text, SourceLocation(page=1), level=level)


def _row(text: str) -> Element:
    return Element(ElementKind.TABLE_ROW, text, SourceLocation(page=1))


def test_headings_without_level_are_siblings() -> None:
    """Düzeyi bilinmeyen başlık öncekinin altına girmez: kopuk parça ("FW") kök olmaz."""
    sections = _sections([_heading("FW"), _row("A: 1"), _heading("POMs"), _row("Bel: 38")])

    assert sections == {"A: 1": "FW", "Bel: 38": "POMs"}


def test_code_carrying_first_heading_stays_the_root() -> None:
    """Karar 0025: kod taşıyan ilk başlık belge başlığıdır; sonraki başlıklar altına girer."""
    root = "SS28-6026412-US-TEE CHART"
    sections = _sections([_heading(root), _heading("BOM"), _row("Kod: BG-1"), _heading(root)])

    assert sections == {"Kod: BG-1": f"{root} · BOM"}


def test_levelled_headings_still_nest() -> None:
    """Düzey kanıtı olan başlıklar (Markdown, Excel) iç içe kalır."""
    elements = [_heading("Kılavuz", 1), _heading("Kurulum", 2), _row("Adım: 1")]

    assert _sections(elements) == {"Adım: 1": "Kılavuz · Kurulum"}
