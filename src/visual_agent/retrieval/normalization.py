"""BM25 için belge ve sorguya aynı uygulanan metin biçimi."""

import re

_TURKISH_FOLD = str.maketrans({"İ": "i", "ı": "i", "I": "i"})
_HYPHENS = str.maketrans({"\u2010": "-", "\u2011": "-"})
"""U+2010 ve U+2011 (Word'ün bölünmez tiresi) kısa tiredir; doğrulamadaki okumayla aynı."""
_CODE_HYPHEN_RE = re.compile(r"\b([A-Za-z]{1,4})[-–](\d)")


def normalize_for_bm25(text: str) -> str:
    """Tireli kodları birleştirir ve Türkçe I/İ harflerini sadeleştirir."""
    return _CODE_HYPHEN_RE.sub(r"\1\2", text.translate(_HYPHENS)).translate(_TURKISH_FOLD)
