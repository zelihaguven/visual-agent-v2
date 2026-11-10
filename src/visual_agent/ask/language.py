"""Metnin dili: cevap sorunun dilinde verilir."""

import re
from collections.abc import Sequence

from visual_agent.domain.document import Chunk

_TURKISH_LETTERS_RE = re.compile(r"[çğıöşüÇĞİÖŞÜ]")
_WORD_RE = re.compile(r"[a-z]+")
_TURKISH_HINTS = {
    "ne",
    "nedir",
    "nasil",
    "kac",
    "mi",
    "mu",
    "icin",
    "olmali",
    "hangi",
    "neden",
    "ve",
    "bir",
    "ile",
    "var",
    "yok",
    "degil",
}
_ENGLISH_HINTS = {
    "the",
    "how",
    "what",
    "which",
    "is",
    "are",
    "for",
    "of",
    "many",
    "much",
    "should",
    "does",
    "do",
    "on",
    "in",
    "to",
    "with",
    "when",
    "why",
    "can",
}


_LANGUAGE_SAMPLE_CHUNKS = 40


def document_language(chunks: Sequence[Chunk], fallback: str = "tr") -> str:
    """Belgenin dili ilk parçalarından okunur; uygulama ve ölçüm katalogu aynı kuralla kurar."""
    sample = " ".join(chunk.text for chunk in chunks[:_LANGUAGE_SAMPLE_CHUNKS])
    return detect_language(sample) if sample else fallback


def detect_language(text: str) -> str:
    """Yalnız Türkçe ve İngilizce ayırır; emin olunamazsa Türkçe döner."""
    if _TURKISH_LETTERS_RE.search(text):
        return "tr"
    words = _WORD_RE.findall(text.lower())
    english = sum(word in _ENGLISH_HINTS for word in words)
    turkish = sum(word in _TURKISH_HINTS for word in words)
    return "en" if english > turkish else "tr"
