"""Parçaları vektörleyip Qdrant'a yazar. Modeller ilk işte yüklenir."""

import asyncio
from collections.abc import Callable, Sequence
from typing import Any

from visual_agent.domain.document import Chunk
from visual_agent.retrieval.qdrant_store import QdrantChunkStore

Encoders = tuple[Any, Any]


def _load_encoders() -> Encoders:
    from visual_agent.retrieval.encoders import BgeM3Dense, Bm25Sparse

    return BgeM3Dense(), Bm25Sparse()


class SharedEncoders:
    """Arama ve indeksleme aynı süreçteyse modeller bir kez yüklenir."""

    def __init__(self, load: Callable[[], Encoders] = _load_encoders) -> None:
        self._load = load
        self._encoders: Encoders | None = None
        self._lock = asyncio.Lock()

    async def get(self) -> Encoders:
        async with self._lock:
            if self._encoders is None:
                self._encoders = await asyncio.to_thread(self._load)
            return self._encoders


class LazyIndexer:
    def __init__(self, store: QdrantChunkStore, encoders: SharedEncoders) -> None:
        self._store = store
        self._encoders = encoders

    async def index(self, doc_id: str, access: Sequence[str], chunks: Sequence[Chunk]) -> None:
        dense, sparse = await self._encoders.get()
        await self._store.ensure_collection(dense.size)
        texts = [chunk.embed_text for chunk in chunks]
        dense_vectors, sparse_vectors = await asyncio.gather(
            asyncio.to_thread(dense.encode_documents, texts),
            asyncio.to_thread(sparse.encode_documents, texts),
        )
        await self._store.delete_document(doc_id)
        await self._store.upsert(chunks, access, dense_vectors, sparse_vectors)

    async def remove(self, doc_id: str) -> None:
        await self._store.delete_document(doc_id)
