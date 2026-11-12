"""Markdown ve Excel okuma kuralları; belgenin hangi kural sürümüyle işlendiği."""

from pathlib import Path

import openpyxl
import pytest

from visual_agent.domain.document import ChunkKind, DocumentMeta, SourceLocation
from visual_agent.ingest.chunking import build_chunks
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.formats import RULES_VERSIONS, is_outdated
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

    return IngestTools(*([unused] * 9))  # type: ignore[arg-type]


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
    ("filename", "outdated"),
    [("kilavuz.md", True), ("tablo.xlsx", True), ("rapor.sql", True), ("belge.pdf", False)],
)
def test_old_reports_are_outdated_only_where_the_rules_changed(
    filename: str, outdated: bool
) -> None:
    assert is_outdated(_old_report(), filename) is outdated


def test_unknown_file_type_is_never_outdated() -> None:
    assert not is_outdated(_old_report(), "eski.bin")
