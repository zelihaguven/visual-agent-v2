"""Tamamlanan soruda kullanıcının söylemediği bir değer olmamasını denetler."""

import re
from collections.abc import Iterable

from visual_agent.domain.conversation import MAX_QUESTION_CHARS
from visual_agent.verification.text import identifiers_in, normalize

_MARKED_TOKEN_RE = re.compile(r"(?<![\w-])[A-ZÇĞİÖŞÜ0-9][A-ZÇĞİÖŞÜ0-9_.,/-]*(?!\w)")
_WORD_RE = re.compile(r"[\w.,/-]+")
_TOKEN_EDGES = ".,/-"


def _words(text: str) -> set[str]:
    return {word.strip(_TOKEN_EDGES) for word in _WORD_RE.findall(normalize(text))}


def _marked_tokens(text: str) -> set[str]:
    """Rakam içeren ya da tamamı büyük harf olan sözcükler: kod, sayı, beden."""
    return {normalize(token).strip(_TOKEN_EDGES) for token in _MARKED_TOKEN_RE.findall(text)}


def is_grounded(rewritten: str, inputs: Iterable[str]) -> bool:
    if not rewritten.strip() or len(rewritten) > MAX_QUESTION_CHARS:
        return False
    sources = list(inputs)
    known_words = set().union(*(_words(source) for source in sources))
    known_identifiers = set().union(*(identifiers_in(source) for source in sources))
    return (
        identifiers_in(rewritten) <= known_identifiers and _marked_tokens(rewritten) <= known_words
    )
