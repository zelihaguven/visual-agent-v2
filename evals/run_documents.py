"""Bir klasördeki belgeleri ayrı bir indekse alır ve bir soru listesini bir kez sorar.

    python -m evals.run_documents --documents KLASOR --questions sorular.json \\
        --work evals/output/calisma --output evals/output/sonuc.json

- Her dosya bir belgedir: doc_id dosya adı, başlık dosya adının gövdesi, dil bilinmiyor
  (yüklemedeki gibi; ilk OCR tur+eng).
- İndeks --work altında kendi gömülü Qdrant klasöründedir; uygulamanın indeksine dokunmaz.
- Parçalar ve vektörler bir kez üretilir; tekrar çalıştırmada indeks yeniden kurulmaz.
- Model cevapları önbellektedir; sonuç dosyasında olan soru yeniden sorulmaz.
- Soru dosyası: [{"id": "...", "question": "..."}]. Başka alanlar yok sayılır.

Ölçüm içindir; cevapları puanlamaz, ek model çağrısı yapmaz.
"""

import argparse
import asyncio
import json
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx

from evals.answer_cache import CacheCounts, CachingTransport, Usage
from evals.index_cache import Documents, ensure_index, load_or_ingest
from evals.run_questions import cache_label
from visual_agent.ask.clients import ask_deps, build_model_clients
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.language import document_language
from visual_agent.ask.orchestrator import answer_question
from visual_agent.catalog.identifiers import build_identifier_index
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.domain.document import UNDETECTED_LANGUAGE, Chunk, DocumentMeta
from visual_agent.domain.result import Answered, AskOutcome, Clarify, NotFound
from visual_agent.retrieval.hybrid import HybridRetriever
from visual_agent.retrieval.qdrant_store import COLLECTION, QdrantChunkStore, open_client
from visual_agent.settings import Settings

PREVIEW_CHARS = 200


def folder_documents(folder: Path) -> Documents:
    """Her dosya bir belge, yüklemedeki gibi: doc_id dosya adı, başlık dosya adının gövdesi,
    dil bilinmiyor (ilk OCR tur+eng)."""
    return [
        (path, DocumentMeta(doc_id=path.name, title=path.stem, language=UNDETECTED_LANGUAGE))
        for path in sorted(item for item in folder.iterdir() if item.is_file())
    ]


def _citations(result: Answered, verified_only: bool) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for item in result.items:
        if verified_only and not item.verified:
            continue
        for citation in item.citations:
            seen.setdefault(
                citation.chunk_id,
                {
                    "doc_id": citation.doc_id,
                    "chunk_id": citation.chunk_id,
                    "title": citation.title,
                    "location": citation.location.model_dump(mode="json", exclude_none=True),
                },
            )
    return list(seen.values())


def _answer(outcome: AskOutcome) -> dict[str, Any]:
    result = outcome.result
    answer: dict[str, Any] = {"kind": type(result).__name__}
    if isinstance(result, Answered):
        answer["status"] = result.status.value
        answer["items"] = [
            {"text": item.text, "verified": item.verified, "problems": list(item.problems)}
            for item in result.items
        ]
        answer["problems"] = list(result.problems)
    elif isinstance(result, Clarify):
        answer["question"] = result.question
    elif isinstance(result, NotFound):
        answer["reason"] = result.reason
    else:
        answer["detail"] = result.model_dump(mode="json")
    return answer


def question_row(
    question: dict[str, Any],
    outcome: AskOutcome,
    seconds: float,
    counts: CacheCounts,
    usage: Usage,
    offline: bool = False,
) -> dict[str, Any]:
    """Ham sonuç: cevap, getirilen parçalar, gösterilen kaynaklar, süre, token ve maliyet."""
    result = outcome.result
    label = cache_label(counts, offline)
    return {
        "id": question["id"],
        "question": question["question"],
        "resolved_question": outcome.question,
        "answer": _answer(outcome),
        "retrieved": [
            {
                "rank": rank,
                "doc_id": hit.chunk.doc_id,
                "chunk_id": hit.chunk.chunk_id,
                "score": round(hit.score, 6),
                "text": hit.chunk.text[:PREVIEW_CHARS],
            }
            for rank, hit in enumerate(outcome.hits, start=1)
        ],
        "shown_sources": _citations(result, True) if isinstance(result, Answered) else [],
        "cited_sources": _citations(result, False) if isinstance(result, Answered) else [],
        "seconds": round(seconds, 3) if label == "live" else None,
        "timings": {k: round(v, 3) for k, v in outcome.timings.items()},
        "cache": label,
        "model_requests": usage.requests,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "cost_usd": round(usage.cost_usd, 6),
        "provider": outcome.provider,
        "provider_attempts": outcome.provider_attempts,
    }


def load_rows(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


async def ask_all(
    questions: Sequence[dict[str, Any]],
    deps: AskDeps,
    transport: CachingTransport,
    output: Path,
) -> list[dict[str, Any]]:
    """Sonuç dosyasında olan soru yeniden sorulmaz; her sorudan sonra dosya yazılır."""
    rows = load_rows(output)
    done = {row["id"] for row in rows}
    for question in questions:
        if question["id"] in done:
            continue
        counts, usage = transport.counts.snapshot(), transport.usage.snapshot()
        started = time.perf_counter()
        outcome = await answer_question(AskRequest(question["question"]), deps)
        seconds = time.perf_counter() - started
        rows.append(
            question_row(
                question,
                outcome,
                seconds,
                transport.counts.since(counts),
                transport.usage.since(usage),
            )
        )
        output.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"soru {question['id']}: {rows[-1]['answer']['kind']}", file=sys.stderr, flush=True)
    return rows


def catalog_of(chunks: dict[str, list[Chunk]]) -> DocumentCatalog:
    catalog = DocumentCatalog()
    for doc_id, items in chunks.items():
        title = items[0].title if items else Path(doc_id).stem
        catalog.add(DocumentMeta(doc_id=doc_id, title=title, language=document_language(items)))
    return catalog


async def run(arguments: argparse.Namespace) -> dict[str, Any]:
    from visual_agent.retrieval.encoders import BgeM3Dense, Bm25Sparse

    settings = Settings()
    key = settings.openrouter_api_key
    if key is None or not key.get_secret_value():
        raise SystemExit("OpenRouter anahtarı yok")
    arguments.work.mkdir(parents=True, exist_ok=True)
    chunks, manifest = load_or_ingest(folder_documents(arguments.documents), arguments.work)
    flat = [chunk for items in chunks.values() for chunk in items]
    questions = json.loads(arguments.questions.read_text(encoding="utf-8"))
    dense, sparse = BgeM3Dense(), Bm25Sparse()
    client = open_client("", str(arguments.work / "qdrant"))
    try:
        store = QdrantChunkStore(client, COLLECTION)
        index = await ensure_index(flat, dense, sparse, store, arguments.work)
        transport = CachingTransport(httpx.AsyncHTTPTransport(), arguments.cache_dir)
        async with httpx.AsyncClient(transport=transport) as http:
            clients = await build_model_clients(http, settings, key.get_secret_value())
            deps = ask_deps(
                catalog_of(chunks),
                build_identifier_index(flat),
                HybridRetriever(dense, sparse, store),
                clients,
            )
            rows = await ask_all(questions, deps, transport, arguments.output)
    finally:
        await client.close()
    return {
        "ingest": manifest,
        "index": index,
        "questions": len(rows),
        "cost_usd": round(sum(row["cost_usd"] for row in rows), 6),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Bir belge klasörünü ayrı indekste ölçer.")
    parser.add_argument("--documents", type=Path, required=True)
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, default=Path("evals/output/answer-cache"))
    arguments = parser.parse_args()
    json.dump(asyncio.run(run(arguments)), sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
