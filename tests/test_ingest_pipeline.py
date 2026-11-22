from dataclasses import replace
from pathlib import Path

import pytest

from visual_agent.domain.answer import ModelItem, PromptSource, Quote
from visual_agent.domain.document import Box, ChunkKind, DocumentMeta, SourceLocation
from visual_agent.domain.result import Hit
from visual_agent.generation.sources import to_prompt_sources
from visual_agent.ingest.chunking import build_chunks
from visual_agent.ingest.docling_parser import page_header_identifies
from visual_agent.ingest.elements import Element, ElementKind, carries_value
from visual_agent.ingest.external import ReaderUnavailable
from visual_agent.ingest.images import (
    OcrSegment,
    group_lines,
    image_skip_reason,
    lines_to_elements,
)
from visual_agent.ingest.pipeline import (
    IngestTools,
    OcrOutcome,
    PageInfo,
    annotate_ocr_pages,
    ingest_document,
    pages_missing_text,
    promote_code_elements,
    with_images_in_place,
)
from visual_agent.ingest.text_layer import PageKind
from visual_agent.verification.answer import verify_item

META = DocumentMeta(doc_id="d", title="Belge")


def segment(text: str, left: float, top: float) -> OcrSegment:
    return OcrSegment(text=text, left=left, top=top, right=left + 40, bottom=top + 10)


def box(page: int = 1) -> Box:
    return Box(page=page, left=0, top=0, right=100, bottom=20, page_width=600, page_height=800)


def test_segments_on_the_same_height_form_one_ordered_line() -> None:
    lines = group_lines([segment("B", 80, 12), segment("A", 10, 10), segment("C", 10, 50)])

    assert [[item.text for item in line] for line in lines] == [["A", "B"], ["C"]]


def test_consistent_columns_become_table_rows_with_headers() -> None:
    lines = group_lines(
        [
            segment("Kolon", 10, 10),
            segment("Uzunluk", 100, 10),
            segment("DEPO_KODU", 10, 40),
            segment("59", 100, 40),
        ]
    )

    elements = lines_to_elements(lines, box())

    assert [element.kind for element in elements] == [ElementKind.TABLE_ROW]
    assert elements[0].text == "Kolon: DEPO_KODU | Uzunluk: 59"
    assert elements[0].from_ocr


def test_lines_without_columns_stay_as_text() -> None:
    lines = group_lines([segment("Birinci satır", 10, 10), segment("İkinci satır", 10, 40)])

    elements = lines_to_elements(lines, box())

    assert [element.text for element in elements] == ["Birinci satır", "İkinci satır"]
    assert {element.kind for element in elements} == {ElementKind.FIGURE}


def test_ocr_page_elements_are_marked_and_uncertain_tokens_attached() -> None:
    location = SourceLocation(page=2)
    elements = [
        Element(ElementKind.TEXT, "Değer 12,5 cm", location),
        Element(ElementKind.TEXT, "Değer 40 cm", SourceLocation(page=3)),
    ]

    marked = annotate_ocr_pages(elements, {2: ("12,5",)})

    assert marked[0].from_ocr and marked[0].ocr_uncertain == ("12,5",)
    assert not marked[1].from_ocr
    assert marked[0].legacy_ocr and not marked[1].legacy_ocr


def test_legacy_ocr_mark_reaches_the_chunk_and_reader_elements_stay_unmarked() -> None:
    """Karar 0022: eski OCR yolunun (gömülü görsel, ocrmypdf) parçaları işaretlidir; sayfa
    okuyucusundan gelen öğe (`ocr_checked`) eski yol sayılmaz."""
    image_row = lines_to_elements([[segment("Görsel satırı", 0, 0)]], box())[0]
    read = Element(
        ElementKind.TABLE_ROW, "Kod: BL010", SourceLocation(page=2), from_ocr=True, ocr_checked=True
    )
    reader_row = annotate_ocr_pages([read], {2: ()})[0]

    chunks = build_chunks([image_row, reader_row], DocumentMeta(doc_id="d", title="Belge"))

    assert [chunk.legacy_ocr for chunk in chunks] == [True, False]
    assert all(chunk.from_ocr for chunk in chunks)


def test_legacy_ocr_mark_survives_splitting_merging_and_reaches_the_prompt_source() -> None:
    """ocrmypdf sayfasının düz metni bölünür ve birleşir; işaret her parçada ve modele giden
    kaynakta kalmalı."""
    page = SourceLocation(page=1)
    long_text = Element(ElementKind.TEXT, "Uzun cümle sonu. " * 80, page, legacy_ocr=True)
    digital = Element(ElementKind.TEXT, "Dijital satır.", SourceLocation(page=2))
    read = Element(ElementKind.TEXT, "Okunan satır.", SourceLocation(page=2), legacy_ocr=True)

    chunks = build_chunks([long_text, digital, read], DocumentMeta(doc_id="d", title="Belge"))

    assert len(chunks) > 2 and all(chunk.legacy_ocr for chunk in chunks)
    hits = [Hit(chunk=chunk, score=1.0) for chunk in chunks]
    assert all(source.legacy_ocr for source in to_prompt_sources(hits, lambda _: "tr").values())


def test_cell_checked_table_rows_keep_their_own_uncertain_values() -> None:
    """Hücre düzeyinde doğrulanan satıra sayfanın iki okuma karşılaştırması eklenmez."""
    location = SourceLocation(page=2)
    elements = [
        Element(ElementKind.TABLE_ROW, "XS: 27 1/2 | SM: 28", location, ocr_checked=True),
        Element(ElementKind.TABLE_ROW, "XS: 30", location, ocr_uncertain=("30",), ocr_checked=True),
    ]

    marked = annotate_ocr_pages(elements, {2: ("28", "27")})

    assert marked[0].ocr_uncertain == ()
    assert marked[1].ocr_uncertain == ("30",)


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

    def ocr(path: Path, pages: list[PageInfo], language: str, work: Path) -> OcrOutcome:
        calls.append(f"ocr:{language}")
        return OcrOutcome(pdf_path=path, ocr_pages={1: ("99",)})

    def parse(path: Path) -> list[Element]:
        calls.append(f"parse:{path.name}")
        return [
            Element(ElementKind.HEADING, "Başlık", SourceLocation(page=1)),
            Element(ElementKind.TEXT, "Değer 99 cm " * 40, SourceLocation(page=1, boxes=(box(),))),
        ]

    def images(path: Path, pages: list[PageInfo], language: str) -> list[Element]:
        calls.append(f"images:{language}")
        return [Element(ElementKind.FIGURE, "Görsel metni", SourceLocation(page=1), from_ocr=True)]

    def read_scanned(path: Path, pages: list[int], work: Path, image: Path | None) -> list[Element]:
        calls.append(f"image:{image.name}") if image is not None else None
        calls.append(f"reader:{pages}")
        return [
            Element(
                ElementKind.TEXT,
                "Taranmış sayfa 42 mm",
                SourceLocation(page=page),
                from_ocr=True,
                ocr_checked=True,
            )
            for page in pages
        ]

    return IngestTools(
        read_scanned_pages=read_scanned,
        office_to_pdf=office_to_pdf,
        legacy_spreadsheet_to_xlsx=lambda path, work: path,
        image_to_pdf=image_to_pdf,
        inspect_pdf=inspect,
        run_ocr=ocr,
        parse_pdf=parse,
        read_embedded_images=images,
        recover_page_text=lambda path, page: [],
        skipped_image_warnings=lambda pages: [],
    )


def test_skipped_images_are_listed_in_the_report(tmp_path: Path) -> None:
    path = tmp_path / "belge.pdf"
    path.write_bytes(b"%PDF-x")
    warning = "Sayfa 1: görsel okunmadı (kısa kenarı 17 pt, en az 50 pt gerekir)."
    tools = replace(_fake_tools([]), skipped_image_warnings=lambda pages: [warning])

    report = ingest_document(path, META, tools, tmp_path).report

    assert report.warnings == (warning,)


def _image_box(width: float, height: float) -> Box:
    return Box(
        page=1,
        left=0,
        top=0,
        right=width,
        bottom=height,
        page_width=600,
        page_height=800,
    )


def test_image_with_a_short_side_is_skipped_with_its_size() -> None:
    reason = image_skip_reason(_image_box(300, 20), 0.0, 50.0)

    assert reason == "kısa kenarı 20 pt, en az 50 pt gerekir"


def test_image_with_a_small_area_is_skipped_with_its_ratio() -> None:
    reason = image_skip_reason(_image_box(60, 60), 0.02, 50.0)

    assert reason == "alanı sayfanın %0,8 kadarı, en az %2 gerekir"


def test_image_at_the_limits_is_read() -> None:
    assert image_skip_reason(_image_box(192, 50), 0.02, 50.0) is None


def test_word_file_goes_through_pdf_and_embedded_image_reading(tmp_path: Path) -> None:
    path = tmp_path / "belge.docx"
    path.write_bytes(b"PK\x03\x04x")
    calls: list[str] = []

    result = ingest_document(path, META, _fake_tools(calls), tmp_path)

    assert calls == ["office", "inspect", "ocr:tr", "parse:converted.pdf", "images:tr"]
    assert result.display_pdf == tmp_path / "converted.pdf"
    assert {chunk.kind for chunk in result.chunks} == {ChunkKind.TEXT, ChunkKind.FIGURE}


def test_scanned_pages_do_not_get_a_second_image_pass(tmp_path: Path) -> None:
    path = tmp_path / "tarama.pdf"
    path.write_bytes(b"%PDF-x")
    calls: list[str] = []

    ingest_document(path, META, _fake_tools(calls, page_kind=PageKind.NONE), tmp_path)

    # Okuyucu çağrılır; sayfa seçimi okuyucunun sorumluluğundadır.
    assert any(call.startswith("images:") for call in calls)


def test_report_summarizes_what_was_read(tmp_path: Path) -> None:
    path = tmp_path / "belge.pdf"
    path.write_bytes(b"%PDF-x")

    report = ingest_document(path, META, _fake_tools([]), tmp_path).report

    assert report.doc_id == "d"
    assert report.page_count == 1
    assert report.ocr_pages == (1,)
    assert report.uncertain_values == 1
    assert report.chunks_by_kind["figure"] == 1


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
            ocr_checked=True,
            ocr_uncertain=("-603186",),
        )
        rows = [
            Element(ElementKind.TABLE_ROW, f"Bel: {n}", location, from_ocr=True, ocr_checked=True)
            for n in (70, 72, 74)
        ]
        return [heading, *rows]

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


def test_uncertain_token_matches_only_whole_values() -> None:
    elements = [
        Element(ElementKind.TEXT, "İç paça 74,5 cm", SourceLocation(page=1)),
        Element(ElementKind.TEXT, "Toplam 4 adet", SourceLocation(page=1)),
    ]

    marked = annotate_ocr_pages(elements, {1: ("4",)})

    assert marked[0].ocr_uncertain == ()
    assert marked[1].ocr_uncertain == ("4",)


def test_image_table_aligns_rows_when_a_header_cell_was_not_read() -> None:
    lines = group_lines(
        [
            segment("Tablo", 10, 10),
            segment("Uzunluk", 300, 10),
            segment("KALEM", 10, 40),
            segment("VARCHAR", 150, 40),
            segment("19", 300, 40),
            segment("KALEM", 10, 70),
            segment("VARCHAR", 150, 70),
            segment("59", 300, 70),
        ]
    )

    elements = lines_to_elements(lines, box())

    assert [element.kind for element in elements] == [ElementKind.TABLE_ROW] * 2
    assert elements[0].text == "Tablo: KALEM | VARCHAR | Uzunluk: 19"


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


def test_pages_without_a_text_layer_go_to_the_page_reader_not_to_ocr(tmp_path: Path) -> None:
    path = tmp_path / "karisik.pdf"
    path.write_bytes(b"%PDF-x")
    calls: list[str] = []
    ocr_pages: list[int] = []
    tools = _fake_tools(calls)

    def inspect(path: Path) -> list[PageInfo]:
        return [
            PageInfo(page=1, kind=PageKind.TEXT, chars=500, image_boxes=()),
            PageInfo(page=2, kind=PageKind.NONE, chars=0, image_boxes=(box(),)),
        ]

    def ocr(path: Path, pages: list[PageInfo], language: str, work: Path) -> OcrOutcome:
        ocr_pages.extend(page.page for page in pages)
        return OcrOutcome(pdf_path=path, ocr_pages={})

    result = ingest_document(path, META, replace(tools, inspect_pdf=inspect, run_ocr=ocr), tmp_path)

    assert "reader:[2]" in calls
    assert ocr_pages == [1]
    assert result.report.ocr_pages == (2,)
    scanned = [chunk for chunk in result.chunks if chunk.location.page == 2]
    assert [chunk.text for chunk in scanned] == ["Taranmış sayfa 42 mm"]
    assert all(chunk.from_ocr for chunk in scanned)


def test_unavailable_reader_stops_the_document_without_falling_back_to_ocr(
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

    assert not any(call.startswith(("ocr", "parse")) for call in calls)


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
            ocr_checked=True,
        ),
        Element(
            ElementKind.TABLE_ROW,
            "Beden: M | Etiket kodu: ETK-3392",
            page,
            from_ocr=True,
            ocr_checked=True,
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


def test_uncertain_value_in_the_row_context_is_marked_on_the_docling_path() -> None:
    row = Element(
        ElementKind.TABLE_ROW,
        "Beden: M | Etiket kodu: ETK-3392",
        SourceLocation(page=2),
        context="GML-6473 ölçü föyü",
    )

    [marked] = annotate_ocr_pages([row], {2: ("GML-6473",)})

    assert marked.ocr_uncertain == ("GML-6473",)


def _at(kind: ElementKind, text: str, page: int, top: float) -> Element:
    at = Box(
        page=page, left=0, top=top, right=100, bottom=top + 10, page_width=600, page_height=800
    )
    return Element(kind, text, SourceLocation(page=page, boxes=(at,)))


def test_embedded_image_rows_land_in_the_section_where_the_image_is() -> None:
    """B5: iki ürünlü sayfada görseldeki tablo kendi ürününün bölümünde kalır (önceden sayfanın
    sonuna, yani son başlığın bölümüne ekleniyordu)."""
    page = [
        _at(ElementKind.HEADING, "PNT-1162 ölçü föyü", 1, 10),
        _at(ElementKind.TEXT, "Bel ölçüleri aşağıda.", 1, 30),
        _at(ElementKind.HEADING, "CKT-7308 ölçü föyü", 1, 400),
        _at(ElementKind.TEXT, "Kalça ölçüleri aşağıda.", 1, 420),
    ]
    image_row = _at(ElementKind.TABLE_ROW, "Bel | M: 40,5", 1, 120)
    next_page = _at(ElementKind.TEXT, "İkinci sayfa", 2, 5)

    placed = with_images_in_place([*page, next_page], [image_row])
    chunks = build_chunks(placed, DocumentMeta(doc_id="d", title="föy", language="tr"))

    row = next(chunk for chunk in chunks if chunk.text == "Bel | M: 40,5")
    assert row.section == "PNT-1162 ölçü föyü"
    assert [element.text for element in placed if element is not image_row] == [
        element.text for element in [*page, next_page]
    ]
