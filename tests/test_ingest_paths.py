from pathlib import Path

import openpyxl
import pytest

from visual_agent.catalog.identifiers import build_identifier_index
from visual_agent.domain.document import Chunk, ChunkKind, DocumentMeta, SourceLocation
from visual_agent.ingest.chunking import CHUNK_MAX_CHARS, build_chunks
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.formats import InputFormat, UnsupportedFormat, detect_format
from visual_agent.ingest.plain_text import parse_plain_text
from visual_agent.ingest.spreadsheet import parse_workbook

META = DocumentMeta(doc_id="d1", title="Ölçü föyü")


def _workbook(path: Path) -> Path:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Ölçüler"
    sheet["A1"] = "PNT-4417 ölçü föyü"
    sheet["B2"] = "Beden"
    sheet.merge_cells("B2:C2")
    for column, header in enumerate(("Ölçü noktası", "S", "M", "Tolerans"), start=1):
        sheet.cell(3, column, header)
    for column, value in enumerate(("İç paça", "74,5", "76,5", "1,0"), start=1):
        sheet.cell(4, column, value)
    for column, cell_value in enumerate(("Dış paça", 100.5, 102, "1,0"), start=1):
        sheet.cell(5, column, cell_value)
    sheet.cell(6, 1, "Yorum")
    sheet.cell(6, 2, "ortak değer")
    sheet.merge_cells("B6:C6")
    other = workbook.create_sheet("Etiketler")
    other.append(["Beden", "Etiket kodu"])
    other.append(["S", "ETK-1000"])
    target = path / "kitap.xlsx"
    workbook.save(target)
    return target


def _rows(elements: list[Element]) -> list[Element]:
    return [element for element in elements if element.kind is ElementKind.TABLE_ROW]


def test_excel_rows_keep_their_real_address_and_headers(tmp_path: Path) -> None:
    rows = _rows(parse_workbook(_workbook(tmp_path))[0])

    assert rows[0].location == SourceLocation(sheet="Ölçüler", row=4)
    assert rows[0].text == "Ölçü noktası: İç paça | Beden S: 74,5 | Beden M: 76,5 | Tolerans: 1,0"


def test_excel_general_numbers_are_written_as_shown(tmp_path: Path) -> None:
    assert "Beden S: 100,5" in _rows(parse_workbook(_workbook(tmp_path))[0])[1].text


def test_excel_merged_data_cell_applies_to_every_column(tmp_path: Path) -> None:
    text = _rows(parse_workbook(_workbook(tmp_path))[0])[2].text

    assert "Beden S: ortak değer" in text and "Beden M: ortak değer" in text


def test_excel_title_above_header_is_available_as_section(tmp_path: Path) -> None:
    headings = [
        element
        for element in parse_workbook(_workbook(tmp_path))[0]
        if element.kind is ElementKind.HEADING
    ]

    assert "PNT-4417 ölçü föyü" in headings[0].text
    assert "Ölçüler" in headings[0].text


def test_excel_every_sheet_is_read(tmp_path: Path) -> None:
    rows = _rows(parse_workbook(_workbook(tmp_path))[0])

    assert rows[-1].location == SourceLocation(sheet="Etiketler", row=2)
    assert rows[-1].text == "Beden: S | Etiket kodu: ETK-1000"


def test_sql_file_becomes_code_with_comment_as_heading(tmp_path: Path) -> None:
    path = tmp_path / "rapor.sql"
    path.write_text("-- Aylık ciro\nSELECT SUM(TUTAR)\nFROM FATURA;\n", encoding="utf-8")

    elements = parse_plain_text(path, InputFormat.SQL)

    assert [element.kind for element in elements] == [ElementKind.HEADING, ElementKind.CODE]
    assert elements[1].text == "SELECT SUM(TUTAR)\nFROM FATURA;"


def test_text_file_is_split_into_paragraphs(tmp_path: Path) -> None:
    path = tmp_path / "notlar.txt"
    path.write_text("Birinci paragraf.\n\nİkinci paragraf.\n", encoding="utf-8")

    assert [e.text for e in parse_plain_text(path, InputFormat.TEXT)] == [
        "Birinci paragraf.",
        "İkinci paragraf.",
    ]


@pytest.mark.parametrize(
    ("name", "content", "expected"),
    [
        ("a.pdf", b"%PDF-1.7 rest", InputFormat.PDF),
        ("a.sql", b"SELECT 1;", InputFormat.SQL),
        ("a.txt", b"metin", InputFormat.TEXT),
        ("a.docx", b"PK\x03\x04data", InputFormat.OFFICE),
        ("a.pptx", b"PK\x03\x04data", InputFormat.OFFICE),
        ("a.xlsx", b"PK\x03\x04data", InputFormat.SPREADSHEET),
        ("a.JPG", b"\xff\xd8\xffdata", InputFormat.IMAGE),
        ("a.png", b"\x89PNG\r\n\x1a\ndata", InputFormat.IMAGE),
    ],
)
def test_detect_format(tmp_path: Path, name: str, content: bytes, expected: InputFormat) -> None:
    path = tmp_path / name
    path.write_bytes(content)

    assert detect_format(path) is expected


@pytest.mark.parametrize(
    ("name", "content"),
    [("a.exe", b"MZ"), ("a.pdf", b"not a pdf"), ("a.xlsx", b"plain text")],
)
def test_unknown_or_mislabeled_file_is_rejected_with_a_reason(
    tmp_path: Path, name: str, content: bytes
) -> None:
    path = tmp_path / name
    path.write_bytes(content)

    with pytest.raises(UnsupportedFormat, match=name):
        detect_format(path)


def element(kind: ElementKind, text: str, page: int = 1) -> Element:
    return Element(kind=kind, text=text, location=SourceLocation(page=page))


def test_heading_sets_section_of_following_chunks() -> None:
    chunks = build_chunks(
        [element(ElementKind.HEADING, "Kurulum"), element(ElementKind.TEXT, "Fişi takın.")], META
    )

    assert len(chunks) == 1
    assert chunks[0].section == "Kurulum"
    assert chunks[0].embed_text == "Ölçü föyü | Kurulum\nFişi takın."


def test_section_keeps_the_document_heading_as_context() -> None:
    chunks = build_chunks(
        [
            element(ElementKind.HEADING, "PNT-4417 ölçü föyü"),
            element(ElementKind.HEADING, "Ölçü tablosu"),
            element(ElementKind.TABLE_ROW, "Bel: 38,0"),
        ],
        META,
    )

    assert chunks[0].section == "PNT-4417 ölçü föyü · Ölçü tablosu"


def test_paragraphs_merge_up_to_the_limit_on_the_same_page() -> None:
    long_text = "kelime " * 60
    chunks = build_chunks(
        [element(ElementKind.TEXT, text) for text in (long_text, long_text, long_text)], META
    )

    assert len(chunks) == 2
    assert all(len(chunk.text) <= CHUNK_MAX_CHARS for chunk in chunks)


def test_table_row_and_code_are_never_merged_or_split() -> None:
    code = "SELECT " + "A, " * 500 + "B FROM T;"
    chunks = build_chunks(
        [
            element(ElementKind.TEXT, "Önce"),
            element(ElementKind.TABLE_ROW, "A: 1"),
            element(ElementKind.TABLE_ROW, "A: 2"),
            element(ElementKind.CODE, code),
        ],
        META,
    )

    assert [chunk.kind for chunk in chunks] == [
        ChunkKind.TEXT,
        ChunkKind.TABLE_ROW,
        ChunkKind.TABLE_ROW,
        ChunkKind.CODE,
    ]
    assert chunks[-1].text == code


def test_overlong_paragraph_is_split_at_sentence_boundaries() -> None:
    text = " ".join(f"Bu {index}. cümle biraz uzunca yazılmış bir cümledir." for index in range(60))

    chunks = build_chunks([element(ElementKind.TEXT, text)], META)

    assert len(chunks) > 1
    assert all(len(chunk.text) <= CHUNK_MAX_CHARS for chunk in chunks)
    assert all(chunk.text.endswith(".") for chunk in chunks)


def test_chunk_ids_are_stable_and_unique() -> None:
    elements = [element(ElementKind.TABLE_ROW, "A: 1"), element(ElementKind.TABLE_ROW, "A: 1")]

    first, second = build_chunks(elements, META), build_chunks(elements, META)

    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
    assert len({chunk.chunk_id for chunk in first}) == 2


def test_merging_paragraphs_keeps_ocr_uncertain_tokens() -> None:
    uncertain = Element(
        kind=ElementKind.TEXT,
        text="Değer 12,5.",
        location=SourceLocation(page=1),
        from_ocr=True,
        ocr_uncertain=("12,5",),
    )

    chunks = build_chunks([element(ElementKind.TEXT, "Önce."), uncertain], META)

    assert chunks[0].ocr_uncertain == ("12,5",)
    assert chunks[0].from_ocr


def _chunk(chunk_id: str, doc_id: str, text: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id=doc_id,
        kind=ChunkKind.TEXT,
        text=text,
        title="t",
        location=SourceLocation(),
    )


def test_identifier_index_finds_exact_codes_within_scope() -> None:
    index = build_identifier_index(
        [
            _chunk("c1", "a", "Hata E050 görülür."),
            _chunk("c2", "b", "Hata E050 ve E05 görülür."),
        ]
    )

    assert index.lookup("E050") == ("c1", "c2")
    assert index.lookup("e050", doc_ids=("a",)) == ("c1",)
    assert index.lookup("E05") == ("c2",)
    assert index.lookup("E999") == ()
    assert index.documents_with("E050") == ("a", "b")
