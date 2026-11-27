"""Yerel yoğun vektör ve BM25 ile hibrit arama; kollar belirli sırayla birleştirilir."""

import asyncio
import re
from collections.abc import Mapping, Sequence
from typing import Protocol

from visual_agent.domain.document import Chunk
from visual_agent.domain.result import Hit
from visual_agent.retrieval.qdrant_store import QdrantChunkStore, ScoredChunk

_PREFETCH_K = 30
_FUSED_K = 20
_RRF_K = 2
_MIN_TOC_LEADERS = 2
_TOC_LEADER_RE = re.compile(r"\.{5,}\s*\d+")
_TOC_LINE_RE = re.compile(r"\s*[\w\-. ()/]{3,80}?\s*\.{5,}\s*\d+\s*")


def is_table_of_contents(text: str) -> bool:
    return len(_TOC_LEADER_RE.findall(text)) >= _MIN_TOC_LEADERS or bool(
        _TOC_LINE_RE.fullmatch(text)
    )


def rrf_fuse(
    dense: Sequence[ScoredChunk], sparse: Sequence[ScoredChunk], limit: int
) -> list[ScoredChunk]:
    """Eşitlikte önce dense skoru, sonra parça kimliği belirler; sonuç her koşuda aynıdır."""
    fused: dict[str, float] = {}
    chunks: dict[str, Chunk] = {}
    for arm in (dense, sparse):
        for rank, item in enumerate(arm):
            chunk_id = item.chunk.chunk_id
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (rank + _RRF_K)
            chunks.setdefault(chunk_id, item.chunk)
    dense_scores = {item.chunk.chunk_id: item.score for item in dense}
    order = sorted(
        fused,
        key=lambda chunk_id: (
            -fused[chunk_id],
            -dense_scores.get(chunk_id, float("-inf")),
            chunk_id,
        ),
    )
    return [ScoredChunk(chunks[chunk_id], fused[chunk_id]) for chunk_id in order[:limit]]


class DenseEncoder(Protocol):
    def encode_query(self, text: str) -> list[float]: ...


class SparseEncoder(Protocol):
    def encode_query(self, text: str) -> Mapping[int, float]: ...


class HybridRetriever:
    def __init__(self, dense: DenseEncoder, sparse: SparseEncoder, store: QdrantChunkStore) -> None:
        self._dense = dense
        self._sparse = sparse
        self._store = store

    async def search(
        self,
        query: str,
        bm25_query: str,
        doc_ids: Sequence[str] | None,
        top_k: int,
    ) -> list[Hit]:
        dense_vector, sparse_vector = await asyncio.gather(
            asyncio.to_thread(self._dense.encode_query, query),
            asyncio.to_thread(self._sparse.encode_query, bm25_query),
        )
        dense_arm, sparse_arm = await self._store.search(
            dense_vector, sparse_vector, doc_ids, _PREFETCH_K
        )
        fused = rrf_fuse(dense_arm, sparse_arm, _FUSED_K)
        kept = [item for item in fused if not is_table_of_contents(item.chunk.text)]
        return [Hit(chunk=item.chunk, score=item.score) for item in kept[:top_k]]
