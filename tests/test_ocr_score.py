import json
from pathlib import Path

import pytest

from evals.ocr_score import (
    Outcome,
    ReadCell,
    ReadPage,
    ReadRow,
    html_rows,
    paddle_vl_page,
    pipeline_pages,
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


def _form(*rows: tuple[str, ...]) -> list[Outcome]:
    truth = TruthPage(
        page=1,
        page_type="kapak",
        values=(
            TruthValue(kind=ValueKind.PAIR, value="XS", label="Base size"),
            TruthValue(kind=ValueKind.PAIR, value="FW27", label="Season"),
        ),
    )
    return [outcome for _, outcome in score_page(truth, _read(*rows))]


@pytest.mark.parametrize(
    "rows",
    [
        (("Base size Season XS",),),  # iki etiket karışık: "Etiket A Etiket B DeğerA"
        (("Base size Season XS FW27",),),
        (("Base size", "FW27", "Season", "XS"),),  # aynı satırda başka etiketin değeri
        (("Base size FW27",), ("Season XS",)),  # değerler etiketler arasında yer değiştirmiş
    ],
)
def test_mixed_labels_in_one_reading_are_a_broken_binding(rows: tuple[tuple[str, ...]]) -> None:
    assert _form(*rows)[0] is Outcome.BROKEN


def test_label_and_value_read_into_one_cell_keep_their_binding() -> None:
    outcomes = _outcomes(_read(("Base size XS",)))

    assert outcomes[0] is Outcome.CORRECT


def test_values_the_reader_hides_are_counted_apart() -> None:
    hidden = ReadPage(
        page=1,
        rows=(
            ReadRow(cells=tuple(ReadCell(text=t) for t in HEADER)),
            ReadRow(
                cells=(
                    ReadCell(text="BL005"),
                    ReadCell(text="-3 1/8", uncertain=True),  # yanlış ama gizlendi
                    ReadCell(text="27 1/2", uncertain=True),  # doğru ama gizlendi
                    ReadCell(text="1,0"),
                )
            ),
        ),
    )

    outcomes = _outcomes(hidden)

    assert outcomes[2:5] == [Outcome.HIDDEN_WRONG, Outcome.HIDDEN_RIGHT, Outcome.CORRECT]


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


def test_html_table_keeps_rows_and_spanned_columns() -> None:
    table = (
        '<table><tr><td colspan="2">Under Armour</td><td>MD</td></tr>'
        "<tr><td>BL005</td><td>1390274 &amp; 6007591</td><td>a\\nb</td></tr></table>"
    )

    assert html_rows(table) == [["Under Armour", "", "MD"], ["BL005", "1390274 & 6007591", "a b"]]


def test_paddle_vl_blocks_keep_reading_order(tmp_path: Path) -> None:
    result = tmp_path / "s1_res.json"
    blocks = [
        {"block_label": "paragraph_title", "block_content": "POMs"},
        {
            "block_label": "table",
            "block_content": "<table><tr><td>Dim</td><td>MD</td></tr>"
            "<tr><td>BL005</td><td>$ 27\\frac{1}{2} $</td></tr></table>",
        },
        {"block_label": "image", "block_content": ""},
        {"block_label": "text", "block_content": "Units: inch\nGrade: Absolute"},
    ]
    result.write_text(json.dumps({"parsing_res_list": blocks}))

    page = paddle_vl_page(result, 1)

    assert [[c.text for c in r.cells] for r in page.rows] == [
        ["POMs"],
        ["Dim", "MD"],
        ["BL005", "$ 27\\frac{1}{2} $"],
        ["Units: inch"],
        ["Grade: Absolute"],
    ]


def test_pipeline_rows_become_header_and_value_rows_with_hidden_cells() -> None:
    from visual_agent.domain.document import Chunk, ChunkKind, SourceLocation

    row = Chunk(
        chunk_id="d:1",
        doc_id="d",
        kind=ChunkKind.TABLE_ROW,
        text="Dim: BL005 | Tol (-): -3/8 | MD: 27 1/2",
        title="d",
        section="POMs · Tall",
        location=SourceLocation(page=2),
        ocr_uncertain=("27",),
    )

    page = pipeline_pages([row])[0]

    assert page.page == 2
    assert [[c.text for c in r.cells] for r in page.rows] == [
        ["POMs"],
        ["Tall"],
        ["Dim", "Tol (-)", "MD"],
        ["BL005", "-3/8", "27 1/2"],
    ]
    assert [c.uncertain for c in page.rows[3].cells] == [False, False, True]


def test_second_reading_marks_hidden_cells_by_block(tmp_path: Path) -> None:
    result = tmp_path / "s1_res.json"
    table = "<table><tr><td>Dim</td><td>MD</td></tr><tr><td>BL005</td><td>-3 1/8</td></tr></table>"
    result.write_text(
        json.dumps(
            {"parsing_res_list": [{"block_id": 3, "block_label": "table", "block_content": table}]}
        )
    )

    page = paddle_vl_page(result, 1, {3: ["-3"]})

    assert [c.uncertain for c in page.rows[1].cells] == [False, True]


FROZEN_SCORING = {
    "evals/ocr_score.py": "72b88b001c0bb37d77d10f14e5b8452ee2e31c0ce8682ae5f2fd29b2a8687f24",
    "evals/ocr_truth.py": "9533f39742831eb1eff642efbabd5ba233c04b4ce114b76211bf5d5603137744",
}
"""Puanlama, eşdeğerlik kuralları ve dönüştürücüler ölçümden önce donduruldu (2026-11-16).
Ölçümden sonra değişirse bu test kırılır: değişiklik yeni bir ölçüm turu ve karar notu ister;
sonuçlara bakıp puanlama değiştirilmez."""


def test_scoring_is_frozen() -> None:
    import hashlib

    root = Path(__file__).parent.parent
    current = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in FROZEN_SCORING
    }
    assert current == FROZEN_SCORING
