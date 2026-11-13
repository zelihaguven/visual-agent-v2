"""Kayıtlı run_documents ölçümünü model önbelleğinden, yeni model isteği ya da arama olmadan
değerlendirir.

Denetim ya da puanlama değişikliğinin etkisini maliyetsiz ölçmek içindir. Getirilen parçalar
kayıttan aynı sırayla geri verilir. Önbellekte olmayan model isteği ağa gitmez; soru "miss"
olur ve sonucu güvenilmezdir. Altın setler için: python -m evals.run_questions --offline.

    python -m evals.replay --rows evals/output/fastreact_tur1.json \\
        --work evals/output/fastreact/calisma --cache-dir evals/output/fastreact/answer-cache \\
        --output evals/output/fastreact/yeniden.json
"""

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx

from evals.answer_cache import CachingTransport
from evals.index_cache import read_chunks
from evals.run_documents import catalog_of, question_row
from visual_agent.ask.clients import ask_deps, build_model_clients
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.orchestrator import answer_question
from visual_agent.catalog.identifiers import build_identifier_index
from visual_agent.domain.document import Chunk
from visual_agent.domain.result import Hit
from visual_agent.settings import Settings


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
            offline=True,
        )
        replayed.append({**new_row, "offline_misses": delta.misses})
    return replayed


def _cached_chunks(work: Path) -> dict[str, list[Chunk]]:
    """Yeniden değerlendirme belge işlemez ve --work altına hiçbir şey yazmaz."""
    chunks = read_chunks(work)
    if chunks is None:
        raise SystemExit(
            f"{work} altında parça önbelleği (chunks.json) yok; önce ölçümü çalıştırın"
        )
    return chunks


def _offline(cache_dir: Path) -> CachingTransport:
    return CachingTransport(httpx.AsyncHTTPTransport(), cache_dir, offline=True)


def _api_key(settings: Settings) -> str:
    key = settings.openrouter_api_key
    if key is None or not key.get_secret_value():
        raise SystemExit("OpenRouter anahtarı yok (yalnız ZDR listesi için gerekir)")
    return key.get_secret_value()


async def replay_documents(arguments: argparse.Namespace) -> dict[str, Any]:
    settings = Settings()
    chunks = _cached_chunks(arguments.work)
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kayıtlı run_documents ölçümünü önbellekten yeniden değerlendirir."
    )
    parser.add_argument("--rows", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    json.dump(asyncio.run(replay_documents(arguments)), sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
