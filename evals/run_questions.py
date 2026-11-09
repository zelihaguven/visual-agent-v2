"""Üretilen seti uçtan uca çalıştırır ve puanlar (işçi imajında, Qdrant ile)."""

import argparse
import asyncio
import json
import sys
import tempfile
from collections.abc import Iterable, Sequence
from pathlib import Path

import httpx
from qdrant_client import AsyncQdrantClient

from evals.gold import Badge, GoldQuestion, GoldSet, GoldSource, Outcome
from evals.ingest_check import question_found
from evals.scoring import AnswerItem, AnswerRecord, score_question, summarize
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.language import detect_language
from visual_agent.ask.orchestrator import answer_question
from visual_agent.ask.steps import AskState, resolve_scope, retrieve
from visual_agent.catalog.identifiers import build_identifier_index
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.document import Chunk, DocumentMeta
from visual_agent.domain.result import Answered, AskResult, Citation, Clarify, NotFound
from visual_agent.generation.json_model import JsonModel
from visual_agent.generation.openrouter import (
    AnswerClient,
    AnswerClientOptions,
    StreamCallbacks,
    StreamResult,
    fetch_zdr_index,
    select_providers,
)
from visual_agent.generation.prompts import load_answer_prompt, load_answer_schema
from visual_agent.generation.rewrite import Rewriter, make_rewriter
from visual_agent.generation.translate import Translator, make_translator
from visual_agent.retrieval.encoders import BgeM3Dense, Bm25Sparse
from visual_agent.retrieval.hybrid import HybridRetriever
from visual_agent.retrieval.qdrant_store import QdrantChunkStore
from visual_agent.settings import Settings

_COLLECTION = "evaluation"
_LANGUAGE_SAMPLE_CHARS = 2000
_FIRST_TURN = 1


def _meta(gold: GoldSet, doc_id: str) -> DocumentMeta:
    text = gold.document_texts[doc_id]
    return DocumentMeta(
        doc_id=doc_id,
        title=text.splitlines()[0],
        language=detect_language(text[:_LANGUAGE_SAMPLE_CHARS]),
    )


def _load_chunks(gold: GoldSet, set_directory: Path, cache: Path) -> dict[str, list[Chunk]]:
    if cache.exists():
        raw = json.loads(cache.read_text(encoding="utf-8"))
        return {doc: [Chunk.model_validate(item) for item in items] for doc, items in raw.items()}
    from visual_agent.ingest.pipeline import ingest_document
    from visual_agent.ingest.tools import default_tools

    tools = default_tools()
    chunks: dict[str, list[Chunk]] = {}
    for document in gold.documents:
        with tempfile.TemporaryDirectory() as work:
            result = ingest_document(
                set_directory / document.filename,
                _meta(gold, document.doc_id),
                tools,
                Path(work),
            )
        chunks[document.doc_id] = list(result.chunks)
    payload = {doc: [c.model_dump(mode="json") for c in items] for doc, items in chunks.items()}
    cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return chunks


async def _index(
    chunks: Iterable[Chunk], dense: BgeM3Dense, sparse: Bm25Sparse, store: QdrantChunkStore
) -> None:
    await store.recreate_collection(dense.size)
    items = list(chunks)
    texts = [chunk.embed_text for chunk in items]
    await store.upsert(
        items, ("all",), dense.encode_documents(texts), sparse.encode_documents(texts)
    )


def _standalone(gold: GoldSet) -> list[GoldQuestion]:
    """Yalnız arama ölçümü: takip soruları tamamlanmadan aranamaz."""
    return [q for q in gold.questions if q.turn is None or q.turn == _FIRST_TURN]


async def _retrieval_only(gold: GoldSet, deps: AskDeps) -> dict[str, object]:
    total = top1 = top_k = 0
    missed: list[dict[str, object]] = []
    for question in _standalone(gold):
        if not question.sources:
            continue
        state = await resolve_scope(AskState(AskRequest(question.text)), deps)
        if state.result is None:
            state = await retrieve(state, deps)
        chunks = [hit.chunk for hit in state.hits]
        total += 1
        found = question_found(question, chunks)
        top_k += found
        top1 += question_found(question, chunks[:1])
        if not found:
            missed.append(
                {"question": question.question_id, "top": [c.text[:90] for c in chunks[:3]]}
            )
    return {"questions": total, "hit_at_1": top1, "hit_at_8": top_k, "missed": missed}


def _source(citation: Citation) -> GoldSource:
    location = citation.location
    return GoldSource(
        doc_id=citation.doc_id, page=location.page, sheet=location.sheet, row=location.row
    )


def to_record(question_id: str, result: AskResult) -> AnswerRecord:
    if isinstance(result, Clarify):
        return AnswerRecord(question_id=question_id, outcome=Outcome.CLARIFY, badge=Badge.NONE)
    if isinstance(result, NotFound):
        return AnswerRecord(question_id=question_id, outcome=Outcome.NOT_FOUND, badge=Badge.NONE)
    if not isinstance(result, Answered):
        return AnswerRecord(question_id=question_id, outcome=Outcome.FAILED, badge=Badge.NONE)
    badges = {
        VerificationStatus.VERIFIED: Badge.VERIFIED,
        VerificationStatus.PARTIAL: Badge.PARTIAL,
    }
    items = tuple(
        AnswerItem(
            text=f"{item.text} {item.code or ''}".strip(),
            sources=tuple(_source(citation) for citation in item.citations),
        )
        for item in result.items
        if item.verified
    )
    return AnswerRecord(
        question_id=question_id,
        outcome=Outcome.ANSWERED,
        badge=badges.get(result.status, Badge.FAILED),
        items=items,
    )


async def _answer_client(
    http: httpx.AsyncClient, settings: Settings, api_key: str
) -> tuple[AnswerClient, Translator, Rewriter]:
    url = str(settings.openrouter_url).rstrip("/")
    index = await fetch_zdr_index(http, url, api_key)
    providers, ignored = select_providers(settings.answer_model, settings.answer_providers, index)
    options = AnswerClientOptions(
        model=settings.answer_model,
        providers=providers,
        ignored_providers=ignored,
        schema=load_answer_schema(),
        max_tokens=settings.answer_max_tokens,
        first_token_seconds=settings.answer_first_token_seconds,
        runaway_whitespace_limit=settings.stream_runaway_limit,
    )
    translation_providers, translation_ignored = select_providers(
        settings.translation_model, settings.translation_providers, index
    )
    helper_model = JsonModel(
        http, url, api_key, settings.translation_model, translation_providers, translation_ignored
    )
    return (
        AnswerClient(http, base_url=url, api_key=api_key, options=options),
        make_translator(helper_model),
        make_rewriter(helper_model),
    )


async def _full_run(gold: GoldSet, deps: AskDeps, output: Path) -> dict[str, object]:
    questions = list(gold.questions)
    records: list[AnswerRecord] = []
    rows: list[dict[str, object]] = []
    contexts: dict[str, ConversationContext | None] = {}
    cost = 0.0
    for question in questions:
        conversation = question.conversation_id
        context = contexts.get(conversation) if conversation is not None else None
        outcome = await answer_question(AskRequest(question.text, context=context), deps)
        if conversation is not None:
            contexts[conversation] = outcome.context
        record = to_record(question.question_id, outcome.result)
        records.append(record)
        cost += outcome.cost_usd
        rows.append(
            {
                "question": question.question_id,
                "kind": question.kind.value,
                "resolved_question": outcome.question,
                "record": record.model_dump(mode="json"),
                "score": score_question(question, record).model_dump(mode="json"),
                "timings": outcome.timings,
                "cost_usd": outcome.cost_usd,
                "provider": outcome.provider,
            }
        )
    scores = [score_question(q, r) for q, r in zip(questions, records, strict=True)]
    summary = summarize(questions, scores).model_dump(mode="json")
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return {**summary, "cost_usd": round(cost, 5)}


async def run(arguments: argparse.Namespace) -> dict[str, object]:
    settings = Settings()
    gold = GoldSet.model_validate_json((arguments.set / "gold.json").read_text(encoding="utf-8"))
    chunks = _load_chunks(gold, arguments.set, arguments.work / "chunks.json")
    flat = [chunk for items in chunks.values() for chunk in items]
    catalog = DocumentCatalog()
    for document in gold.documents:
        catalog.add(_meta(gold, document.doc_id))
    dense, sparse = BgeM3Dense(), Bm25Sparse()
    client = AsyncQdrantClient(url=str(settings.qdrant_url))
    store = QdrantChunkStore(client, _COLLECTION)
    await _index(flat, dense, sparse, store)
    retriever = HybridRetriever(dense, sparse, store)
    identifiers = build_identifier_index(flat)

    if arguments.retrieval_only or settings.openrouter_api_key is None:
        no_model = AskDeps(catalog, identifiers, retriever, _NoModel(), "")
        report = await _retrieval_only(gold, no_model)
        if settings.openrouter_api_key is None:
            report["note"] = "OpenRouter anahtarı yok; yalnız arama ölçüldü."
        return report

    api_key = settings.openrouter_api_key.get_secret_value()
    async with httpx.AsyncClient() as http:
        answer_client, translator, rewriter = await _answer_client(http, settings, api_key)
        deps = AskDeps(
            catalog,
            identifiers,
            retriever,
            answer_client,
            load_answer_prompt(),
            translator,
            rewriter=rewriter,
        )
        return await _full_run(gold, deps, arguments.work / "answers.json")


class _NoModel:
    async def stream(
        self, messages: Sequence[dict[str, str]], callbacks: StreamCallbacks | None = None
    ) -> StreamResult:
        raise RuntimeError("Yalnız arama ölçümünde model çağrılmaz")


def main() -> None:
    parser = argparse.ArgumentParser(description="Soru hattını üretilen setle ölçer.")
    parser.add_argument("--set", type=Path, default=Path("evals/output/set"))
    parser.add_argument("--work", type=Path, default=Path("/tmp/run"))
    parser.add_argument("--retrieval-only", action="store_true")
    arguments = parser.parse_args()
    arguments.work.mkdir(parents=True, exist_ok=True)
    json.dump(asyncio.run(run(arguments)), sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
