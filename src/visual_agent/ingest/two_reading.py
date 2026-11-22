"""OCR katmanı seçimi ve eski OCR yolunda iki okumanın karşılaştırması."""

from collections.abc import Iterable
from enum import StrEnum

from visual_agent.ingest.page_reader import count_mismatches, value_tokens

_SCORE_TOLERANCE = 0.02
_STRIP_CHARACTERS = ".,;:()[]{}\"'”“’‘«»|_"


class LayerChoice(StrEnum):
    NEW = "new"
    OLD = "old"


def choose_layer(old_score: float, new_score: float) -> LayerChoice:
    """Yeni OCR katmanı eskisinden belirgin kötüyse eski katman kalır."""
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


def unconfirmed_tokens(primary: str, second: str, *more: str) -> list[str]:
    """Birinci okumanın, ikinci okumada aynı sayıda geçmeyen sayı ve kod parçaları; okuyucu
    yolundaki kuralla (count_mismatches): harf-rakam eşdeğerliği yok ("B12" "812" değildir),
    rakamsız kodlar da denetlenir, virgül ve nokta farklıdır (karar 0008). Dönen parça birinci
    okumanın kendi yazımıdır: belirsiz değer öğenin metninde aynı yazımla aranır."""
    mismatched = set(count_mismatches(primary, second, *more))
    unconfirmed = []
    for raw in primary.split():
        token = raw.strip(_STRIP_CHARACTERS)
        if token and any(part in mismatched for part in value_tokens(raw)):
            unconfirmed.append(token)
    return list(dict.fromkeys(unconfirmed))
