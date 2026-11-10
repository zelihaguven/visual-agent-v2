import asyncio
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx
from qdrant_client import AsyncQdrantClient

from evals.answer_cache import CacheCounts, CachingTransport, Usage
from evals.index_cache import chunks_fingerprint, ensure_index, load_or_ingest
from evals.run_documents import ask_all, folder_documents, question_row
from tests.test_ask_pipeline import CHUNKS, FakeClient, FakeRetriever, answer_payload, make_deps
from visual_agent.ask.language import document_language
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.document import Chunk, ChunkKind, SourceLocation
from visual_agent.domain.result import (
    Answered,
    AnsweredItem,
    AskOutcome,
    Citation,
    Clarify,
    Hit,
    NotFound,
)
from visual_agent.retrieval.qdrant_store import QdrantChunkStore

QUESTION = {"id": "1", "question": "How do I exit?", "expected": "yok sayılır"}


def _chunk(doc_id: str, index: int, text: str = "Close the planning boards first.") -> Chunk:
    return Chunk(
        chunk_id=f"{doc_id}:{index}",
        doc_id=doc_id,
        kind=ChunkKind.TEXT,
        text=text,
        title=Path(doc_id).stem,
        location=SourceLocation(),
    )


def _citation(chunk: Chunk) -> Citation:
    return Citation(
        chunk_id=chunk.chunk_id, doc_id=chunk.doc_id, title=chunk.title, location=chunk.location
    )


def test_row_keeps_answer_retrieved_chunks_sources_and_usage() -> None:
    first, second = _chunk("00_Exit.md", 0, "x" * 300), _chunk("00_Main_Menu.md", 3)
    outcome = AskOutcome(
        result=Answered(
            status=VerificationStatus.PARTIAL,
            items=(
                AnsweredItem(text="Kapatın.", citations=(_citation(first),), verified=True),
                AnsweredItem(text="Uydurma.", citations=(_citation(second),), verified=False),
            ),
        ),
        hits=(Hit(chunk=first, score=0.0328), Hit(chunk=second, score=0.0161)),
        timings={"retrieve": 0.12345},
        provider="deepinfra",
        provider_attempts=1,
        question="How do I exit?",
    )

    row = question_row(QUESTION, outcome, 2.5, CacheCounts(0, 4), Usage(4, 900, 80, 0.0007))

    assert row["answer"]["status"] == "partial"
    assert [(h["rank"], h["doc_id"], h["score"]) for h in row["retrieved"]] == [
        (1, "00_Exit.md", 0.0328),
        (2, "00_Main_Menu.md", 0.0161),
    ]
    assert len(row["retrieved"][0]["text"]) == 200
    assert [s["doc_id"] for s in row["shown_sources"]] == ["00_Exit.md"]
    assert [s["doc_id"] for s in row["cited_sources"]] == ["00_Exit.md", "00_Main_Menu.md"]
    assert row["shown_sources"][0]["location"] == {"boxes": []}
    assert (row["seconds"], row["prompt_tokens"], row["cost_usd"]) == (2.5, 900, 0.0007)
    assert row["cache"] == "live"
    assert "expected" not in row


def test_row_from_cache_has_no_time_and_keeps_other_result_kinds() -> None:
    clarify = AskOutcome(result=Clarify(question="Hangi belge?"), timings={})
    not_found = AskOutcome(result=NotFound(reason="SAP belgelerde geçmiyor."), timings={})

    cached = question_row(QUESTION, clarify, 0.01, CacheCounts(3, 0), Usage(3, 10, 1, 0.0))
    missing = question_row(QUESTION, not_found, 1.0, CacheCounts(0, 1), Usage(1))

    assert (cached["seconds"], cached["answer"]) == (
        None,
        {"kind": "Clarify", "question": "Hangi belge?"},
    )
    assert missing["answer"] == {"kind": "NotFound", "reason": "SAP belgelerde geçmiyor."}
    assert missing["shown_sources"] == []


def test_language_and_fingerprint() -> None:
    english = [_chunk("a.md", 0, "Planning boards must be closed before you can exit the program.")]

    assert document_language(english) == "en"
    assert document_language([]) == "tr"
    assert chunks_fingerprint(english) == chunks_fingerprint(list(english))
    assert chunks_fingerprint(english) != chunks_fingerprint([_chunk("a.md", 0, "farklı")])


def test_saved_chunks_are_reused_without_processing_again(tmp_path: Path) -> None:
    (tmp_path / "chunks.json").write_text(
        json.dumps({"a.md": [_chunk("a.md", 0).model_dump(mode="json")]}), encoding="utf-8"
    )
    (tmp_path / "ingest.json").write_text(json.dumps({"files": 1, "errors": {}}), encoding="utf-8")

    chunks, manifest = load_or_ingest([], tmp_path)

    assert [c.chunk_id for c in chunks["a.md"]] == ["a.md:0"]
    assert manifest["files"] == 1


class CountingDense:
    size = 2

    def __init__(self) -> None:
        self.calls = 0

    def encode_documents(self, texts: Sequence[str]) -> list[list[float]]:
        self.calls += 1
        return [[1.0, 0.0] for _ in texts]


class FakeSparse:
    def encode_documents(self, texts: Sequence[str]) -> list[dict[int, float]]:
        return [{1: 1.0} for _ in texts]


def test_vectors_are_not_rebuilt_while_chunks_are_unchanged(tmp_path: Path) -> None:
    chunks = [_chunk("a.md", 0), _chunk("b.md", 0)]
    dense = CountingDense()

    async def run() -> list[Any]:
        store = QdrantChunkStore(AsyncQdrantClient(":memory:"), "test")
        first = await ensure_index(chunks, dense, FakeSparse(), store, tmp_path)
        again = await ensure_index(chunks, dense, FakeSparse(), store, tmp_path)
        changed = await ensure_index(chunks[:1], dense, FakeSparse(), store, tmp_path)
        return [first, again, changed]

    first, again, changed = asyncio.run(run())

    assert first == again and first["chunks"] == 2
    assert changed["chunks"] == 1
    assert dense.calls == 2


def test_answered_questions_are_read_back_instead_of_asked_again(tmp_path: Path) -> None:
    output = tmp_path / "sonuc.json"
    client = FakeClient(answer_payload("76,5"))
    deps = make_deps(client, FakeRetriever(hits=[CHUNKS[0]]))
    transport = CachingTransport(httpx.AsyncHTTPTransport(), tmp_path / "cache")
    questions = [{"id": "1", "question": "iç paça nedir"}, {"id": "2", "question": "bel nedir"}]

    first = asyncio.run(ask_all(questions[:1], deps, transport, output))
    both = asyncio.run(ask_all(questions, deps, transport, output))

    assert [row["id"] for row in first] == ["1"]
    assert [row["id"] for row in both] == ["1", "2"]
    assert len(client.calls) == 2
    assert [row["id"] for row in json.loads(output.read_text(encoding="utf-8"))] == ["1", "2"]


def test_saved_chunks_without_a_report_are_still_reused(tmp_path: Path) -> None:
    (tmp_path / "chunks.json").write_text(
        json.dumps({"a.md": [_chunk("a.md", 0).model_dump(mode="json")]}), encoding="utf-8"
    )

    chunks, manifest = load_or_ingest([], tmp_path)

    assert [c.chunk_id for c in chunks["a.md"]] == ["a.md:0"]
    assert manifest == {}


def test_each_file_in_a_folder_is_a_document_named_after_it(tmp_path: Path) -> None:
    for name in ("b.md", "a.md"):
        (tmp_path / name).write_text("x", encoding="utf-8")
    (tmp_path / "alt").mkdir()

    documents = folder_documents(tmp_path)

    assert [(path.name, meta.doc_id, meta.title) for path, meta in documents] == [
        ("a.md", "a.md", "a"),
        ("b.md", "b.md", "b"),
    ]
