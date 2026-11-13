"""Doğrulanmış cümleyi sesli okunacak metne çevirir; değerler değişmez."""

import re

from visual_agent.verification.text import MINUS_SIGNS, NUMBER, UNITS, UPPER, identifiers_in

CODE_ON_SCREEN = "Komut ekranda gösteriliyor."

_DIGITS = ["sıfır", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_TENS = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
_LETTERS = dict(
    zip(
        "ABCÇDEFGĞHIİJKLMNOÖPQRSŞTUÜVWXYZ",
        [
            "a",
            "be",
            "ce",
            "çe",
            "de",
            "e",
            "fe",
            "ge",
            "yumuşakge",
            "he",
            "ı",
            "i",
            "je",
            "ke",
            "le",
            "me",
            "ne",
            "o",
            "ö",
            "pe",
            "kü",
            "re",
            "se",
            "şe",
            "te",
            "u",
            "ü",
            "ve",
            "dabılyu",
            "iks",
            "ye",
            "ze",
        ],
        strict=True,
    )
)
# Okunuşu olan birimler. Tek harfli birim yalnız küçük harfle birimdir: "38 M" bedendir.
_SPOKEN_UNITS = {unit: spoken for unit, (_, spoken) in UNITS.items() if spoken}
_UNIT = "|".join(
    re.escape(unit) if len(unit) == 1 else f"(?i:{re.escape(unit)})"
    for unit in sorted(_SPOKEN_UNITS, key=len, reverse=True)
)
_MAX_SPELLED_LETTERS = 3
_MAX_WORDED_NUMBER = 999_999

# Binlik noktası ve ondalık virgülüyle yazılmış Türkçe biçim; ondalık mı binlik mi belirsiz değil.
_TURKISH_GROUPED_RE = re.compile(r"[1-9]\d{0,2}(?:\.\d{3})+(?:,\d+)?")
_TOKEN_RE = re.compile(
    rf"%(?P<percent>{NUMBER})"
    # Sayı bütün okunur ya da hiç dokunulmaz: "x1.500" ve "2,5x3" yazıldığı gibi kalır.
    rf"|(?<![\w-])(?<!\d[.,])(?P<minus>[{MINUS_SIGNS}])?(?P<number>{NUMBER})"
    rf"(?:[-–](?P<to>{NUMBER}))?+(?![\w-])"
    rf"(?:(?P<percent_after>%)|(?P<close>\)?)\s?(?P<unit>{_UNIT})(?!\w))?"
    rf"(?P<suffix>'\w+)?"
    rf"|(?<![\w-])(?P<code>[{UPPER}][{UPPER}0-9]*(?:[-_][{UPPER}0-9]+)*)(?![\w-])"
    rf"(?P<code_suffix>'\w+)?"
)


def _below_thousand(value: int) -> list[str]:
    words: list[str] = []
    hundreds, rest = divmod(value, 100)
    if hundreds:
        words += [*([_DIGITS[hundreds]] if hundreds > 1 else []), "yüz"]
    tens, ones = divmod(rest, 10)
    if tens:
        words.append(_TENS[tens])
    if ones:
        words.append(_DIGITS[ones])
    return words


def _integer_words(digits: str) -> str:
    value = int(digits)
    if value == 0 or value > _MAX_WORDED_NUMBER or (digits.startswith("0") and len(digits) > 1):
        return _digit_words(digits)
    thousands, rest = divmod(value, 1000)
    words = [*_below_thousand(thousands)] if thousands > 1 else []
    return " ".join([*words, *(["bin"] if thousands else []), *_below_thousand(rest)])


def _digit_words(digits: str) -> str:
    return " ".join(_DIGITS[int(digit)] for digit in digits)


def _number_words(raw: str) -> str:
    """Okunan değer yazılan değerle aynıdır; ayraç ancak anlamı belliyse yorumlanır.

    Yalnız Türkçe binlik biçimi ("1.234,50") değeriyle okunur; 999.999'u aşan tam kısım
    ("1.234.567") rakam rakam okunur. Öteki her ayraç
    adıyla, sonrası rakam rakam okunur: "42,5" kırk iki virgül beş, "14.30" on dört nokta üç
    sıfır, "1.500" bir nokta beş sıfır sıfır. Saat, tarih ya da binlik olabilecek yazım yorumlanmaz.
    """
    if _TURKISH_GROUPED_RE.fullmatch(raw) and (raw.count(".") > 1 or "," in raw):
        whole, _, fraction = raw.replace(".", "").partition(",")
        spoken = _integer_words(whole)
        return f"{spoken} virgül {_digit_words(fraction)}" if fraction else spoken
    parts = re.split(r"([.,])", raw)
    words = [_integer_words(parts[0])]
    for separator, digits in zip(parts[1::2], parts[2::2], strict=True):
        words += ["virgül" if separator == "," else "nokta", _digit_words(digits)]
    return " ".join(words)


def _spell(part: str) -> str:
    return " ".join(_LETTERS[c] if c in _LETTERS else _DIGITS[int(c)] for c in part)


def _code_words(code: str) -> str:
    """Kod harf harf okunur; yalnız harften oluşan uzun adlar sözcük gibi okunur."""
    parts = re.split(r"[-_]", code)
    if all(part.isalpha() and len(part) > _MAX_SPELLED_LETTERS for part in parts):
        return " ".join(part.replace("I", "ı").replace("İ", "i").lower() for part in parts)
    return " ".join(_spell(part) for part in parts)


def _replace(match: re.Match[str]) -> str:
    if match["percent"] is not None:
        return f"yüzde {_number_words(match['percent'])}"
    if match["number"] is not None:
        spoken = _number_words(match["number"])
        if match["minus"]:
            spoken = f"eksi {spoken}"
        if match["to"]:
            spoken += f" tire {_number_words(match['to'])}"
        if match["percent_after"]:
            spoken = f"yüzde {spoken}"
        elif match["unit"]:
            spoken += f"{match['close']} {_SPOKEN_UNITS[match['unit'].casefold()]}"
        return f"{spoken}{(match['suffix'] or '')[1:]}"
    return f"{_code_words(match['code'])}{(match['code_suffix'] or '')[1:]}"


def _read_turkish(text: str) -> str:
    return _TOKEN_RE.sub(_replace, text.replace("±", "artı eksi"))


def spoken_text(text: str, language: str, *, has_code: bool = False) -> str:
    """Komutlar sesle okunmaz; dinleyen kişi birebir metni ekrandan alır."""
    if has_code and identifiers_in(text):
        return CODE_ON_SCREEN
    body = _read_turkish(text) if language == "tr" else text
    return f"{body} {CODE_ON_SCREEN}" if has_code else body
