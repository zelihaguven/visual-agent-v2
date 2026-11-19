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


@pytest.mark.parametrize("word", ["III", "lbs", "NSN", "12,5", "E050", "S", "M", "L", "B"])
def test_junk_score_accepts_real_tokens(word: str) -> None:
    assert junk_score(word) == 1.0


def test_size_letters_do_not_drop_a_label_table_page() -> None:
    page = "GML-6473 ölçü föyü Etiket kodları Beden Etiket kodu S ETK-3391 M ETK-3392 L ETK-3393"

    assert junk_score(page) >= 0.85


@pytest.mark.parametrize("letter", ["x", "q", "ğ"])
def test_lone_lowercase_letters_still_count_as_noise(letter: str) -> None:
    assert junk_score(letter) == 0.0


@pytest.mark.parametrize(
    ("old", "new", "expected"),
    [
        (0.95, 0.5, LayerChoice.OLD),
        (0.95, 0.94, LayerChoice.NEW),
        (0.5, 0.9, LayerChoice.NEW),
    ],
)
def test_choose_layer(old: float, new: float, expected: LayerChoice) -> None:
    assert choose_layer(old, new) is expected


def test_page_ranges_compacts_pages() -> None:
    assert page_ranges([1, 2, 3, 7, 9, 10]) == "1-3,7,9-10"


@pytest.mark.parametrize(
    ("primary", "second", "expected"),
    [
        ("Değer 12,5 cm", "Değer 12,5 cm", []),
        ("Değer 112 cm", "Değer /12 cm", ["112"]),  # eğik çizgi "1" sayılmaz (okuyucu kuralı)
        ("Kol 318 ölçü", "Kol 3/8 ölçü", ["318"]),  # kesir çizgisi "1" okuması değildir
        ("Kol 3/8 ölçü", "Kol 318 ölçü", ["3/8"]),
        ("Tolerans ±1/2", "Tolerans +1/2", ["±1/2"]),
        ("40lbs yük", "40 lbs yük", ["40lbs"]),  # farklı bölünen parça da uyuşmaz
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


def test_decimal_comma_and_point_are_different_readings() -> None:
    """Virgül ve nokta farklı değer olabilir ("1.500" / "1,500"; karar 0008)."""
    assert unconfirmed_tokens("İç paça 77.0", "İç paça 77,0") == ["77.0"]


@pytest.mark.parametrize(("primary", "second"), [("Ölçü 812", "Ölçü B12"), ("Ölçü 50", "Ölçü SO")])
def test_letter_read_as_a_digit_does_not_confirm_the_value(primary: str, second: str) -> None:
    """B2: eski yol "B"yi "8", "S"yi "5", "O"yu "0" sayıyordu; ikinci okumada harf olan değer
    doğrulanmış geçiyordu. Artık okuyucu yolundaki gibi aynı parça olmalı."""
    assert unconfirmed_tokens(primary, second) == [primary.split()[1]]


def test_code_without_digits_is_compared_too() -> None:
    """B2: "4XL"in "AXL" okunması (karar 0007) rakamsız kodda da yakalanır."""
    assert unconfirmed_tokens("Beden XS-AXL", "Beden XS-4XL") == ["XS-AXL"]


def test_missing_decimal_separator_stays_uncertain() -> None:
    assert unconfirmed_tokens("Tolerans 10", "Tolerans 1,0") == ["10"]


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
