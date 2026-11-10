"""Alıntı denetimi: yalnız biçim farkı (markdown işaretleri, kaçış, tırnak, boşluk) yok sayılır."""

import pytest

from visual_agent.verification.quote import quote_matches
from visual_agent.verification.text import quote_form

# Gerçek örnekler: parça metni ve modelin alıntısı (FastReact tur 1, sorular 2, 12, 15, 7).
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
    ],
)
def test_quotes_differing_only_in_format_are_accepted(quote: str, source: str) -> None:
    assert quote_matches(quote, source)


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("Production is 1500 units per day.", "**Production** is 1000 units per day."),
        ("Bel ölçüsü 76 mm.", "**Bel ölçüsü** 76 cm."),
        ("Tolerans 15 cm.", "**Tolerans** 1,5 cm."),
        ("Kapasite 1000 adet.", "*Kapasite* 1.000 adet."),
        ("Mandatory field: `P.TYPE`", "**Mandatory field:** `P.CODE`"),
        ("Use O.QTY WEEK in the layout.", "Use **O.QTY_WEEK** in the layout."),
        ("Use @SUMS in the layout.", "Use `@SUM` in the layout."),
        (
            "Only turn this on if asked to by FastReact staff.",
            LOG_SOURCE,
        ),
        (
            "Only turn this on if you are explicitly asked to by FastReact staff.",
            LOG_SOURCE,
        ),
    ],
)
def test_quotes_with_a_different_value_code_or_wording_are_still_rejected(
    quote: str, source: str
) -> None:
    assert not quote_matches(quote, source)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("**Log to text file:** On", "log to text file: on"),
        ("*Context: Help › Index*", "context: help › index"),
        ("`EF.NAME` alanı", "ef.name alanı"),
        ("An asterisk ‘\\*’", 'an asterisk "*"'),
        ("“possible”  date\nnext", '"possible" date next'),
        ("2*3*4 and a * b * c", "2*3*4 and a * b * c"),
        ("‘*’ and ‘?’", '"*" and "?"'),
        ("O.QTY_WEEK~1 and P^WC:n", "o.qty_week~1 and p^wc:n"),
        ("C:\\Program Files\\FastReact", "c:\\program files\\fastreact"),
        ("1.000 and 1,5", "1.000 and 1,5"),
        ("_not changed_ and __init__", "_not changed_ and __init__"),
    ],
)
def test_quote_form_removes_only_format(text: str, expected: str) -> None:
    assert quote_form(text) == expected


RELEASE_SOURCE = (
    "*Context: FastReact Help › Software Releases > 4.44 › Release content › New Enhancements And"
    " Additional Fucntionality* **Ref 17394 — New reporting function @SPLITPART to allow splitting"
    " of data in a reporting field** Functionality has been added to allow the splitting of data"
)


def test_quote_cutting_through_emphasis_marks_still_matches() -> None:
    """Soru 17: alıntı italiğin sonunu ve kalının başını içeriyor, eşleri alıntının dışında."""
    quote = (
        "Software Releases > 4.44 › Release content › New Enhancements And Additional"
        " Fucntionality* **Ref 17394 — New reporting function @SPLITPART to allow"
    )

    assert quote_matches(quote, RELEASE_SOURCE)
    assert not quote_matches(quote.replace("17394", "17349"), RELEASE_SOURCE)
    assert not quote_matches(quote.replace("4.44", "4.43"), RELEASE_SOURCE)


def test_escaped_asterisks_are_literal_not_emphasis() -> None:
    assert quote_form("\\*\\*not bold\\*\\*") == "**not bold**"
