import asyncio
from collections.abc import Sequence
from dataclasses import dataclass

import httpx
from qdrant_client import AsyncQdrantClient

from visual_agent.domain.document import Chunk, ChunkKind, SourceLocation
from visual_agent.generation.translate import (
    bm25_text,
    make_translator,
)
from visual_agent.retrieval.fusion import ScoredChunk, is_table_of_contents, rrf_fuse
from visual_agent.retrieval.hybrid import HybridRetriever
from visual_agent.retrieval.normalization import normalize_for_bm25
from visual_agent.retrieval.qdrant_store import QdrantChunkStore


def _chunk(chunk_id: str, doc_id: str, text: str, access: tuple[str, ...] = ("all",)) -> Chunk:
    return Chunk(
        chunk_id=chunk_id,
        doc_id=doc_id,
        kind=ChunkKind.TEXT,
        text=text,
        title="t",
        location=SourceLocation(page=1),
    )


def _scored(chunk_id: str, score: float) -> ScoredChunk:
    return ScoredChunk(chunk=_chunk(chunk_id, "d", chunk_id), score=score)


def test_rrf_rewards_presence_in_both_arms() -> None:
    fused = rrf_fuse(
        [_scored("a", 0.9), _scored("b", 0.8)], [_scored("b", 5.0), _scored("c", 4.0)], 3
    )

    assert [item.chunk.chunk_id for item in fused] == ["b", "a", "c"]


def test_rrf_order_is_deterministic_on_ties() -> None:
    first = rrf_fuse([_scored("b", 0.5)], [_scored("a", 1.0)], 2)
    second = rrf_fuse([_scored("b", 0.5)], [_scored("a", 1.0)], 2)

    assert [item.chunk.chunk_id for item in first] == [item.chunk.chunk_id for item in second]
    assert first[0].chunk.chunk_id == "b"


def test_table_of_contents_lines_are_detected() -> None:
    assert is_table_of_contents("5-5-1. Needle up/down ........ 32")
    assert not is_table_of_contents("TOTAL. ....... 1 | 00.00% açıklama metni uzun")
    assert not is_table_of_contents("Normal bir cümle.")


def test_bm25_normalization_keeps_codes_and_turkish_letters_searchable() -> None:
    assert normalize_for_bm25("E-050 İğne") == "E050 iğne"


class FakeDense:
    size = 2

    def encode_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [[1.0, 0.0] if "elma" in text else [0.0, 1.0] for text in texts]

    def encode_query(self, text: str) -> list[float]:
        return [1.0, 0.0] if "elma" in text else [0.0, 1.0]


class FakeSparse:
    def encode_documents(self, texts: Sequence[str]) -> list[dict[int, float]]:
        return [{hash(word) % 1000: 1.0 for word in text.split()} for text in texts]

    def encode_query(self, text: str) -> dict[int, float]:
        return {hash(word) % 1000: 1.0 for word in text.split()}


async def _indexed_store() -> QdrantChunkStore:
    store = QdrantChunkStore(AsyncQdrantClient(":memory:"), "test")
    await store.ensure_collection(dense_size=2)
    chunks = [
        _chunk("1", "a", "elma tablosu"),
        _chunk("2", "b", "armut kodu"),
        _chunk("3", "a", "elma suyu"),
    ]
    dense, sparse = FakeDense(), FakeSparse()
    texts = [chunk.embed_text for chunk in chunks]
    await store.upsert(
        chunks,
        ("all",),
        dense.encode_documents(texts),
        sparse.encode_documents(texts),
    )
    return store


def test_store_searches_and_filters_by_document() -> None:
    async def run() -> list[str]:
        store = await _indexed_store()
        retriever = HybridRetriever(FakeDense(), FakeSparse(), store)
        hits = await retriever.search("elma", "elma", ("a",), 5)
        return [hit.chunk.doc_id for hit in hits]

    assert set(asyncio.run(run())) == {"a"}


def test_chunks_survive_the_round_trip() -> None:
    async def run() -> Chunk:
        store = await _indexed_store()
        hits = await HybridRetriever(FakeDense(), FakeSparse(), store).search(
            "armut", "armut", None, 1
        )
        return hits[0].chunk

    found = asyncio.run(run())

    assert found.location.page == 1
    assert found.kind is ChunkKind.TEXT


def test_access_filter_hides_other_groups() -> None:
    async def run() -> list[Chunk]:
        store = QdrantChunkStore(AsyncQdrantClient(":memory:"), "test")
        await store.ensure_collection(dense_size=2)
        await store.upsert([_chunk("1", "a", "elma")], ("ik",), [[1.0, 0.0]], [{1: 1.0}])
        allowed = await store.search([1.0, 0.0], {1: 1.0}, None, ("kalite",), 5)
        return [item.chunk for arm in allowed for item in arm]

    assert asyncio.run(run()) == []


def test_delete_document_removes_its_chunks() -> None:
    async def run() -> list[str]:
        store = await _indexed_store()
        await store.delete_document("a")
        hits = await HybridRetriever(FakeDense(), FakeSparse(), store).search(
            "elma", "elma", None, 5
        )
        return [hit.chunk.doc_id for hit in hits]

    assert "a" not in asyncio.run(run())


def test_bm25_text_joins_translations_and_falls_back() -> None:
    assert bm25_text({"en": "inseam", "tr": "iç paça"}, "soru") == "inseam iç paça"
    assert bm25_text({}, "soru") == "soru"


@dataclass
class _Recorder:
    body: dict[str, object] | None = None


def test_translator_sends_only_the_question_with_zdr() -> None:
    import json

    recorder = _Recorder()

    def handler(request: httpx.Request) -> httpx.Response:
        recorder.body = json.loads(request.content)
        message = {"message": {"content": '{"en": "inseam"}'}}
        return httpx.Response(200, json={"choices": [message]})

    async def run() -> str:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            translator = make_translator(
                http,
                base_url="https://router.test/api/v1",
                api_key="k",
                model="m",
                providers=("alpha",),
                ignored_providers=(),
            )
            return await translator("iç paça", "tr", ["en"])

    assert asyncio.run(run()) == "inseam"
    assert recorder.body is not None
    provider = recorder.body["provider"]
    assert isinstance(provider, dict)
    assert provider["zdr"] is True and provider["data_collection"] == "deny"
    assert "iç paça" in str(recorder.body["messages"])
