"""Sayfa başına metin katmanı kontrolü; belgeye özel kural içermez."""

import re
from enum import StrEnum

MIN_TEXT_CHARS = 50
IMAGE_COVER_RATIO = 0.5
WEAK_SCORE = 0.85
_PUNCTUATION = ".,;:()[]\"'!?"
_VOWELS = set("aeıioöuüAEIİOÖUÜyY")
_WIDE_VOWELS = _VOWELS | set("àâäéèêëîïôûùáíóúñÀÂÉÈÊÎÔÛÁÍÓÚ")
_MIN_LETTER_SPACED_RUN = 4
_ROMAN_RE = re.compile(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")
_JUNK_CHARACTERS = set("|«»~\\{}®$¢£¥§¶^`")
_REPEATED_LETTER_RE = re.compile(r"(.)\1\1")


class PageKind(StrEnum):
    TEXT = "text"
    WEAK = "weak"
    SCANNED = "scanned"
    NONE = "none"


def classify_page(chars: int, image_cover: float, score: float) -> PageKind:
    if chars < MIN_TEXT_CHARS:
        return PageKind.NONE if image_cover >= IMAGE_COVER_RATIO or chars == 0 else PageKind.TEXT
    if score < WEAK_SCORE:
        return PageKind.WEAK
    return PageKind.SCANNED if image_cover >= IMAGE_COVER_RATIO else PageKind.TEXT


def _letter_spaced_count(words: list[str]) -> int:
    """Ardışık tek harfler harf aralıklı yazıdır; tek tük beden harfi ("S", "M") değildir."""
    total = run = 0
    for word in [*words, ""]:
        if len(word) == 1 and word.isalpha():
            run += 1
            continue
        total += run if run >= _MIN_LETTER_SPACED_RUN else 0
        run = 0
    return total


def _has_no_vowel(word: str) -> bool:
    return len(word) >= 4 and word.isalpha() and not set(word) & _VOWELS and not word.isupper()


def quality_score(text: str) -> float:
    words = [word.strip(_PUNCTUATION) for word in text.split()]
    words = [word for word in words if word]
    if not words:
        return 0.0
    broken = _letter_spaced_count(words) + sum(map(_has_no_vowel, words)) + text.count("�")
    return round(max(0.0, 1.0 - broken / len(words)), 3)


def _is_junk_upper(core: str) -> bool:
    if len(core) < 8 or not core.isupper():
        return False
    ratio = sum(character in _WIDE_VOWELS for character in core) / len(core)
    return ratio < 0.25 or ratio > 0.6


def _is_junk_alpha(core: str) -> bool:
    if len(core) == 1:
        return core not in "aAIoOeEyY"
    if _ROMAN_RE.match(core):
        return False
    if _REPEATED_LETTER_RE.search(core.casefold()):
        return True
    if not set(core) & _WIDE_VOWELS and len(core) >= 4:
        return True
    inner = core[1:]
    mixed_case = any(c.islower() for c in inner) and any(c.isupper() for c in inner)
    return _is_junk_upper(core) or mixed_case


def _is_junk_word(word: str) -> bool:
    core = word.strip(_PUNCTUATION)
    if not core:
        return False
    if set(core) & _JUNK_CHARACTERS and not any(character.isdigit() for character in core):
        return True
    return core.isalpha() and _is_junk_alpha(core)


def junk_score(text: str) -> float:
    """OCR'ın ürettiği anlamsız dizilerin karşıtı: 1 tamamen temiz."""
    words = text.split()
    if not words:
        return 0.0
    return round(1.0 - sum(map(_is_junk_word, words)) / len(words), 3)
