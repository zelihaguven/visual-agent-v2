import pytest

from visual_agent.ingest.pdf_tables import TableCell, group_table_rows
from visual_agent.ingest.text_layer import PageKind, classify_page, quality_score


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


def test_full_width_rows_become_the_context_of_the_rows_they_label() -> None:
    """ "Tall" altındaki satır o bölüme, tablo sonundaki not bütün satırlara bağlanır."""
    cells = [
        cell(0, 0, "Dim", header=True),
        cell(0, 1, "MD", header=True),
        cell(0, 2, "LG", header=True),
        cell(1, 0, "SL095"),
        cell(1, 1, "11 1/4"),
        cell(1, 2, "11 1/4"),
        cell(2, 0, "Tall", span=3),
        cell(3, 0, "SL095"),
        cell(3, 1, "10 3/4"),
        cell(3, 2, "10 3/4"),
        cell(4, 0, "Grade Rule Display: Increment", span=3),
    ]

    rows = group_table_rows(cells)

    assert [(row.text, row.context) for row in rows] == [
        ("Dim: SL095 | MD: 11 1/4 | LG: 11 1/4", "Grade Rule Display: Increment"),
        ("Dim: SL095 | MD: 10 3/4 | LG: 10 3/4", "Tall · Grade Rule Display: Increment"),
    ]


def test_table_without_value_rows_keeps_its_rows() -> None:
    cells = [cell(0, 0, "Başlık", header=True, span=2), cell(1, 0, "Yalnız not", span=2)]

    assert [row.text for row in group_table_rows(cells)] == ["Yalnız not"]


def test_note_split_over_two_wide_cells_is_still_the_table_note() -> None:
    cells = [
        cell(0, 0, "Dim", header=True),
        cell(0, 1, "XS", header=True),
        cell(0, 2, "SM", header=True),
        cell(0, 3, "MD", header=True),
        cell(1, 0, "BL005"),
        cell(1, 1, "-1/2"),
        cell(1, 2, "0"),
        cell(1, 3, "1"),
        cell(2, 0, "Displaying 1 - 16 of 38 results", span=2),
        cell(2, 2, "Grade Rule Display: Increment", span=2),
    ]

    rows = group_table_rows(cells)

    assert len(rows) == 1
    assert rows[0].context == "Displaying 1 - 16 of 38 results | Grade Rule Display: Increment"


def test_form_table_whose_empty_cell_docling_dropped_is_not_given_a_header() -> None:
    """Docling'in gerçek çıktısı (2026-11-19): ilk satırın boş 2. hücresi hücre listesinde yok.
    Önceden ilk satır başlık sayılıyor, değer yanlış etiketi alıyordu ("Material Description:
    Fit Approved"). Artık başlıksız: boş hücre "(boş)" yazılır, etiket kendi değerinin yanında."""
    cells = [
        cell(0, 0, "Supplier Request Round"),
        cell(0, 2, "Material Description"),
        cell(0, 3, "Fleece"),
        cell(1, 0, "Sample Status"),
        cell(1, 1, "Fit Approved"),
        cell(1, 2, "Season"),
        cell(1, 3, "FW27"),
    ]

    assert [row.text for row in group_table_rows(cells)] == [
        "Supplier Request Round | (boş) | Material Description | Fleece",
        "Sample Status | Fit Approved | Season | FW27",
    ]


def test_label_row_does_not_stop_a_fitting_first_row_from_being_the_header() -> None:
    cells = [
        cell(0, 0, "Ölçü"),
        cell(0, 1, "M"),
        cell(1, 0, "Üst beden", span=2),
        cell(2, 0, "Bel"),
        cell(2, 1, "38,0"),
    ]

    assert [row.text for row in group_table_rows(cells)][-1] == "Ölçü: Bel | M: 38,0"
