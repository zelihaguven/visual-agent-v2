"""Alıntı denetimi: yalnız biçim farkı yok sayılır, içerik sayılabilecek işaret korunur."""

import pytest

from visual_agent.verification.quote import field_quote_matches, quote_matches
from visual_agent.verification.text import quote_form, quote_plain_form, source_plain_form

# Gerçek örnekler: parça metni ve modelin alıntısı (FastReact tur 1, sorular 2, 12, 15, 7, 17).
LOG_SOURCE = (
    "or checking here. **Log to text file:** This is provided to help FastReact support staff"
    " to diagnose problems. Only turn this on if you are asked to by FastReact staff."
)
MENU_SOURCE = (
    "# Main Menu - Tools - Archiving - Archive Orders **Source:** FastReact Help (version 4.44)"
    " — User manual\n**Menu path:** Main Menu > Tools > Archiving > Archive Orders\n"
    "**Index keywords:** Archive"
)
WILDCARD_SOURCE = (
    "Wild cards explained Two wild card match characters are available. An asterisk ‘\\*’ and a"
    " question mark ‘?’. The asterisk matches any number of characters whilst the question mark"
    " matches one single character."
)
POSSIBLE_SOURCE = (
    'When the delivery date is changed the system will also generate a "possible" date for the'
    " order. A possible date is the best estimated date based on where the order has been planned."
)
RELEASE_SOURCE = (
    "*Context: FastReact Help › Software Releases > 4.44 › Release content › New Enhancements And"
    " Additional Fucntionality* **Ref 17394 — New reporting function @SPLITPART to allow splitting"
    " of data in a reporting field** Functionality has been added to allow the splitting of data"
)


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        (
            "Log to text file: This is provided to help FastReact support staff to diagnose"
            " problems. Only turn this on if you are asked to by FastReact staff.",
            LOG_SOURCE,
        ),
        ("Menu path: Main Menu > Tools > Archiving > Archive Orders", MENU_SOURCE),
        (
            "Two wild card match characters are available. An asterisk ‘*’ and a question mark"
            " ‘?’.",
            WILDCARD_SOURCE,
        ),
        (
            "the system will also generate a 'possible' date for the order. A possible date is"
            " the best estimated date based on where the order has been planned.",
            POSSIBLE_SOURCE,
        ),
        (
            "Software Releases > 4.44 › Release content › New Enhancements And Additional"
            " Fucntionality* **Ref 17394 — New reporting function @SPLITPART to allow",
            RELEASE_SOURCE,
        ),
    ],
)
def test_quotes_differing_only_in_format_are_accepted(quote: str, source: str) -> None:
    assert quote_matches(quote, source)


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("bold.", "**bold**."),
        ("Use Archive Orders, then save.", "Use **Archive Orders**, then save."),
        ("Set it to bold-italic now", "Set it to ***bold-italic*** now"),
        ("Enter P.CODE here", "Enter `P.CODE` here"),
    ],
)
def test_paired_markdown_marks_before_punctuation_are_format(quote: str, source: str) -> None:
    assert quote_matches(quote, source)


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("Enter ABC to match", "Enter ABC* to match"),
        ("Filter .txt files only", "Filter *.txt files only"),
        ("pass kwargs to the function", "pass **kwargs to the function"),
        ("result is 23 and 42", "result is 2**3 and 4**2"),
    ],
)
def test_marks_that_may_be_content_are_not_dropped(quote: str, source: str) -> None:
    assert not quote_matches(quote, source)


@pytest.mark.parametrize(
    "source", ["Enter ABC* to match", "pass **kwargs to the function", "Use `ls -la` here"]
)
def test_a_verbatim_quote_of_content_marks_is_accepted(source: str) -> None:
    assert quote_matches(source, source)


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("Production is 1500 units per day.", "**Production** is 1000 units per day."),
        ("Bel ölçüsü 76 mm.", "**Bel ölçüsü** 76 cm."),
        ("Tolerans 15 cm.", "**Tolerans** 1,5 cm."),
        ("Kapasite 1000 adet.", "**Kapasite** 1.000 adet."),
        ("Mandatory field: `P.TYPE`", "**Mandatory field:** `P.CODE`"),
        ("Use O.QTY WEEK in the layout.", "Use **O.QTY_WEEK** in the layout."),
        ("Use @SUMS in the layout.", "Use `@SUM` in the layout."),
        ("Only turn this on if asked to by FastReact staff.", LOG_SOURCE),
        ("Only turn this on if you are explicitly asked to by FastReact staff.", LOG_SOURCE),
        (
            "Software Releases > 4.44 › Release content › New Enhancements And Additional"
            " Fucntionality* **Ref 17349 — New reporting function @SPLITPART to allow",
            RELEASE_SOURCE,
        ),
    ],
)
def test_quotes_with_a_different_value_code_or_wording_are_still_rejected(
    quote: str, source: str
) -> None:
    assert not quote_matches(quote, source)


def test_labeled_quote_matches_through_paired_marks() -> None:
    assert quote_matches("Week numbers: Enabled", "**Week numbers:** Enabled | Year 1: x")
    assert field_quote_matches("Week numbers: Enabled", "Week numbers: Enabled | Year 1: x")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("**Log to text file:** On", "log to text file: on"),
        ("Use **Archive Orders**, then", "use archive orders, then"),
        ("`EF.NAME` alanı", "ef.name alanı"),
        ("An asterisk ‘\\*’", 'an asterisk "*"'),
        ("*Context: Help › Index*", "*context: help › index*"),
        ("pass **kwargs and 2**3", "pass **kwargs and 2**3"),
        ("ABC* and *.txt", "abc* and *.txt"),
        ("O.QTY_WEEK~1 and P^WC:n", "o.qty_week~1 and p^wc:n"),
        ("C:\\Program Files\\FastReact", "c:\\program files\\fastreact"),
        ("“possible”  date\nnext", '"possible" date next'),
    ],
)
def test_source_side_removes_only_paired_marks(text: str, expected: str) -> None:
    assert source_plain_form(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Fucntionality* **Ref 17394", "fucntionality* ref 17394"),
        ("`P.CODE` alanı", "p.code alanı"),
        ("ABC* and *.txt", "abc* and *.txt"),
    ],
)
def test_quote_side_removes_every_strong_mark_but_keeps_single_stars(
    text: str, expected: str
) -> None:
    assert quote_plain_form(text) == expected


def test_verbatim_way_changes_only_quote_marks_and_spacing() -> None:
    assert quote_form("**A** ‘x’  y") == '**a** "x" y'


def test_escaped_asterisks_are_literal_not_emphasis() -> None:
    assert source_plain_form("\\*\\*not bold\\*\\*") == "**not bold**"
