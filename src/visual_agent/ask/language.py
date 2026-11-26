"""Metnin dili: cevap sorunun dilinde verilir."""

import re
from collections.abc import Sequence

from visual_agent.domain.document import Chunk

_TURKISH_LETTERS_RE = re.compile(r"[çğıöşüÇĞİÖŞÜ]")
_WORD_RE = re.compile(r"[a-z]+")
_DOCUMENT_WORD_RE = re.compile(r"[^\W\d_]+")
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


# Belgede "in" inç birimidir ("Bel (in): 32"), "on" Türkçe sayıdır ("on dakika"); sayılmaz.
_DOCUMENT_ENGLISH_HINTS = _ENGLISH_HINTS - {"in", "on"}
_LANGUAGE_SAMPLE_CHUNKS = 40
_DEFAULT_LANGUAGE = "tr"


def document_language(chunks: Sequence[Chunk], fallback: str = _DEFAULT_LANGUAGE) -> str:
    """Belgenin dili ilk parçalarından okunur; uygulama ve ölçüm katalogu aynı kuralla kurar.

    Soru kısadır, tek Türkçe harf yeter; belgede ise sözcükler sayılır: Türkçe harf taşıyan ya da
    Türkçe ipucu olan sözcükler, İngilizce ipucu sözcüklerine karşı. İngilizce kılavuzda geçen
    bir Türk firma adı belgeyi Türkçe yapmaz. Eşitlikte ve parça yoksa Türkçe sayılır.
    """
    sample = " ".join(chunk.text for chunk in chunks[:_LANGUAGE_SAMPLE_CHUNKS])
    if not sample:
        return fallback or _DEFAULT_LANGUAGE
    # "İ".lower() birleşik nokta üretir ve sözcüğü böler ("DİKKAT" -> "di", "kkat").
    words = _DOCUMENT_WORD_RE.findall(sample.replace("İ", "i").lower())
    turkish = sum(
        bool(_TURKISH_LETTERS_RE.search(word)) or word in _TURKISH_HINTS for word in words
    )
    english = sum(word in _DOCUMENT_ENGLISH_HINTS for word in words)
    return "en" if english > turkish else "tr"


_APOSTROPHE_SUFFIX_RE = re.compile(r"['’]\w+")
"""Kesmeyle bağlanan ek sözcük değildir: Türkçede sayıya ya da ada gelen ek ("6029278'in",
"FastReact'ı"), İngilizcede kısaltmanın kuyruğu ("isn't", "what's"; kuyruk zaten ipucu değil)."""
_TURKISH_QUESTION_RE = re.compile(r"m[iu](?:y[iu]m|s[iu]n|y[iu]z|s[iu]n[iu]z|d[iu]r|yd[iu])?")
"""Soru eki ailesi ("mi", "miyiz", "musunuz", "midir"); Türkçe harfsiz yazılışlarıyla."""
_MIN_ENGLISH_HINTS = 2
"""Tek bir İngilizce ipucu dili değiştirmez: Türkçe soruda "on", "in", "do" kendiliğinden geçer."""


def detect_language(text: str) -> str:
    """Yalnız Türkçe ve İngilizce ayırır; emin olunamazsa Türkçe döner. Soru Türkçe harfsiz
    yazılmış olabilir (tablet klavyesi), bu yüzden İngilizce için en az iki ipucu gerekir."""
    if _TURKISH_LETTERS_RE.search(text):
        return "tr"
    words = _WORD_RE.findall(_APOSTROPHE_SUFFIX_RE.sub("", text.lower()))
    english = sum(word in _ENGLISH_HINTS for word in words)
    turkish = sum(
        word in _TURKISH_HINTS or bool(_TURKISH_QUESTION_RE.fullmatch(word)) for word in words
    )
    return "en" if english >= _MIN_ENGLISH_HINTS and english > turkish else "tr"
