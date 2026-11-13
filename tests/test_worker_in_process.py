import asyncio
from collections.abc import Sequence
from typing import Any

from qdrant_client import AsyncQdrantClient

from apps.worker.indexing import LazyIndexer, SharedEncoders
from apps.worker.main import process_until_stopped
from visual_agent.domain.document import Chunk, ChunkKind, SourceLocation
from visual_agent.retrieval.qdrant_store import QdrantChunkStore


class FakeDense:
    size = 2

    def encode_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


class FakeSparse:
    def encode_documents(self, texts: Sequence[str]) -> list[dict[int, float]]:
        return [{1: 1.0} for _ in texts]


def _chunk(chunk_id: str) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id="a",
        kind=ChunkKind.TEXT,
        text="elma",
        title="Belge",
        location=SourceLocation(page=1),
    )


def test_encoders_are_loaded_once_for_search_and_indexing() -> None:
    loads: list[int] = []

    def load() -> tuple[Any, Any]:
        loads.append(1)
        return FakeDense(), FakeSparse()

    async def run() -> None:
        shared = SharedEncoders(load)
        await asyncio.gather(shared.get(), shared.get(), shared.get())

    asyncio.run(run())

    assert loads == [1]


def test_indexer_replaces_previous_vectors_of_the_document() -> None:
    async def run() -> list[str]:
        store = QdrantChunkStore(AsyncQdrantClient(":memory:"), "test")
        indexer = LazyIndexer(store, SharedEncoders(lambda: (FakeDense(), FakeSparse())))
        await indexer.index("a", [_chunk("a:0"), _chunk("a:1")])
        await indexer.index("a", [_chunk("a:2")])
        arms = await store.search([1.0, 0.0], {1: 1.0}, None, 10)
        await indexer.remove("b")
        return [item.chunk.chunk_id for item in arms[0]]

    assert asyncio.run(run()) == ["a:2"]


def test_in_process_worker_drains_the_queue_then_waits() -> None:
    queue = [True, True, False]
    calls: list[int] = []

    async def run() -> int:
        stop = asyncio.Event()

        async def process_next() -> bool:
            calls.append(1)
            if not queue:
                stop.set()
                return False
            return queue.pop(0)

        return await process_until_stopped(process_next, stop, poll_seconds=0.01)

    polls = asyncio.run(run())

    assert len(calls) == 4
    assert polls == 1


def test_in_process_worker_survives_a_failing_job() -> None:
    calls: list[int] = []

    async def run() -> None:
        stop = asyncio.Event()

        async def process_next() -> bool:
            calls.append(1)
            if len(calls) == 1:
                raise ConnectionError("veritabanı kilitli")
            stop.set()
            return False

        await process_until_stopped(process_next, stop, poll_seconds=0.01)

    asyncio.run(run())

    assert len(calls) == 2


def test_in_process_worker_stops_without_waiting_the_full_interval() -> None:
    async def run() -> int:
        stop = asyncio.Event()

        async def process_next() -> bool:
            asyncio.get_running_loop().call_later(0.01, stop.set)
            return False

        return await asyncio.wait_for(process_until_stopped(process_next, stop, 30.0), 2.0)

    assert asyncio.run(run()) == 0
