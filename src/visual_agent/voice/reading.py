"""Doğrulanmış cümleyi sesli okunacak metne çevirir; değerler değişmez."""

import re

from visual_agent.verification.text import identifiers_in

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
_UNITS = {
    "cm": "santimetre",
    "mm": "milimetre",
    "m": "metre",
    "kg": "kilogram",
    "gr": "gram",
    "TL": "Türk lirası",
}
_MAX_SPELLED_LETTERS = 3
_MAX_WORDED_NUMBER = 999_999

_UPPER = "A-ZÇĞİÖŞÜ"
_NUMBER = r"\d+(?:[.,]\d+)?"
_TOKEN_RE = re.compile(
    rf"%(?P<percent>{_NUMBER})"
    rf"|(?<![\w-])(?P<number>{_NUMBER})(?![\w-])(?:(?P<close>\)?)\s?(?P<unit>{'|'.join(_UNITS)})(?!\w))?"
    rf"(?P<suffix>'\w+)?"
    rf"|(?<![\w-])(?P<code>[{_UPPER}][{_UPPER}0-9]*(?:[-_][{_UPPER}0-9]+)*)(?![\w-])"
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
        return " ".join(_DIGITS[int(digit)] for digit in digits)
    thousands, rest = divmod(value, 1000)
    words = [*_below_thousand(thousands)] if thousands > 1 else []
    return " ".join([*words, *(["bin"] if thousands else []), *_below_thousand(rest)])


def _number_words(raw: str) -> str:
    whole, _, fraction = raw.replace(".", ",").partition(",")
    spoken = _integer_words(whole)
    if not fraction:
        return spoken
    return f"{spoken} virgül {' '.join(_DIGITS[int(digit)] for digit in fraction)}"


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
        unit = f"{match['close']} {_UNITS[match['unit']]}" if match["unit"] else ""
        return f"{_number_words(match['number'])}{unit}{(match['suffix'] or '')[1:]}"
    return f"{_code_words(match['code'])}{(match['code_suffix'] or '')[1:]}"


def _read_turkish(text: str) -> str:
    return _TOKEN_RE.sub(_replace, text.replace("±", "artı eksi"))


def spoken_text(text: str, language: str, *, has_code: bool = False) -> str:
    """Komutlar sesle okunmaz; dinleyen kişi birebir metni ekrandan alır."""
    if has_code and identifiers_in(text):
        return CODE_ON_SCREEN
    body = _read_turkish(text) if language == "tr" else text
    return f"{body} {CODE_ON_SCREEN}" if has_code else body
