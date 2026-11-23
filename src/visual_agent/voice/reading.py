"""Doğrulanmış cümleyi sesli okunacak metne çevirir; değerler değişmez."""

import re

from visual_agent.verification.text import (
    MINUS_SIGNS,
    NUMBER,
    UNITS,
    UPPER,
    identifiers_in,
    turkish_lower,
)

CODE_ON_SCREEN = "Komut ekranda gösteriliyor."
VALUE_ON_SCREEN = "Değer ekranda gösteriliyor."

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


# Sesin bütün olarak okuduğu yazımlar (_TOKEN_RE ile aynı): düz sayı, yüzde, aralık, işaretli
# sayı, Türkçe binlik. Baştaki % yalnız tek sayıyla okunur ("%5-10" yarım okunurdu).
_READABLE_NUMBER_RE = re.compile(
    rf"%{NUMBER}|[{MINUS_SIGNS}±]?{NUMBER}(?:[-–]{NUMBER})?%?|{_TURKISH_GROUPED_RE.pattern}"
)
# Harf harf okunan kod: büyük harfle başlayan (E050, XL, M8) ya da tireyle bağlı (tt-100157).
_CODE_WORD_RE = re.compile(
    rf"[{UPPER}][{UPPER}0-9]*(?:[-_][{UPPER}0-9]+)*|[^\W\d_][^\W_]*(?:[-_][^\W_]+)+"
)
# Sözcük uçları web'deki büyük değer kuralıyla aynı (apps/web/src/components/TurnView.tsx).
_WORD_EDGES_RE = re.compile(r"^[(\"“'‘\[]+|['’][^\W\d_]*[.,;:!?)\"”\]]*$|[.,;:!?)\"”\]]+$")


def _has_unreadable_number(text: str) -> bool:
    """Rakam taşıyan sözcük bütün okunabilir bir sayı ya da kod değil mi ("x1.500", "2,5x3,5",
    "M8x1,25", "27½", "190gm/m2", "3/8", tarih). Böyle sözcüğü TTS kendi yorumlar ve sayının
    bir parçasını okuyabilir; cümle okunmaz, değer ekranda kalır (kural 1). Kesir ve üs
    karakterleri ("½", "²") de sayı sayılır: tek başına yazılsa da okunmaz."""
    for word in text.split():
        core = _WORD_EDGES_RE.sub("", word)
        if any(c.isnumeric() for c in core) and not (
            _READABLE_NUMBER_RE.fullmatch(core) or _CODE_WORD_RE.fullmatch(core)
        ):
            return True
    return False


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
        return " ".join(turkish_lower(part) for part in parts)
    return " ".join(_spell(part) for part in parts)


_VOWELS = "aeıioöuü"
_BACK_VOWELS = "aıou"
_ROUNDED_VOWELS = "oöuü"
_INVARIANT_TAIL_RE = re.compile(r"(?P<head>.*?)(?P<tail>(?:ki|ken)\w*)?")
"""-ki ve -ken ünlü uyumuna girmez ("kg'daki" → "kilogramdaki"); ardından gelen ek ona uyar."""


def _harmonized(suffix: str, word: str) -> str:
    """Ek, yazılan kısaltmaya göre yazılmıştır ("TL'dir"); okunan sözcüğün son ünlüsüne uyar
    ("Türk lirasıdır"). İki yönlü (e/a) ve dört yönlü (ı/i/u/ü) ünlüler sırayla uyum sağlar."""
    parts = _INVARIANT_TAIL_RE.fullmatch(suffix)
    head, tail = (parts["head"], parts["tail"] or "") if parts else (suffix, "")
    previous = next((char for char in reversed(turkish_lower(word)) if char in _VOWELS), None)
    if previous is None:
        return suffix
    harmonized = []
    for char in head:
        back, rounded = previous in _BACK_VOWELS, previous in _ROUNDED_VOWELS
        if char in "ea":
            char = "a" if back else "e"
        elif char in "ıiuü":
            char = ("u" if rounded else "ı") if back else ("ü" if rounded else "i")
        if char in _VOWELS:
            previous = char
        harmonized.append(char)
    return "".join(harmonized) + tail


def _replace(match: re.Match[str]) -> str:
    if match["percent"] is not None:
        return f"yüzde {_number_words(match['percent'])}"
    if match["number"] is not None:
        spoken = _number_words(match["number"])
        if match["minus"]:
            spoken = f"eksi {spoken}"
        if match["to"]:
            spoken += f" tire {_number_words(match['to'])}"
        suffix = (match["suffix"] or "")[1:]
        if match["percent_after"]:
            spoken = f"yüzde {spoken}"
        elif match["unit"]:
            spoken += f"{match['close']} {_SPOKEN_UNITS[match['unit'].casefold()]}"
            suffix = _harmonized(suffix, spoken)
        return f"{spoken}{suffix}"
    return f"{_code_words(match['code'])}{(match['code_suffix'] or '')[1:]}"


def _read_turkish(text: str) -> str:
    return _TOKEN_RE.sub(_replace, re.sub(r"±\s*", "artı eksi ", text))


def spoken_text(text: str, language: str, *, has_code: bool = False) -> str:
    """Komutlar sesle okunmaz; dinleyen kişi birebir metni ekrandan alır."""
    if has_code and identifiers_in(text):
        return CODE_ON_SCREEN
    if _has_unreadable_number(text):
        return f"{VALUE_ON_SCREEN} {CODE_ON_SCREEN}" if has_code else VALUE_ON_SCREEN
    body = _read_turkish(text) if language == "tr" else text
    return f"{body} {CODE_ON_SCREEN}" if has_code else body
