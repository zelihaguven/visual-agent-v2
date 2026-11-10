"""Önbellekten yeniden değerlendirme: ağa gitmez, kayıtlı parçaları aynı sırayla kullanır."""

import asyncio
from dataclasses import replace
from pathlib import Path

import httpx
import pytest

from evals.answer_cache import CacheCounts, CachingTransport, OfflineMiss
from evals.replay import RecordedRetriever, replay_rows
from tests.test_ask_pipeline import CHUNKS, FakeClient, answer_payload, make_deps

URL = "https://openrouter.ai/api/v1/chat/completions"


def test_offline_cache_never_sends_a_missing_model_request(tmp_path: Path) -> None:
    sent: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(200, json={"data": []})

    async def run() -> CacheCounts:
        transport = CachingTransport(httpx.MockTransport(handle), tmp_path, offline=True)
        async with httpx.AsyncClient(transport=transport) as client:
            with pytest.raises(OfflineMiss):
                await client.post(URL, json={"soru": "bel"})
            await client.get("https://openrouter.ai/api/v1/endpoints/zdr")
        return transport.counts

    counts = asyncio.run(run())

    assert counts == CacheCounts(hits=0, misses=1)
    assert [request.method for request in sent] == ["GET"]


def test_recorded_chunks_are_returned_in_the_recorded_order(tmp_path: Path) -> None:
    retriever = RecordedRetriever()
    deps = replace(make_deps(FakeClient(answer_payload("76,5"))), retriever=retriever)
    by_id = {chunk.chunk_id: chunk for chunk in CHUNKS}
    first, second = CHUNKS[1], CHUNKS[0]
    rows = [
        {
            "id": "1",
            "question": "iç paça nedir",
            "retrieved": [
                {"chunk_id": first.chunk_id, "score": 0.9},
                {"chunk_id": second.chunk_id, "score": 0.5},
            ],
        }
    ]
    transport = CachingTransport(httpx.MockTransport(lambda r: httpx.Response(500)), tmp_path)

    replayed = asyncio.run(replay_rows(rows, by_id, deps, retriever, transport))

    assert [(r["chunk_id"], r["score"]) for r in replayed[0]["retrieved"]] == [
        (first.chunk_id, 0.9),
        (second.chunk_id, 0.5),
    ]
    assert replayed[0]["offline_misses"] == 0
    assert replayed[0]["id"] == "1"
