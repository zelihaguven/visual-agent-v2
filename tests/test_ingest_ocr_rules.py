import pytest

from visual_agent.ingest.pdf_tables import TableCell, group_table_rows
from visual_agent.ingest.text_layer import PageKind, classify_page, junk_score, quality_score
from visual_agent.ingest.two_reading import (
    LayerChoice,
    choose_layer,
    page_ranges,
    unconfirmed_tokens,
)


@pytest.mark.parametrize(
    ("chars", "cover", "score", "expected"),
    [
        (0, 0.0, 0.0, PageKind.NONE),
        (10, 0.9, 0.0, PageKind.NONE),
        (10, 0.1, 1.0, PageKind.TEXT),
        (500, 0.1, 0.5, PageKind.WEAK),
        (500, 0.9, 1.0, PageKind.SCANNED),
        (500, 0.1, 1.0, PageKind.TEXT),
    ],
)
def test_classify_page(chars: int, cover: float, score: float, expected: PageKind) -> None:
    assert classify_page(chars, cover, score) is expected


def test_quality_penalizes_letter_spaced_text() -> None:
    assert quality_score("C a r d f l a t k u m a ş") < quality_score("Cardflat kumaş ölçüsü")


def test_quality_accepts_technical_codes() -> None:
    assert quality_score("LSd-1 3/16-inch 230psi değer") == 1.0


def test_empty_text_scores_zero() -> None:
    assert quality_score("") == 0.0
    assert junk_score("") == 0.0


@pytest.mark.parametrize("junk", ["NNN", "RWQQN", "ıııııuu", "AWK}", "JopurpAo"])
def test_junk_score_detects_ocr_noise(junk: str) -> None:
    assert junk_score(junk) == 0.0


@pytest.mark.parametrize("word", ["III", "lbs", "NSN", "12,5", "E050"])
def test_junk_score_accepts_real_tokens(word: str) -> None:
    assert junk_score(word) == 1.0


@pytest.mark.parametrize(
    ("kind", "old", "new", "expected"),
    [
        (PageKind.NONE, 0.0, 0.95, LayerChoice.NEW),
        (PageKind.NONE, 0.0, 0.4, LayerChoice.IMAGE_ONLY),
        (PageKind.SCANNED, 0.95, 0.5, LayerChoice.OLD),
        (PageKind.SCANNED, 0.95, 0.94, LayerChoice.NEW),
        (PageKind.WEAK, 0.5, 0.9, LayerChoice.NEW),
    ],
)
def test_choose_layer(kind: PageKind, old: float, new: float, expected: LayerChoice) -> None:
    assert choose_layer(kind, old, new) is expected


def test_page_ranges_compacts_pages() -> None:
    assert page_ranges([1, 2, 3, 7, 9, 10]) == "1-3,7,9-10"


@pytest.mark.parametrize(
    ("primary", "second", "expected"),
    [
        ("Değer 12,5 cm", "Değer 12,5 cm", []),
        ("Değer 112 cm", "Değer /12 cm", []),
        ("40lbs yük", "40 lbs yük", []),
        ("43-3/8 ölçü", "43.3/8 ölçü", ["43-3/8"]),
        ("Değer 299.999%", "Değer", ["299.999%"]),
        ("metin", "başka metin", []),
    ],
)
def test_unconfirmed_tokens(primary: str, second: str, expected: list[str]) -> None:
    assert unconfirmed_tokens(primary, second) == expected


def cell(row: int, column: int, text: str, header: bool = False, span: int = 1) -> TableCell:
    return TableCell(
        row_start=row,
        row_end=row + 1,
        column_start=column,
        column_end=column + span,
        text=text,
        header=header,
    )


def test_table_rows_are_written_with_their_headers() -> None:
    cells = [
        cell(0, 0, "Ölçü", header=True),
        cell(0, 1, "M", header=True),
        cell(1, 0, "Bel"),
        cell(1, 1, "38,0"),
    ]

    assert [row.text for row in group_table_rows(cells)] == ["Ölçü: Bel | M: 38,0"]


def test_merged_value_carries_every_covered_column_header() -> None:
    cells = [
        cell(0, 0, "Özellik", header=True),
        cell(0, 1, "A", header=True),
        cell(0, 2, "B", header=True),
        cell(1, 0, "Ağırlık"),
        cell(1, 1, "28 kg", span=2),
    ]

    assert group_table_rows(cells)[0].text == "Özellik: Ağırlık | A & B: 28 kg"


def test_table_without_body_produces_no_rows() -> None:
    assert group_table_rows([cell(0, 0, "Başlık", header=True)]) == []


def test_short_size_labels_do_not_look_like_letter_spaced_text() -> None:
    assert quality_score("Beden Etiket S ETK-1 M ETK-2 L ETK-3") == 1.0


def test_short_number_is_not_confirmed_by_a_substring_of_another_number() -> None:
    assert unconfirmed_tokens("Tolerans 10", "Tolerans 1,0 ölçü 104,5") == ["10"]


def test_table_without_detected_headers_uses_a_label_first_row() -> None:
    cells = [
        cell(0, 0, "Ölçü"),
        cell(0, 1, "M"),
        cell(1, 0, "Bel"),
        cell(1, 1, "38,0"),
    ]

    assert [row.text for row in group_table_rows(cells)] == ["Ölçü: Bel | M: 38,0"]


def test_numeric_first_row_is_not_taken_as_header() -> None:
    cells = [cell(0, 0, "10"), cell(0, 1, "20"), cell(1, 0, "30"), cell(1, 1, "40")]

    assert [row.text for row in group_table_rows(cells)] == ["10 | 20", "30 | 40"]


def test_ocr_table_line_artifacts_are_removed_from_cells() -> None:
    cells = [cell(0, 0, "| Ölçü", header=True), cell(1, 0, "| Bel |")]

    assert [row.text for row in group_table_rows(cells)] == ["Ölçü: Bel"]


def test_table_line_next_to_a_value_does_not_make_it_uncertain() -> None:
    assert unconfirmed_tokens("Uzunluk 59", "Uzunluk | 59|") == []


def test_decimal_comma_and_point_are_the_same_reading() -> None:
    assert unconfirmed_tokens("İç paça 77.0", "İç paça 77,0") == []


def test_missing_decimal_separator_stays_uncertain() -> None:
    assert unconfirmed_tokens("Tolerans 10", "Tolerans 1,0") == ["10"]
