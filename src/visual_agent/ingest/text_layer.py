"""Sayfa başına metin katmanı kontrolü; belgeye özel kural içermez."""

from enum import StrEnum

MIN_TEXT_CHARS = 50
IMAGE_COVER_RATIO = 0.5
WEAK_SCORE = 0.85
_PUNCTUATION = ".,;:()[]\"'!?"
_VOWELS = set("aeıioöuüAEIİOÖUÜyY")
_MIN_LETTER_SPACED_RUN = 4


class PageKind(StrEnum):
    """Yalnız metinli sayfa (TEXT) Docling'den geçer; ötekiler sayfa okuyucusuna gider (0028)."""

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
