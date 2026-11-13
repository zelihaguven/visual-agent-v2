"""CPU'da çalışan yerel kodlayıcılar. Modeller ilk kullanımda yüklenir."""

import os
from collections.abc import Sequence
from typing import Any

from visual_agent.retrieval.normalization import normalize_for_bm25

DENSE_MODEL = "BAAI/bge-m3"
_DENSE_SIZE = 1024
_MAX_SEQUENCE_LENGTH = 512
_BATCH_SIZE = 16
BM25_MODEL = "Qdrant/bm25"
# Kalıcı klasör: geçici klasör temizlenirse model internetten yeniden inmek zorunda kalırdı.
# Docker FASTEMBED_CACHE_PATH ile kendi birimini verir.
BM25_CACHE_DIRECTORY = "data/models/fastembed"


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
