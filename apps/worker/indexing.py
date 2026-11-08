"""Parçaları vektörleyip Qdrant'a yazar. Modeller ilk işte yüklenir."""

import asyncio
from collections.abc import Sequence
from typing import Any

from visual_agent.domain.document import Chunk
from visual_agent.retrieval.qdrant_store import QdrantChunkStore


class LazyIndexer:
    def __init__(self, store: QdrantChunkStore) -> None:
        self._store = store
        self._encoders: tuple[Any, Any] | None = None

    def _load_encoders(self) -> tuple[Any, Any]:
        from visual_agent.retrieval.encoders import BgeM3Dense, Bm25Sparse

        return BgeM3Dense(), Bm25Sparse()

    async def index(self, doc_id: str, access: Sequence[str], chunks: Sequence[Chunk]) -> None:
        if self._encoders is None:
            self._encoders = await asyncio.to_thread(self._load_encoders)
        dense, sparse = self._encoders
        await self._store.ensure_collection(dense.size)
        texts = [chunk.embed_text for chunk in chunks]
        dense_vectors, sparse_vectors = await asyncio.gather(
            asyncio.to_thread(dense.encode_documents, texts),
            asyncio.to_thread(sparse.encode_documents, texts),
        )
        await self._store.delete_document(doc_id)
        await self._store.upsert(chunks, access, dense_vectors, sparse_vectors)
