"""OCR katmanı seçimi ve iki okumanın sayısal karşılaştırması."""

import re
from collections.abc import Iterable
from enum import StrEnum

from visual_agent.ingest.text_layer import PageKind

OCR_MIN_SCORE = 0.85
_SCORE_TOLERANCE = 0.02
_CONFUSABLE = str.maketrans(
    {
        "/": "1",
        "l": "1",
        "I": "1",
        "i": "1",
        "|": "1",
        "!": "1",
        "]": "1",
        "S": "5",
        "s": "5",
        "O": "0",
        "o": "0",
        "B": "8",
        "Z": "2",
        "≥": "~",
        "±": "~",
        "+": "~",
    }
)
_STRIP_CHARACTERS = ".,;:()[]{}\"'”“’‘«»|_"


class LayerChoice(StrEnum):
    ORIGINAL = "original"
    NEW = "new"
    OLD = "old"
    IMAGE_ONLY = "image_only"


def choose_layer(kind: PageKind, old_score: float, new_score: float) -> LayerChoice:
    if kind is PageKind.NONE:
        return LayerChoice.NEW if new_score >= OCR_MIN_SCORE else LayerChoice.IMAGE_ONLY
    if new_score < old_score - _SCORE_TOLERANCE:
        return LayerChoice.OLD
    return LayerChoice.NEW


def page_ranges(pages: Iterable[int]) -> str:
    ordered = sorted(set(pages))
    ranges: list[str] = []
    start = previous = ordered[0]
    for page in [*ordered[1:], None]:
        if page is not None and page == previous + 1:
            previous = page
            continue
        ranges.append(str(start) if start == previous else f"{start}-{previous}")
        if page is not None:
            start = previous = page
    return ",".join(ranges)


def contains_token(text: str, token: str) -> bool:
    """Belirsiz değer yalnız tam değer olarak geçiyorsa eşleşir ("4", "74,5" içinde sayılmaz)."""
    return re.search(rf"(?<![\w.,-]){re.escape(token)}(?![\w,-]|\.\d)", text) is not None


def _token_key(token: str) -> str:
    return token.strip(_STRIP_CHARACTERS).replace(",", ".").translate(_CONFUSABLE)


def unconfirmed_tokens(primary: str, second: str) -> list[str]:
    """Birinci okumadaki, ikinci okumada eşi olmayan sayı içeren diziler."""
    keys = {_token_key(token) for token in second.split()}
    joined = "".join(second.split()).translate(_CONFUSABLE)
    unconfirmed = []
    for token in primary.split():
        if not re.search(r"\d", token):
            continue
        key = _token_key(token)
        spaced_differently = any(character.isalpha() for character in token) and key in joined
        if key not in keys and not spaced_differently:
            unconfirmed.append(token.strip(_STRIP_CHARACTERS))
    return unconfirmed
