"""Yerel yoğun vektör ve BM25 ile hibrit arama."""

import asyncio
from collections.abc import Mapping, Sequence
from typing import Protocol

from visual_agent.domain.result import Hit
from visual_agent.retrieval.fusion import is_table_of_contents, rrf_fuse
from visual_agent.retrieval.qdrant_store import QdrantChunkStore

_PREFETCH_K = 30
_FUSED_K = 20


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
