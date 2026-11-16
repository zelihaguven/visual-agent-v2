from pathlib import Path

import pytest

from evals.ocr_score import (
    Outcome,
    ReadCell,
    ReadPage,
    ReadRow,
    score_document,
    score_page,
    text_layer_pages,
)
from evals.ocr_truth import TruthDocument, TruthPage, TruthValue, ValueKind

SET_A = Path(__file__).parent.parent / "evals" / "assets" / "techpack_set_a"


def _truth() -> TruthPage:
    def cell(key: str, column: str, value: str) -> TruthValue:
        return TruthValue(kind=ValueKind.CELL, value=value, table=1, row_key=key, column=column)

    return TruthPage(
        page=1,
        page_type="olcu",
        values=(
            TruthValue(kind=ValueKind.PAIR, value="XS", label="Base size"),
            cell("BL005", "Dim", "BL005"),
            cell("BL005", "Tol (-)", "-3/8"),
            cell("BL005", "MD", "27 1/2"),
            cell("BL005", "LG", "1,0"),
            TruthValue(kind=ValueKind.TEXT, value="Units: Fractions of inches"),
        ),
    )


def _read(*rows: tuple[str, ...]) -> ReadPage:
    """Konumsuz okuma (HTML tablo gibi): sütun sıra numarasıyla eşleşir."""
    return ReadPage(
        page=1, rows=tuple(ReadRow(cells=tuple(ReadCell(text=t) for t in row)) for row in rows)
    )


HEADER = ("Dim", "Tol (-)", "MD", "LG")


def _outcomes(read: ReadPage) -> list[Outcome]:
    return [outcome for _, outcome in score_page(_truth(), read)]


def test_correct_reading_with_other_notations_is_correct() -> None:
    read = _read(
        ("Base size", "XS"), HEADER, ("BL005", "−⅜", "27½", "1,0"), ("Units: Fractions of inches",)
    )

    assert set(_outcomes(read)) == {Outcome.CORRECT}


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        (("BL005", "-3 1/8", "27 1/2", "1,0"), Outcome.WRONG),  # yanlış karakter
        (("BL005", "-3/8", "271/2", "1,0"), Outcome.WRONG),
        (("BL005", "-3/8", "", "1,0"), Outcome.MISSING),  # hücre boş
        (("BL005", "-3/8", "1,0", "27 1/2"), Outcome.BROKEN),  # sütunlar yer değiştirmiş
    ],
)
def test_each_error_kind_is_named(row: tuple[str, ...], expected: Outcome) -> None:
    outcomes = _outcomes(_read(("Base size", "XS"), HEADER, row))

    assert expected in outcomes[2:4]


def test_separator_difference_is_its_own_kind() -> None:
    outcomes = _outcomes(_read(HEADER, ("BL005", "-3/8", "27 1/2", "1.0")))

    assert outcomes[4] is Outcome.SEPARATOR


def test_lost_header_breaks_the_binding() -> None:
    outcomes = _outcomes(_read(("BL005", "-3/8", "27 1/2", "1,0")))

    assert outcomes[2:5] == [Outcome.BROKEN] * 3


def test_pair_value_under_another_label_is_a_broken_binding() -> None:
    outcomes = _outcomes(_read(("Base size", "Grade rule"), ("Tolerance", "XS")))

    assert outcomes[0] is Outcome.BROKEN


def test_label_and_value_read_into_one_cell_keep_their_binding() -> None:
    outcomes = _outcomes(_read(("Base size XS",)))

    assert outcomes[0] is Outcome.CORRECT


def test_unread_page_is_all_missing() -> None:
    assert set(outcome for _, outcome in score_page(_truth(), None)) == {Outcome.MISSING}


def test_positioned_cells_match_columns_by_place() -> None:
    def at(text: str, left: float) -> ReadCell:
        return ReadCell(text=text, left=left, right=left + 20)

    header = ReadRow(cells=(at("Dim", 0), at("Tol (-)", 40), at("MD", 80), at("LG", 120)))
    # Boş "Tol (-)" hücresi okunmamış: sıra numarası kayar, konum kaymaz.
    row = ReadRow(cells=(at("BL005", 0), at("27 1/2", 80), at("1,0", 120)))

    outcomes = [o for _, o in score_page(_truth(), ReadPage(page=1, rows=(header, row)))]

    assert outcomes[3:5] == [Outcome.CORRECT, Outcome.CORRECT]
    assert outcomes[2] is Outcome.MISSING


def test_digital_text_layer_of_set_a_scores_perfectly() -> None:
    """Puanlama betiğinin sınaması: metin katmanı doğru cevabın kaynağıyla aynıdır."""
    for number in (1, 3):
        truth = TruthDocument.model_validate_json((SET_A / f"syn{number}.json").read_text())
        results = score_document(truth, text_layer_pages(SET_A / f"syn{number}.pdf"))
        assert {outcome for *_, outcome in results} == {Outcome.CORRECT}
