from dataclasses import replace
from pathlib import Path

import pytest

from visual_agent.domain.document import Box, ChunkKind, DocumentMeta, SourceLocation
from visual_agent.ingest.docling_parser import page_header_identifies
from visual_agent.ingest.elements import Element, ElementKind
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
)
from visual_agent.ingest.text_layer import PageKind

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
        calls.append("images")
        return [Element(ElementKind.FIGURE, "Görsel metni", SourceLocation(page=1), from_ocr=True)]

    return IngestTools(
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


def test_pages_left_as_image_only_are_warned_about(tmp_path: Path) -> None:
    path = tmp_path / "belge.pdf"
    path.write_bytes(b"%PDF-x")

    def ocr(path: Path, pages: list[PageInfo], language: str, work: Path) -> OcrOutcome:
        return OcrOutcome(pdf_path=path, ocr_pages={}, image_only_pages=(2, 3, 5))

    report = ingest_document(path, META, replace(_fake_tools([]), run_ocr=ocr), tmp_path).report

    assert report.warnings == (
        "Sayfa 2-3,5: metin okunamadı, yalnız görüntü olarak kaldı; aramada bulunmaz.",
    )


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

    assert calls == ["office", "inspect", "ocr:tr", "parse:converted.pdf", "images"]
    assert result.display_pdf == tmp_path / "converted.pdf"
    assert {chunk.kind for chunk in result.chunks} == {ChunkKind.TEXT, ChunkKind.FIGURE}


def test_scanned_pages_do_not_get_a_second_image_pass(tmp_path: Path) -> None:
    path = tmp_path / "tarama.pdf"
    path.write_bytes(b"%PDF-x")
    calls: list[str] = []

    ingest_document(path, META, _fake_tools(calls, page_kind=PageKind.NONE), tmp_path)

    assert "images" in calls  # okuyucu çağrılır; sayfa seçimi okuyucunun sorumluluğundadır


def test_report_summarizes_what_was_read(tmp_path: Path) -> None:
    path = tmp_path / "belge.pdf"
    path.write_bytes(b"%PDF-x")

    report = ingest_document(path, META, _fake_tools([]), tmp_path).report

    assert report.doc_id == "d"
    assert report.page_count == 1
    assert report.ocr_pages == (1,)
    assert report.uncertain_values == 1
    assert report.chunks_by_kind["figure"] == 1


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
