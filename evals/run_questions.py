"""Üretilen seti uçtan uca çalıştırır ve puanlar (yerelde gömülü Qdrant ile ya da sunucuda)."""

import argparse
import asyncio
import json
import sys
from collections.abc import Sequence
from pathlib import Path

import httpx
from qdrant_client import AsyncQdrantClient

from evals.answer_cache import CacheCounts, CachingTransport
from evals.gold import Badge, GoldQuestion, GoldSet, GoldSource, Outcome
from evals.index_cache import Documents, ensure_index, load_or_ingest
from evals.scoring import AnswerItem, AnswerRecord, question_found, score_question, summarize
from visual_agent.ask.clients import ask_deps, build_model_clients
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.language import detect_language, document_language
from visual_agent.ask.orchestrator import answer_question
from visual_agent.ask.steps import AskState, resolve_scope, retrieve
from visual_agent.catalog.identifiers import build_identifier_index
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.document import Chunk, DocumentMeta
from visual_agent.domain.result import Answered, AskResult, Citation, Clarify, NotFound
from visual_agent.generation.openrouter import StreamCallbacks, StreamResult
from visual_agent.retrieval.encoders import BgeM3Dense, Bm25Sparse
from visual_agent.retrieval.hybrid import HybridRetriever
from visual_agent.retrieval.qdrant_store import QdrantChunkStore, open_client
from visual_agent.settings import Settings

_COLLECTION = "evaluation"
_LANGUAGE_SAMPLE_CHARS = 2000
_FIRST_TURN = 1


def _meta(gold: GoldSet, doc_id: str) -> DocumentMeta:
    """Belge işleme (OCR dili dahil) altın verideki metinden okunan dille yapılır."""
    text = gold.document_texts[doc_id]
    return DocumentMeta(
        doc_id=doc_id,
        title=text.splitlines()[0],
        language=detect_language(text[:_LANGUAGE_SAMPLE_CHARS]),
    )


def gold_documents(gold: GoldSet, set_directory: Path) -> Documents:
    return [
        (set_directory / document.filename, _meta(gold, document.doc_id))
        for document in gold.documents
    ]


def load_chunks(gold: GoldSet, set_directory: Path, work: Path) -> dict[str, list[Chunk]]:
    chunks, manifest = load_or_ingest(gold_documents(gold, set_directory), work, keep_partial=False)
    if manifest.get("errors"):
        raise SystemExit(f"belge işlenemedi: {manifest['errors']}")
    return chunks


def gold_catalog(gold: GoldSet, chunks: dict[str, list[Chunk]]) -> DocumentCatalog:
    """Katalog dili, uygulamadaki gibi belgenin parçalarından okunur."""
    catalog = DocumentCatalog()
    for document in gold.documents:
        meta = _meta(gold, document.doc_id)
        language = document_language(chunks[document.doc_id], meta.language)
        catalog.add(meta.model_copy(update={"language": language}))
    return catalog


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


def cache_label(delta: CacheCounts, offline: bool = False) -> str:
    """Önbellekten gelen istek varsa sorunun süresi ve maliyeti gerçek değildir.

    Çevrimdışı koşuda ıska ağa gitmez: soru "miss" olur, canlı sayılmaz; sonucu güvenilmezdir.
    """
    if offline and delta.misses:
        return "miss"
    if delta.hits and delta.misses:
        return "partial"
    return "cached" if delta.hits else "live"


def select_questions(gold: GoldSet, wanted: Sequence[str] | None) -> list[GoldQuestion]:
    """Seçilen sorular ve takip sorularının sohbetteki önceki turları, altın veri sırasıyla."""
    if not wanted:
        return list(gold.questions)
    unknown = sorted(set(wanted) - {q.question_id for q in gold.questions})
    if unknown:
        raise ValueError(f"sette olmayan sorular: {', '.join(unknown)}")
    picked = [q for q in gold.questions if q.question_id in wanted]
    last_turn: dict[str, int] = {}
    for question in picked:
        if question.conversation_id is not None:
            conversation = question.conversation_id
            last_turn[conversation] = max(last_turn.get(conversation, 0), question.turn or 0)
    return [
        q
        for q in gold.questions
        if q in picked
        or (q.conversation_id in last_turn and (q.turn or 0) <= last_turn[q.conversation_id])
    ]


async def _full_run(
    questions: Sequence[GoldQuestion],
    gold: GoldSet,
    deps: AskDeps,
    output: Path,
    counts: CacheCounts,
    offline: bool = False,
) -> dict[str, object]:
    records: list[AnswerRecord] = []
    rows: list[dict[str, object]] = []
    contexts: dict[str, ConversationContext | None] = {}
    cost = 0.0
    labels: dict[str, int] = {"live": 0, "cached": 0, "partial": 0}
    # Iskalanan soru güvenilmez: puana girmez. Sohbette ondan sonraki turlar da onun
    # bağlamıyla sorulduğu için onlar da ıska sayılır.
    missed: list[str] = []
    missed_conversations: set[str] = set()
    for question in questions:
        conversation = question.conversation_id
        context = contexts.get(conversation) if conversation is not None else None
        before = counts.snapshot()
        outcome = await answer_question(AskRequest(question.text, context=context), deps)
        label = cache_label(counts.since(before), offline)
        if offline and conversation in missed_conversations:
            label = "miss"
        if label == "miss":
            missed.append(question.question_id)
            if conversation is not None:
                missed_conversations.add(conversation)
        else:
            labels[label] += 1
        live = label == "live"
        if conversation is not None:
            contexts[conversation] = outcome.context
        record = to_record(question.question_id, outcome.result)
        records.append(record)
        cost += outcome.cost_usd if live else 0.0
        rows.append(
            {
                "question": question.question_id,
                "kind": question.kind.value,
                "resolved_question": outcome.question,
                "record": record.model_dump(mode="json"),
                "score": score_question(question, record, gold.document_texts).model_dump(
                    mode="json"
                ),
                "cache": label,
                "timings": outcome.timings if live else None,
                "cost_usd": outcome.cost_usd if live else None,
                "provider": outcome.provider,
            }
        )
    scored = [
        (q, r) for q, r in zip(questions, records, strict=True) if q.question_id not in missed
    ]
    scores = [score_question(q, r, gold.document_texts) for q, r in scored]
    summary = summarize([q for q, _ in scored], scores).model_dump(mode="json")
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    return {
        **summary,
        "cost_usd_live_questions": round(cost, 5),
        "questions_live": labels["live"],
        "questions_from_cache": labels["cached"],
        "questions_partly_from_cache": labels["partial"],
        "questions_missed_offline": missed,
    }


async def run(arguments: argparse.Namespace) -> dict[str, object]:
    settings = Settings()
    gold = GoldSet.model_validate_json((arguments.set / "gold.json").read_text(encoding="utf-8"))
    chunks = load_chunks(gold, arguments.set, arguments.work)
    flat = [chunk for items in chunks.values() for chunk in items]
    catalog = gold_catalog(gold, chunks)
    dense, sparse = BgeM3Dense(), Bm25Sparse()
    client = _qdrant(arguments)
    try:
        return await _measure(arguments, settings, gold, catalog, flat, dense, sparse, client)
    finally:
        await client.close()


def _qdrant(arguments: argparse.Namespace) -> AsyncQdrantClient:
    """Varsayılan: --work altında ölçüme özel gömülü klasör; uygulamanın klasörüne dokunmaz."""
    folder = None if arguments.qdrant_url else str(arguments.work / "qdrant")
    return open_client(arguments.qdrant_url or "", folder)


async def _measure(
    arguments: argparse.Namespace,
    settings: Settings,
    gold: GoldSet,
    catalog: DocumentCatalog,
    flat: list[Chunk],
    dense: BgeM3Dense,
    sparse: Bm25Sparse,
    client: AsyncQdrantClient,
) -> dict[str, object]:
    store = QdrantChunkStore(client, _COLLECTION)
    await ensure_index(flat, dense, sparse, store, arguments.work)
    retriever = HybridRetriever(dense, sparse, store)
    identifiers = build_identifier_index(flat)
    key = settings.openrouter_api_key
    if arguments.retrieval_only or key is None or not key.get_secret_value():
        no_model = AskDeps(catalog, identifiers, retriever, _NoModel(), "")
        report = await _retrieval_only(gold, no_model)
        if not arguments.retrieval_only:
            report["note"] = "OpenRouter anahtarı yok; yalnız arama ölçüldü."
        return report

    api_key = key.get_secret_value()
    counts = CacheCounts()
    transport: httpx.AsyncBaseTransport = httpx.AsyncHTTPTransport()
    if not arguments.no_cache:
        transport = CachingTransport(
            transport,
            arguments.cache_dir,
            refresh=arguments.refresh_cache,
            offline=arguments.offline,
        )
        counts = transport.counts
    async with httpx.AsyncClient(transport=transport) as http:
        clients = await build_model_clients(http, settings, api_key)
        deps = ask_deps(catalog, identifiers, retriever, clients)
        questions = select_questions(gold, arguments.questions)
        if arguments.repeat == 1:
            output = arguments.work / "answers.json"
            return await _full_run(questions, gold, deps, output, counts, arguments.offline)
        return await _repeated(arguments, questions, gold, deps, counts)


async def _repeated(
    arguments: argparse.Namespace,
    questions: Sequence[GoldQuestion],
    gold: GoldSet,
    deps: AskDeps,
    counts: CacheCounts,
) -> dict[str, object]:
    """Kararlılık ölçümü: aynı sorular art arda sorulur, her soru kaç kez geçti sayılır."""
    passed: dict[str, int] = {q.question_id: 0 for q in questions}
    for attempt in range(1, arguments.repeat + 1):
        output = arguments.work / f"answers-{attempt}.json"
        await _full_run(questions, gold, deps, output, counts)
        for row in json.loads(output.read_text(encoding="utf-8")):
            passed[row["question"]] += int(row["score"]["passed"])
    return {"repeat": arguments.repeat, "cache": NO_CACHE_NOTE, "passed": passed}


class _NoModel:
    async def stream(
        self, messages: Sequence[dict[str, str]], callbacks: StreamCallbacks | None = None
    ) -> StreamResult:
        raise RuntimeError("Yalnız arama ölçümünde model çağrılmaz")


NO_CACHE_NOTE = "önbellek kullanılmadı"
DEFAULT_CACHE_DIR = Path("evals/output/answer-cache")


def check_cache_arguments(arguments: argparse.Namespace) -> str | None:
    """Tekrarlar bağımsız model koşusu olmalı: önbellek ne okunur ne yazılır.

    Tekrarla birlikte önbelleği açmaya çalışan seçenek hata mesajı döndürür; geçerliyse
    önbellek kapatılır ve None döner.
    """
    if arguments.repeat < 1:
        return "--repeat en az 1 olmalı"
    if arguments.offline and (
        arguments.repeat != 1 or arguments.refresh_cache or arguments.no_cache
    ):
        return "--offline yalnız önbellekten okur; --repeat, --refresh-cache, --no-cache olmaz"
    if arguments.repeat == 1:
        if arguments.cache_dir is None:
            arguments.cache_dir = DEFAULT_CACHE_DIR
        return None
    if arguments.refresh_cache or arguments.cache_dir is not None:
        return (
            "--repeat önbelleksiz çalışır; --refresh-cache ve --cache-dir ile birlikte kullanılamaz"
        )
    arguments.no_cache = True
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Soru hattını üretilen setle ölçer.")
    parser.add_argument("--set", type=Path, default=Path("evals/output/set"))
    parser.add_argument("--work", type=Path, default=Path("evals/output/run"))
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--qdrant-url", help="gömülü klasör yerine Qdrant sunucusu")
    parser.add_argument(
        "--cache-dir", type=Path, help=f"cevap önbelleği (varsayılan {DEFAULT_CACHE_DIR})"
    )
    parser.add_argument(
        "--refresh-cache", action="store_true", help="önbellekteki cevapları yeniden sor"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="önbelleği hiç kullanma ve değiştirme"
    )
    parser.add_argument(
        "--questions",
        type=lambda text: [item.strip() for item in text.split(",") if item.strip()],
        help="yalnız bu sorular (virgülle); takip sorularının önceki turları da sorulur",
    )
    parser.add_argument(
        "--repeat", type=int, default=1, help="aynı soruları kaç kez sor (önbelleksiz)"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help='model isteği ağa gitmez; önbellekte olmayan soru "miss" olarak listelenir',
    )
    arguments = parser.parse_args()
    problem = check_cache_arguments(arguments)
    if problem is not None:
        parser.error(problem)
    arguments.work.mkdir(parents=True, exist_ok=True)
    json.dump(asyncio.run(run(arguments)), sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
