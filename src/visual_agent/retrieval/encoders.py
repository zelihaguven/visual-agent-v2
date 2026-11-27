"""CPU'da çalışan yerel kodlayıcılar. Modeller ilk kullanımda yüklenir."""

import os
import re
from collections.abc import Sequence
from typing import Any

DENSE_MODEL = "BAAI/bge-m3"
_DENSE_SIZE = 1024
_MAX_SEQUENCE_LENGTH = 512
_BATCH_SIZE = 16
BM25_MODEL = "Qdrant/bm25"
# Kalıcı klasör: geçici klasör temizlenirse model internetten yeniden inmek zorunda kalırdı.
# FASTEMBED_CACHE_PATH verilirse o klasör kullanılır.
BM25_CACHE_DIRECTORY = "data/models/fastembed"


_TURKISH_FOLD = str.maketrans({"İ": "i", "ı": "i", "I": "i"})
_HYPHENS = str.maketrans({"\u2010": "-", "\u2011": "-"})
"""U+2010 ve U+2011 (Word'ün bölünmez tiresi) kısa tiredir; doğrulamadaki okumayla aynı."""
_CODE_HYPHEN_RE = re.compile(r"\b([A-Za-z]{1,4})[-–](\d)")


def normalize_for_bm25(text: str) -> str:
    """BM25 için belge ve sorguya aynı uygulanan biçim: tireli kodları birleştirir ve Türkçe
    I/İ harflerini sadeleştirir."""
    return _CODE_HYPHEN_RE.sub(r"\1\2", text.translate(_HYPHENS)).translate(_TURKISH_FOLD)


def bm25_cache_directory() -> str:
    return os.environ.get("FASTEMBED_CACHE_PATH") or BM25_CACHE_DIRECTORY


class BgeM3Dense:
    size = _DENSE_SIZE

    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._model: Any = SentenceTransformer(DENSE_MODEL, device="cpu")
        self._model.max_seq_length = _MAX_SEQUENCE_LENGTH

    def _encode(self, texts: Sequence[str]) -> list[list[float]]:
        vectors = self._model.encode(
            list(texts), batch_size=_BATCH_SIZE, normalize_embeddings=True, show_progress_bar=False
        )
        return [[float(value) for value in vector] for vector in vectors]

    def encode_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._encode(texts)

    def encode_query(self, text: str) -> list[float]:
        return self._encode([text])[0]


def _to_mapping(embedding: Any) -> dict[int, float]:
    return {
        int(index): float(value)
        for index, value in zip(embedding.indices, embedding.values, strict=True)
    }


class Bm25Sparse:
    def __init__(self) -> None:
        from fastembed.sparse.bm25 import Bm25

        self._model: Any = Bm25(BM25_MODEL, cache_dir=bm25_cache_directory())

    def encode_documents(self, texts: Sequence[str]) -> list[dict[int, float]]:
        normalized = [normalize_for_bm25(text) for text in texts]
        return [_to_mapping(embedding) for embedding in self._model.embed(normalized)]

    def encode_query(self, text: str) -> dict[int, float]:
        return _to_mapping(next(iter(self._model.query_embed([normalize_for_bm25(text)]))))
