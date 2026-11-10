"""Kayıtlı ölçümü model önbelleğinden, yeni model isteği ya da belge vektörü olmadan değerlendirir.

Denetim ya da puanlama değişikliğinin etkisini maliyetsiz ölçmek içindir. Önbellekte olmayan
model isteği ağa gitmez, ıska sayılır; ıska varsa o soru güvenilmezdir.

    python -m evals.replay documents --rows evals/output/fastreact_tur1.json \\
        --work evals/output/fastreact/calisma --cache-dir evals/output/fastreact/answer-cache \\
        --output evals/output/fastreact/yeniden.json
    python -m evals.replay questions --set evals/output/set7 --work evals/output/run7-taban \\
        --output evals/output/yeniden7.json

documents: getirilen parçalar run_documents kaydından aynı sırayla geri verilir, arama yapılmaz.
questions: arama, --work altındaki indeksin geçici bir kopyasında yapılır (yalnız sorgu vektörü
hesaplanır); asıl indeks değişmez.
"""

import argparse
import asyncio
import json
import shutil
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx

from evals.answer_cache import CachingTransport
from evals.gold import GoldSet
from evals.index_cache import load_or_ingest
from evals.run_documents import catalog_of, question_row
from evals.run_questions import _full_run, gold_catalog, load_chunks, select_questions
from visual_agent.ask.clients import ask_deps, build_model_clients
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.orchestrator import answer_question
from visual_agent.catalog.identifiers import build_identifier_index
from visual_agent.domain.document import Chunk
from visual_agent.domain.result import Hit
from visual_agent.retrieval.hybrid import HybridRetriever
from visual_agent.retrieval.qdrant_store import QdrantChunkStore, open_client
from visual_agent.settings import Settings

_QUESTIONS_COLLECTION = "evaluation"


class RecordedRetriever:
    """Arama yapmaz; kayıttaki parçaları aynı sırayla ve skorla döndürür."""

    def __init__(self) -> None:
        self.hits: list[Hit] = []

    async def search(
        self,
        query: str,
        bm25_query: str,
        doc_ids: Sequence[str] | None,
        top_k: int,
        access: Sequence[str] | None = None,
    ) -> list[Hit]:
        return list(self.hits)


async def replay_rows(
    rows: Sequence[dict[str, Any]],
    chunks: dict[str, Chunk],
    deps: AskDeps,
    retriever: RecordedRetriever,
    transport: CachingTransport,
) -> list[dict[str, Any]]:
    """Her kayıtlı soru, kayıttaki parçalarla yeniden cevaplanır; ıska sayısı satıra yazılır."""
    replayed = []
    for row in rows:
        retriever.hits = [
            Hit(chunk=chunks[item["chunk_id"]], score=item["score"]) for item in row["retrieved"]
        ]
        counts, usage = transport.counts.snapshot(), transport.usage.snapshot()
        outcome = await answer_question(AskRequest(row["question"]), deps)
        delta = transport.counts.since(counts)
        new_row = question_row(
            {"id": row["id"], "question": row["question"]},
            outcome,
            0.0,
            delta,
            transport.usage.since(usage),
        )
        replayed.append({**new_row, "offline_misses": delta.misses})
    return replayed


def _offline(cache_dir: Path) -> CachingTransport:
    return CachingTransport(httpx.AsyncHTTPTransport(), cache_dir, offline=True)


def _api_key(settings: Settings) -> str:
    key = settings.openrouter_api_key
    if key is None or not key.get_secret_value():
        raise SystemExit("OpenRouter anahtarı yok (yalnız ZDR listesi için gerekir)")
    return key.get_secret_value()


async def replay_documents(arguments: argparse.Namespace) -> dict[str, Any]:
    settings = Settings()
    chunks, _ = load_or_ingest([], arguments.work)
    by_id = {chunk.chunk_id: chunk for items in chunks.values() for chunk in items}
    rows = json.loads(arguments.rows.read_text(encoding="utf-8"))
    transport = _offline(arguments.cache_dir)
    retriever = RecordedRetriever()
    async with httpx.AsyncClient(transport=transport) as http:
        clients = await build_model_clients(http, settings, _api_key(settings))
        flat = list(by_id.values())
        deps = ask_deps(catalog_of(chunks), build_identifier_index(flat), retriever, clients)
        replayed = await replay_rows(rows, by_id, deps, retriever, transport)
    arguments.output.write_text(json.dumps(replayed, ensure_ascii=False, indent=1), "utf-8")
    return {
        "questions": len(replayed),
        "cache_hits": transport.counts.hits,
        "offline_misses": transport.counts.misses,
        "cost_usd": 0.0,
    }


async def replay_questions(arguments: argparse.Namespace) -> dict[str, Any]:
    from visual_agent.retrieval.encoders import BgeM3Dense, Bm25Sparse

    settings = Settings()
    gold = GoldSet.model_validate_json((arguments.set / "gold.json").read_text(encoding="utf-8"))
    chunks = load_chunks(gold, arguments.set, arguments.work)
    flat = [chunk for items in chunks.values() for chunk in items]
    transport = _offline(arguments.cache_dir)
    with tempfile.TemporaryDirectory() as copy:
        index = Path(copy) / "qdrant"
        shutil.copytree(arguments.work / "qdrant", index)
        client = open_client("", str(index))
        try:
            store = QdrantChunkStore(client, _QUESTIONS_COLLECTION)
            retriever = HybridRetriever(BgeM3Dense(), Bm25Sparse(), store)
            async with httpx.AsyncClient(transport=transport) as http:
                clients = await build_model_clients(http, settings, _api_key(settings))
                deps = ask_deps(
                    gold_catalog(gold, chunks), build_identifier_index(flat), retriever, clients
                )
                summary = await _full_run(
                    select_questions(gold, None), gold, deps, arguments.output, transport.counts
                )
        finally:
            await client.close()
    return {
        **summary,
        "cache_hits": transport.counts.hits,
        "offline_misses": transport.counts.misses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kayıtlı ölçümü önbellekten yeniden değerlendirir."
    )
    modes = parser.add_subparsers(dest="mode", required=True)
    documents = modes.add_parser("documents", help="run_documents sonucunu yeniden değerlendirir")
    documents.add_argument("--rows", type=Path, required=True)
    documents.add_argument("--work", type=Path, required=True)
    documents.add_argument("--cache-dir", type=Path, required=True)
    documents.add_argument("--output", type=Path, required=True)
    questions = modes.add_parser(
        "questions", help="altın seti mevcut indeksle yeniden değerlendirir"
    )
    questions.add_argument("--set", type=Path, required=True)
    questions.add_argument("--work", type=Path, required=True)
    questions.add_argument("--cache-dir", type=Path, default=Path("evals/output/answer-cache"))
    questions.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    run = replay_documents if arguments.mode == "documents" else replay_questions
    json.dump(asyncio.run(run(arguments)), sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
