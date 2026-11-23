"""Markdown ve Excel okuma kuralları; belgenin hangi kural sürümüyle işlendiği."""

from pathlib import Path

import openpyxl
import pytest

from visual_agent.domain.document import ChunkKind, DocumentMeta, SourceLocation
from visual_agent.ingest.chunking import build_chunks
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.formats import RULES_VERSIONS, InputFormat, is_outdated
from visual_agent.ingest.markdown import parse_markdown
from visual_agent.ingest.pipeline import IngestTools, ingest_document
from visual_agent.ingest.spreadsheet import display_number, parse_workbook

META = DocumentMeta(doc_id="d", title="kilavuz")

GUIDE = """# Ayarlar

**Menü yolu:** Ana menü > Ayarlar
**Bölüm:** 1

## Genel

*Bağlam: Ayarlar › Genel*

### Hafta numaraları

**Açık:** Tarihin yanında hafta numarası gösterilir. Yıldız işareti ‘\\*’ joker karakterdir.

1. `Configure` ekranını açın.
2. [Destek](mailto:destek@ornek.com) ve [kılavuz](http://wiki/kilavuz) sayfasına bakın.

| Alan | Değer |
|---|---|
| Yıl 1 | 2024<br>2025 |
| Yıl 2 | |

```sql
SELECT 1;
```

## Görünüm

Satır sonu
burada.
"""


def _texts(elements: list[Element], kind: ElementKind) -> list[str]:
    return [element.text for element in elements if element.kind is kind]


def test_markdown_headings_keep_their_levels() -> None:
    headings = [
        (element.level, element.text)
        for element in parse_markdown(GUIDE)
        if element.kind is ElementKind.HEADING
    ]

    assert headings == [(1, "Ayarlar"), (2, "Genel"), (3, "Hafta numaraları"), (2, "Görünüm")]


def test_markdown_marks_leave_the_text_but_content_stays() -> None:
    texts = _texts(parse_markdown(GUIDE), ElementKind.TEXT)

    assert texts[0] == "Menü yolu: Ana menü > Ayarlar\nBölüm: 1"
    assert texts[1] == "Bağlam: Ayarlar › Genel"
    assert "joker karakter ‘*’" not in texts[2] and "‘*’ joker karakterdir" in texts[2]
    assert texts[3] == "1. Configure ekranını açın."
    assert texts[4] == (
        "2. Destek (destek@ornek.com) ve kılavuz (http://wiki/kilavuz) sayfasına bakın."
    )
    assert texts[-1] == "Satır sonu\nburada."


def test_link_whose_address_is_its_text_is_not_repeated() -> None:
    texts = _texts(
        parse_markdown("<http://wiki/a> ve [x@y.com](mailto:x@y.com)\n"), ElementKind.TEXT
    )

    assert texts == ["http://wiki/a ve x@y.com"]


def test_markdown_table_rows_carry_their_headers() -> None:
    rows = _texts(parse_markdown(GUIDE), ElementKind.TABLE_ROW)

    assert rows == ["Alan: Yıl 1 | Değer: 2024\n2025", "Alan: Yıl 2"]


def test_markdown_code_block_stays_as_written() -> None:
    assert _texts(parse_markdown(GUIDE), ElementKind.CODE) == ["SELECT 1;"]


def test_markdown_html_that_is_not_a_line_break_is_content() -> None:
    texts = _texts(parse_markdown("Tarih <First week> girilir.\n"), ElementKind.TEXT)

    assert texts == ["Tarih <First week> girilir."]


def test_heading_path_becomes_the_section_and_the_location_of_pageless_chunks() -> None:
    chunks = build_chunks(parse_markdown(GUIDE), META)
    by_text = {chunk.text: chunk for chunk in chunks}

    first = by_text["Menü yolu: Ana menü > Ayarlar\nBölüm: 1"]
    week = next(chunk for chunk in chunks if chunk.text.startswith("Açık:"))
    view = by_text["Satır sonu\nburada."]

    assert first.section == "Ayarlar"
    assert week.section == "Ayarlar · Genel · Hafta numaraları"
    assert week.location == SourceLocation(section="Ayarlar · Genel · Hafta numaraları")
    assert view.section == "Ayarlar · Görünüm"
    assert by_text["Alan: Yıl 2"].kind is ChunkKind.TABLE_ROW


def test_paged_chunks_keep_their_location_without_a_section() -> None:
    elements = [
        Element(ElementKind.HEADING, "Kılavuz", SourceLocation(page=1)),
        Element(ElementKind.TEXT, "Metin", SourceLocation(page=1)),
    ]

    chunk = build_chunks(elements, META)[0]

    assert chunk.section == "Kılavuz"
    assert chunk.location == SourceLocation(page=1)


@pytest.mark.parametrize(
    ("value", "number_format", "shown"),
    [
        (0.12, "0%", "12%"),
        (0.125, "0.0%", "12,5%"),
        (1234.5, '#,##0.00 "TL"', "1.234,50 TL"),
        (1234.5, "#,##0.00\\ [$TL-41F]", "1.234,50"),
        (-5, "#,##0;(#,##0)", "-5"),
        (-5, '#,##0;[Red]"-"#,##0', "-5"),
        (42, "00000", "00042"),
        (1234567, "#,##0", "1.234.567"),
        (100.5, "General", "100,5"),
        (0.1 + 0.2, "General", "0,3"),
        (7, "General", "7"),
        (12345.678, "0.00E+00", "12345,678"),
        (3.25, "# ?/?", "3,25"),
    ],
)
def test_excel_numbers_are_written_as_shown(value: float, number_format: str, shown: str) -> None:
    assert display_number(value, number_format) == shown


def _formula_workbook(path: Path) -> Path:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Hesap"
    sheet.append(["Kalem", "Oran", "Tutar", "İki katı"])
    sheet.append(["Kumaş", 0.12, 1234.5, "=C2*2"])
    sheet["B2"].number_format = "0%"
    sheet["C2"].number_format = '#,##0.00 "TL"'
    target = path / "hesap.xlsx"
    workbook.save(target)
    return target


def test_excel_formula_without_a_saved_value_is_reported(tmp_path: Path) -> None:
    elements, warnings = parse_workbook(_formula_workbook(tmp_path))

    rows = _texts(elements, ElementKind.TABLE_ROW)
    assert rows == ["Kalem: Kumaş | Oran: 12% | Tutar: 1.234,50 TL"]
    assert warnings == ["Hesap sayfası D2: formülün kayıtlı değeri yok, okunamadı."]


def _no_tools() -> IngestTools:
    def unused(*_: object) -> object:
        raise AssertionError("bu biçimde dış araç kullanılmaz")

    return IngestTools(*([unused] * 7))  # type: ignore[arg-type]


def test_report_records_the_format_and_rules_version(tmp_path: Path) -> None:
    path = tmp_path / "kilavuz.md"
    path.write_text(GUIDE, encoding="utf-8")

    report = ingest_document(path, META, _no_tools(), tmp_path).report

    assert report.input_format is not None
    assert report.rules_version == RULES_VERSIONS[report.input_format]
    assert not is_outdated(report.model_dump(mode="json"), "kilavuz.md")


def test_spreadsheet_warnings_reach_the_report(tmp_path: Path) -> None:
    report = ingest_document(_formula_workbook(tmp_path), META, _no_tools(), tmp_path).report

    assert report.warnings == ("Hesap sayfası D2: formülün kayıtlı değeri yok, okunamadı.",)


def _old_report() -> dict[str, object]:
    """Kural sürümü kaydedilmeden önce yazılmış rapor."""
    return {
        "doc_id": "d",
        "page_count": 0,
        "page_kinds": {},
        "ocr_pages": [],
        "uncertain_values": 0,
        "chunks_by_kind": {},
        "warnings": [],
    }


@pytest.mark.parametrize(
    "filename", ["kilavuz.md", "tablo.xlsx", "rapor.sql", "tarama.pdf", "foto.jpg", "belge.docx"]
)
def test_reports_without_a_rules_version_are_outdated(filename: str) -> None:
    assert is_outdated(_old_report(), filename)


def test_word_report_from_the_first_ocr_rules_is_outdated() -> None:
    report = {**_old_report(), "input_format": "office", "rules_version": 1}

    assert is_outdated(report, "belge.docx")


def test_unknown_file_type_is_never_outdated() -> None:
    assert not is_outdated(_old_report(), "eski.bin")


@pytest.mark.parametrize(
    ("page_kinds", "outdated"),
    [({"text": 12}, False), ({"text": 2, "none": 1}, True), ({"scanned": 3}, True)],
)
def test_page_reader_rules_only_outdate_documents_with_scanned_pages(
    page_kinds: dict[str, int], outdated: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Sürüm 7→13 geçişleri sayfa türüne göre eskitir; sürüm 13'e sabitlenerek sınanır.
    monkeypatch.setitem(RULES_VERSIONS, InputFormat.PDF, 13)
    report = {
        **_old_report(),
        "input_format": "pdf",
        "rules_version": 7,
        "page_kinds": page_kinds,
    }

    assert is_outdated(report, "belge.pdf") is outdated


def test_documents_from_before_the_previous_rules_stay_outdated() -> None:
    report = {**_old_report(), "input_format": "pdf", "rules_version": 6, "page_kinds": {"text": 3}}

    assert is_outdated(report, "belge.pdf")


@pytest.mark.parametrize(
    ("version", "page_kinds", "outdated"),
    [
        (8, {"none": 12}, True),  # 9→10: sayfa okuyucusundaki form tabloları değişti
        (9, {"none": 12}, True),
        (12, {"none": 1}, True),  # 12→13: hücre sayısı uyuşmayan tablolar başlıksız
        (12, {"text": 3, "weak": 1}, False),
        (9, {"text": 3, "weak": 1}, False),  # eski OCR yolundaki sayfayı 9→10 etkilemez
        (9, {"text": 3}, False),
        (8, {"text": 3, "weak": 1}, True),
        (7, {"text": 3, "weak": 1}, True),
        (7, {"text": 3}, False),
    ],
)
def test_removing_cell_rereading_only_outdates_documents_read_by_the_old_ocr(
    version: int, page_kinds: dict[str, int], outdated: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Sürüm 7→13 geçişleri sayfa türüne göre eskitir; sürüm 13'e sabitlenerek sınanır.
    monkeypatch.setitem(RULES_VERSIONS, InputFormat.PDF, 13)
    report = {
        **_old_report(),
        "input_format": "pdf",
        "rules_version": version,
        "page_kinds": page_kinds,
    }

    assert is_outdated(report, "belge.pdf") is outdated


def test_docling_table_guards_outdate_every_pdf_and_office_document() -> None:
    """14→15 gömülü görsellerin ikinci okumasını değiştirdi (metin sayfası): her belge eskir."""
    for input_format, name in (("pdf", "belge.pdf"), ("office", "belge.docx")):
        report = {
            **_old_report(),
            "input_format": input_format,
            "rules_version": 14,
            "page_kinds": {"text": 3},
        }
        assert is_outdated(report, name)


@pytest.mark.parametrize(
    ("page_kinds", "outdated"),
    [({"text": 3}, True), ({"text": 2, "weak": 1}, True), ({"scanned": 3}, False)],
)
def test_embedded_image_count_fix_outdates_only_documents_with_text_pages(
    page_kinds: dict[str, int], outdated: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """20→21 yalnız metinli sayfadaki gömülü görsellerin ikinci okumasını değiştirdi."""
    monkeypatch.setitem(RULES_VERSIONS, InputFormat.PDF, 21)
    report = {**_old_report(), "input_format": "pdf", "rules_version": 20, "page_kinds": page_kinds}

    assert is_outdated(report, "belge.pdf") is outdated


def test_row_without_any_labels_marks_its_empty_cells() -> None:
    from visual_agent.ingest.elements import labeled_row

    assert labeled_row(["", "", ""], ["Supplier Request Round", "", "Fleece"]) == (
        "Supplier Request Round | (boş) | Fleece"
    )
    assert (
        labeled_row(["Etiket", "", "Kumaş"], ["Round", "", "Fleece"])
        == "Etiket: Round | Kumaş: Fleece"
    )


@pytest.mark.parametrize(
    ("page_kinds", "outdated"), [({"text": 3}, False), ({"text": 2, "none": 1}, True)]
)
def test_uncertain_heading_rule_only_outdates_documents_with_ocr_pages(
    page_kinds: dict[str, int], outdated: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(RULES_VERSIONS, InputFormat.PDF, 16)
    report = {**_old_report(), "input_format": "pdf", "rules_version": 15, "page_kinds": page_kinds}

    assert is_outdated(report, "belge.pdf") is outdated


@pytest.mark.parametrize(
    ("kinds", "outdated"),
    [({"text": 2}, True), ({"none": 3, "weak": 1}, True), ({"none": 29}, False)],
)
def test_legacy_ocr_rules_outdate_only_documents_the_old_path_could_read(
    kinds: dict[str, int], outdated: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """19→20 (karar 0022): eski OCR yolu yalnız metinli, zayıf ya da taranmış katmanlı sayfada
    çalışır; tamamı okuyucudan geçen taranmış belge yeniden işlenmez."""
    monkeypatch.setitem(RULES_VERSIONS, InputFormat.PDF, 20)
    report = {"input_format": "pdf", "rules_version": 19, "page_kinds": kinds}

    assert is_outdated(report, "belge.pdf") is outdated


@pytest.mark.parametrize(
    ("kinds", "outdated"),
    [({"text": 2}, True), ({"scanned": 1}, True), ({"weak": 1}, True), ({"none": 29}, False)],
)
def test_removing_the_legacy_ocr_path_does_not_outdate_scanned_sheets(
    kinds: dict[str, int], outdated: bool
) -> None:
    """23→24 (karar 0028): tamamı okuyucudan geçen taranmış föyler yeniden okunmaz."""
    report = {"input_format": "pdf", "rules_version": 23, "page_kinds": kinds}

    assert is_outdated(report, "belge.pdf") is outdated


def _workbook(path: Path, rows: list[list[str]]) -> Path:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Notlar"
    for row in rows:
        sheet.append(row)
    target = path / "notlar.xlsx"
    workbook.save(target)
    return target


def _rows(path: Path) -> list[str]:
    elements, _ = parse_workbook(path)
    return [element.text for element in elements if element.kind is ElementKind.TABLE_ROW]


def test_sheet_with_a_single_filled_row_keeps_its_text(tmp_path: Path) -> None:
    """Yalnız A1'de not olan sayfa: başlık sanılıp metin kaybolmuyordu (kural 3)."""
    assert _rows(_workbook(tmp_path, [["Not: tork 12 Nm"]])) == ["Not: tork 12 Nm"]


def test_header_without_rows_below_is_written_as_a_row(tmp_path: Path) -> None:
    assert _rows(_workbook(tmp_path, [["Kod", "", "Tork"]])) == ["Kod | (boş) | Tork"]


def test_header_with_rows_below_still_labels_them(tmp_path: Path) -> None:
    rows = _rows(_workbook(tmp_path, [["Kod", "Tork"], ["PNT-1", "12"], ["PNT-2", "8"]]))

    assert rows == ["Kod: PNT-1 | Tork: 12", "Kod: PNT-2 | Tork: 8"]


def test_single_column_sheet_writes_each_cell_as_its_own_unlabeled_row(tmp_path: Path) -> None:
    """Tek sütunlu not sayfası: ilk not ikincinin etiketi olmaz (ürün sahibi kararı)."""
    rows = _rows(_workbook(tmp_path, [["Not: tork 12 Nm"], ["Not: sıkma 8 Nm"], [""], ["Son not"]]))

    assert rows == ["Not: tork 12 Nm", "Not: sıkma 8 Nm", "Son not"]


def test_note_sheet_in_another_column_or_merged_cells_is_still_single_column(
    tmp_path: Path,
) -> None:
    """Notlar B sütununda ya da satır satır A:D'ye birleştirilmiş: her not ayrı, işaretsiz."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Notlar"
    sheet["B1"], sheet["B2"] = "Not 1", "Not 2"
    sheet["A4"], sheet["A5"] = "Not 3", "Not 4"
    sheet.merge_cells("A4:D4")
    sheet.merge_cells("A5:D5")
    target = tmp_path / "notlar.xlsx"
    workbook.save(target)

    assert _rows(target) == ["Not 1", "Not 2", "Not 3", "Not 4"]
