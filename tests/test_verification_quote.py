"""Alıntı denetimi: yalnız biçim farkı yok sayılır, içerik olabilecek işaret korunur."""

import pytest

from visual_agent.verification.quote import quote_matches
from visual_agent.verification.text import markdown_plain_form, quote_form

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
RELEASE_QUOTE = (
    "Software Releases > 4.44 › Release content › New Enhancements And Additional"
    " Fucntionality* **Ref 17394 — New reporting function @SPLITPART to allow"
)
KWARGS_SOURCE = "pass **kwargs and **bold** text"


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
        (RELEASE_QUOTE, RELEASE_SOURCE),
    ],
)
def test_real_quotes_differing_only_in_format_are_accepted(quote: str, source: str) -> None:
    assert quote_matches(quote, source, "tr")


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("bold.", "**bold**."),
        ("Use Archive Orders, then save.", "Use **Archive Orders**, then save."),
        ("Set it to bold-italic now", "Set it to ***bold-italic*** now"),
        ("Enter P.CODE here", "Enter `P.CODE` here"),
        ("pass **kwargs and bold text", KWARGS_SOURCE),
    ],
)
def test_markdown_emphasis_and_code_marks_are_format(quote: str, source: str) -> None:
    assert quote_matches(quote, source, "tr")


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("Enter ABC to match", "Enter ABC* to match"),
        ("Filter .txt files only", "Filter *.txt files only"),
        ("pass kwargs and", KWARGS_SOURCE),
        ("pass kwargs to the function", "pass **kwargs to the function"),
        ("result is 234", "result is 2*3*4"),
        ("x2 + y2", "x**2 + y**2"),
        ("call init now", "call __init__ now"),
    ],
)
def test_marks_that_may_be_content_are_not_dropped(quote: str, source: str) -> None:
    assert not quote_matches(quote, source, "tr")


@pytest.mark.parametrize(
    "source",
    [
        "Enter ABC* to match",
        "pass **kwargs to the function",
        "Use `ls -la` here",
        "result is 2*3*4",
    ],
)
def test_a_verbatim_quote_of_content_marks_is_accepted(source: str) -> None:
    assert quote_matches(source, source, "tr")


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
        (RELEASE_QUOTE.replace("17394", "17349"), RELEASE_SOURCE),
    ],
)
def test_quotes_with_a_different_value_code_or_wording_are_still_rejected(
    quote: str, source: str
) -> None:
    assert not quote_matches(quote, source, "tr")


def test_labeled_quote_matches_through_emphasis() -> None:
    assert quote_matches("Week numbers: Enabled", "**Week numbers:** Enabled | Year 1: x", "tr")
    assert quote_matches("Week numbers: Enabled", "Week numbers: Enabled | Year 1: x", "tr")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("**Log to text file:** On", "log to text file: on"),
        ("Use **Archive Orders**, then", "use archive orders, then"),
        ("`EF.NAME` alanı", "ef.name alanı"),
        ("An asterisk ‘\\*’", 'an asterisk "*"'),
        ("*Context: Help › Index*", "context: help › index"),
        (KWARGS_SOURCE, "pass **kwargs and bold text"),
        ("ABC* and *.txt", "abc* and *.txt"),
        ("2*3*4 and x**2", "2*3*4 and x**2"),
        ("O.QTY_WEEK~1, __init__ and _x_", "o.qty_week~1, __init__ and _x_"),
        ("# Başlık [bağlantı](x) | a | b", "# başlık [bağlantı](x) | a | b"),
        ("C:\\Program Files\\FastReact", "c:\\program files\\fastreact"),
        ("“possible”  date\nnext", '"possible" date next'),
    ],
)
def test_parser_removes_only_emphasis_code_marks_and_escapes(text: str, expected: str) -> None:
    assert markdown_plain_form(text) == expected


def test_verbatim_way_changes_only_quote_marks_and_spacing() -> None:
    assert quote_form("**A** ‘x’  y") == '**a** "x" y'


def test_escaped_asterisks_are_literal_not_emphasis() -> None:
    assert markdown_plain_form("\\*\\*not bold\\*\\*") == "**not bold**"


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("4 cm", "Genişlik 74 cm"),
        ("2,5", "Beden M: 72,5 | Beden L: 74,0"),
        ("Genişlik 7", "Genişlik 7,5 cm"),
        ("72", "Kod 1720 kayıtlı"),
        ("5 adet", "Parti 1.5 adet"),
    ],
)
def test_quote_cannot_start_or_end_inside_a_number(quote: str, source: str) -> None:
    assert not quote_matches(quote, source, "tr")


def test_labeled_quote_cannot_cut_a_number() -> None:
    assert not quote_matches("Genişlik: 7", "Genişlik: 72 | Boy: 110", "tr")


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("M: 76,5", "İç paça | M: 76,5 | Tolerans: 0,5"),
        ("76,5", "İç paça | M: 76,5."),
        ("Genişlik 74 cm", "Ölçü: Genişlik 74 cm, boy 110 cm"),
        ("1,0", "Tolerans (cm): 1,0"),
    ],
)
def test_whole_numbers_are_still_accepted(quote: str, source: str) -> None:
    assert quote_matches(quote, source, "tr")


CUT_SOURCE = (
    "Dikiş makinesi ayarlarında kullanılacak iğne numarası ve iplik kalınlığı üretim talimatında"
    " belirtilen değerlere göre seçilmeli ve her vardiya başında kontrol edilmelidir ve kayıt"
    " tutulur."
)
CUT_HEAD = CUT_SOURCE.removesuffix(" kayıt tutulur.")


def test_cut_quote_cannot_add_a_number_in_its_unchecked_tail() -> None:
    assert not quote_matches(CUT_HEAD + " değer 99 cm.", CUT_SOURCE, "tr")


def test_cut_quote_cannot_add_a_code_in_its_unchecked_tail() -> None:
    assert not quote_matches(CUT_HEAD + " kod PNT-77.", CUT_SOURCE, "tr")


def test_cut_quote_with_a_plain_broken_tail_is_still_accepted() -> None:
    assert quote_matches(CUT_HEAD + " kayıt tutu", CUT_SOURCE, "tr")


@pytest.mark.parametrize(
    "source", ["Çalışma sıcaklığı -5 °C", "Çalışma sıcaklığı −5 °C", "En düşük (-5 °C)"]
)
def test_quote_cannot_drop_the_minus_sign_of_a_value(source: str) -> None:
    assert not quote_matches("5 °C", source, "tr")


@pytest.mark.parametrize(
    ("quote", "source"),
    [
        ("-5 °C", "Çalışma sıcaklığı -5 °C"),
        ("14 dikiş", "10-14 dikiş"),
        ("10-14 dikiş", "10-14 dikiş"),
    ],
)
def test_a_dash_that_is_not_a_sign_does_not_block_the_quote(quote: str, source: str) -> None:
    assert quote_matches(quote, source, "tr")


def test_digits_inside_a_code_are_not_a_quotable_value() -> None:
    assert not quote_matches("5 adet", "Kod A-5 adet", "tr")


def test_cut_quote_cannot_add_a_number_word_in_its_unchecked_tail() -> None:
    assert not quote_matches(CUT_HEAD + " beş kez yapılır.", CUT_SOURCE, "tr")


@pytest.mark.parametrize("tail", [" İki kez yapılır.", " ALTI kez yapılır.", " **İki** kez."])
def test_cut_quote_cannot_add_a_capitalized_number_word_in_its_tail(tail: str) -> None:
    assert not quote_matches(CUT_HEAD + tail, CUT_SOURCE, "tr")
