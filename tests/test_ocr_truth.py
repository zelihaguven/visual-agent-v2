from pathlib import Path

import pytest
from reportlab.pdfgen.canvas import Canvas

from evals.ocr_truth import (
    TruthDocument,
    TruthPage,
    TruthValue,
    ValueKind,
    canonical,
    layer_mismatches,
    same_value,
    separator_only,
)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("3/8", "⅜"),
        ("3/8", "³⁄₈"),
        ("3/8", "3⁄8"),
        ("3/8", "3 / 8"),
        ("27 1/2", "27½"),
        ("27 3/8", "27³⁄₈"),
        ("-3/8", "−3/8"),
        ("-3/8", "- 3/8"),
        ("-3/8", "$ -\\frac{3}{8} $"),
        ("27 1/2", "$ 27\\frac{1}{2} $"),
        ("80%", "80 %"),
        ('7/8"', "7/8″"),
        ("Fit Approved, Hold Sampling", "Fit  Approved,\r\nHold Sampling"),
    ],
)
def test_same_value_ignores_only_how_a_value_is_written(a: str, b: str) -> None:
    assert same_value(a, b)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("27 1/2", "271/2"),  # boşluk düşünce başka sayı
        ("-3/8", "-3 1/8"),
        ("3/8", "318"),
        ("4XL", "AXL"),
        ("Flc", "Fic"),
        ("Flc", "flc"),  # harf büyüklüğü korunur
        ("1.500", "1.5"),
        ("1.0", "1,0"),  # ayraç farkı ayrı raporlanır
        ("1.500", "1,500"),
    ],
)
def test_different_values_stay_different(a: str, b: str) -> None:
    assert not same_value(a, b)


def test_comma_between_words_is_not_a_decimal_separator() -> None:
    assert canonical("Fleece, Solid") == "Fleece, Solid"


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        ("1,0", "1.0", True),
        ("2,4931", "2.4931", True),
        ("1.500", "1,500", True),
        ("1.0", "1.0", False),  # aynı değer ayraç farkı değil
        ("1,0", "1.5", False),
        ("Fleece, Solid", "Fleece. Solid", False),
    ],
)
def test_separator_difference_is_reported_separately(a: str, b: str, expected: bool) -> None:
    assert separator_only(a, b) is expected


def test_text_layer_check_reads_each_value_in_its_box(tmp_path: Path) -> None:
    pdf = tmp_path / "a.pdf"
    canvas = Canvas(str(pdf), pagesize=(300, 200))
    canvas.setFont("Helvetica", 10)
    canvas.drawString(20, 150, "MD")
    canvas.drawString(80, 150, "27 1/2")
    canvas.save()
    box = (78.0, 40.0, 120.0, 54.0)  # sol-üst köşeye göre
    truth = TruthDocument(
        doc_id="a",
        source="synthetic",
        pages=(
            TruthPage(
                page=1,
                page_type="ölçü",
                values=(
                    TruthValue(kind=ValueKind.CELL, value="27 1/2", column="MD", box=box),
                    TruthValue(kind=ValueKind.CELL, value="28", column="LG", box=box),
                ),
            ),
        ),
    )

    assert layer_mismatches(pdf, truth) == [(1, "28", "27 1/2")]
