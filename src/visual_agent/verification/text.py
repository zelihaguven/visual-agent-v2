"""Karşılaştırma için metin biçimi; sayı ve teknik ad ayıklama."""

import re
import unicodedata

_NUMBER = r"\d+(?:[.,]\d+)?"
_NUMBER_RE = re.compile(_NUMBER)
TOLERANCE_RE = re.compile(rf"({_NUMBER})\s*\(\s*±\s*({_NUMBER})\s*\)")
CITATION_RE = re.compile(r"\[(\d+)\]")
_MULTI_CITATION_RE = re.compile(r"\[(\d+(?:\s*[,;–-]\s*\d+)+)\]")
CUT_CITATION_RE = re.compile(r"\s*\[\d*$")
FOREIGN_SCRIPT_RE = re.compile("[぀-ヺー-ヿ㐀-鿿가-힯＀-､ｦ-￯Ѐ-ӿ؀-ۿͰ-Ͽ]")
_LETTER_PREFIXED_CODE_RE = re.compile(r"\b[A-Za-z]{1,5}-?\d+[A-Za-z]*\b")
_LIST_MARK_RE = re.compile(
    r"(?:^\s*|(?<=[.:;])\s+)\d{1,2}[.)]\s+(?=[A-ZÇĞİÖŞÜ*])|^\s*\d{1,2}[.)]\s+", re.MULTILINE
)
_LINE_BREAK_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_LEADING_DECIMAL_RE = re.compile(r"(?<![\d.,])[.,](\d)")
_MAX_CITATION_RANGE = 20

_UPPER = "A-ZÇĞİÖŞÜ"
_LOWER = "a-zçğıöşü"
_IDENTIFIER_RE = re.compile(
    r"(?<![\w-])(?:"
    rf"[{_UPPER}][{_UPPER}0-9]*(?:[_-][{_UPPER}0-9]+)+"
    rf"|[{_LOWER}][{_LOWER}0-9]*(?:_[{_LOWER}0-9]+)+"
    rf"|[{_UPPER}]+\d+[{_UPPER}]*"
    r")(?![\w-])"
)
_BACKTICK_RE = re.compile(r"`([^`\n]+)`")

_WORD_NUMBER_LISTS = (
    "one two three four five six seven eight nine ten eleven twelve",
    "uno dos tres cuatro cinco seis siete ocho nueve diez - doce",
    "- deux trois quatre cinq six sept huit neuf dix onze douze",
    "bir iki üç dört beş altı yedi sekiz dokuz - onbir oniki",
)
_WORD_NUMBERS = {
    word: value
    for words in _WORD_NUMBER_LISTS
    for value, word in enumerate(words.split(), start=1)
    if word != "-"
} | {"twice": 2}
_WORD_NUMBER_RE = re.compile(
    r"(?<!\w)(" + "|".join(sorted(_WORD_NUMBERS, key=len, reverse=True)) + r")(?!\w)",
    re.IGNORECASE,
)


def _build_char_table() -> dict[int, str]:
    table = {ord("×"): "x", ord("✕"): "x", ord("⁄"): "/", ord("⓿"): "0"}
    for start, first in ((0x2776, 1), (0x2780, 1), (0x278A, 1), (0x24F5, 1), (0x24EB, 11)):
        for offset in range(10):
            table[start + offset] = str(first + offset)
    return table


_CHAR_TABLE = _build_char_table()


def canon_chars(text: str) -> str:
    """Kaynak, alıntı ve cevabı aynı karakter biçimine getirir."""
    return unicodedata.normalize("NFKC", text.translate(_CHAR_TABLE)).translate(_CHAR_TABLE)


def normalize(text: str) -> str:
    """Boşluk, tırnak, tire ve büyük-küçük harf farklarını yok sayar."""
    folded = canon_chars(text).casefold().replace("\xa0", " ")
    for original, replacement in (("’", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-")):
        folded = folded.replace(original, replacement)
    return re.sub(r"\s+", " ", re.sub(r"\s*-\s*", "-", folded)).strip()


def _expand_citation(match: re.Match[str]) -> str:
    numbers: list[int] = []
    for part in re.split(r"\s*[,;]\s*", match.group(1)):
        bounds = re.split(r"\s*[–-]\s*", part)
        first = int(bounds[0])
        last = int(bounds[1]) if len(bounds) > 1 else None
        if last is not None and 0 <= last - first < _MAX_CITATION_RANGE:
            numbers.extend(range(first, last + 1))
        else:
            numbers.extend([first] if last is None else [first, last])
    return "".join(f"[{number}]" for number in numbers)


def strip_citations(text: str) -> str:
    return CITATION_RE.sub("", _MULTI_CITATION_RE.sub(_expand_citation, text))


def canonical_number(raw: str) -> str:
    value = raw.replace(",", ".")
    return value.rstrip("0").rstrip(".") if "." in value else value


def numbers_in(text: str) -> set[str]:
    """Değer sayıları: atıf, liste numarası ve kod içindeki rakamlar hariç."""
    cleaned = strip_citations(_LINE_BREAK_RE.sub("\n", canon_chars(text)))
    cleaned = _LEADING_DECIMAL_RE.sub(r"0.\1", cleaned)
    cleaned = _LETTER_PREFIXED_CODE_RE.sub(" ", _LIST_MARK_RE.sub("", cleaned))
    return {canonical_number(match.group(0)) for match in _NUMBER_RE.finditer(cleaned)}


def word_numbers(text: str) -> set[str]:
    """Alıntıda yazıyla geçen sayılar; yalnız kaynak tarafında kullanılır."""
    return {str(_WORD_NUMBERS[word.lower()]) for word in _WORD_NUMBER_RE.findall(text)}


def _fold_identifier(value: str) -> str:
    return value.replace("İ", "i").casefold()


def identifiers_in(text: str) -> set[str]:
    """Kod, tablo, kolon ve komut adları gibi birebir olması gereken teknik adlar."""
    canon = canon_chars(text)
    quoted = {_fold_identifier(match) for match in _BACKTICK_RE.findall(canon)}
    remainder = _BACKTICK_RE.sub(" ", canon)
    return quoted | {_fold_identifier(m.group(0)) for m in _IDENTIFIER_RE.finditer(remainder)}
