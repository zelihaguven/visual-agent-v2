"""Soru hattının adımları. Her adım yeni bir durum döndürür."""

import asyncio
import logging
from collections.abc import Sequence
from dataclasses import dataclass, replace

from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.language import detect_language
from visual_agent.domain.answer import (
    AnswerKind,
    AnswerVerification,
    ItemCheck,
    ModelAnswer,
    ModelItem,
    VerificationStatus,
)
from visual_agent.domain.document import Chunk, ChunkKind
from visual_agent.domain.result import (
    Answered,
    AnsweredItem,
    AskResult,
    Citation,
    Clarify,
    ClarifyChoice,
    Failed,
    Hit,
    NotFound,
)
from visual_agent.generation.openrouter import ServiceUnavailable
from visual_agent.generation.parse import ParseFailure, parse_answer
from visual_agent.generation.sources import build_user_message, to_prompt_sources
from visual_agent.verification.answer import verify_answer
from visual_agent.verification.text import identifiers_in

logger = logging.getLogger(__name__)

_MAX_EXACT_CHUNKS_PER_IDENTIFIER = 2
_MIN_CLARIFY_DOCUMENTS = 2
_SERVICE_DOWN = "Cevap servisi şu an kullanılamıyor. Bulunan kaynak sayfaları aşağıda."
_MODEL_FAILED = "Model güvenilir bir cevap üretemedi. Değeri kaynaktan kontrol edin."


@dataclass(frozen=True)
class AskState:
    request: AskRequest
    language: str = "tr"
    allowed: tuple[str, ...] = ()
    scope: tuple[str, ...] | None = None
    exact_chunks: tuple[Chunk, ...] = ()
    hits: tuple[Hit, ...] = ()
    answer: ModelAnswer | None = None
    cost_usd: float = 0.0
    provider: str | None = None
    result: AskResult | None = None


def _citation(hit: Hit) -> Citation:
    chunk = hit.chunk
    return Citation(
        chunk_id=chunk.chunk_id, doc_id=chunk.doc_id, title=chunk.title, location=chunk.location
    )


def _search_domain(state: AskState) -> tuple[str, ...]:
    return state.scope if state.scope is not None else state.allowed


def _exact_chunks(identifiers: Sequence[str], state: AskState, deps: AskDeps) -> tuple[Chunk, ...]:
    """Belge adı olan kodlar yalnız kapsamı belirler, kaynak listesini doldurmaz."""
    chunks: dict[str, Chunk] = {}
    for identifier in identifiers:
        if deps.catalog.is_document_name(identifier):
            continue
        found = deps.identifiers.chunks_for(identifier, _search_domain(state))
        ordered = sorted(found, key=lambda chunk: chunk.kind is not ChunkKind.TABLE_ROW)
        for chunk in ordered[:_MAX_EXACT_CHUNKS_PER_IDENTIFIER]:
            chunks.setdefault(chunk.chunk_id, chunk)
    return tuple(chunks.values())


def _code_not_found(missing: Sequence[str], state: AskState, deps: AskDeps) -> NotFound:
    suggested = tuple(
        dict.fromkeys(
            doc_id
            for identifier in missing
            for doc_id in deps.identifiers.documents_with(identifier)
            if doc_id in state.allowed
        )
    )
    return NotFound(
        reason=f"{', '.join(item.upper() for item in missing)} seçilen belgelerde geçmiyor.",
        suggested_doc_ids=suggested,
    )


async def resolve_scope(state: AskState, deps: AskDeps) -> AskState:
    """Kapsamı belirler; kod hiçbir yerde yoksa arama ve model çalışmadan durur."""
    request = state.request
    allowed = deps.catalog.visible_doc_ids(request.access)
    mentioned = deps.catalog.mentioned_in(request.question, allowed)
    explicit = tuple(doc for doc in request.doc_ids or () if doc in allowed)
    scope = explicit or mentioned or None
    current = replace(
        state, language=detect_language(request.question), allowed=allowed, scope=scope
    )
    identifiers = sorted(identifiers_in(request.question))
    domain = _search_domain(current)
    missing = [item for item in identifiers if not deps.identifiers.lookup(item, domain)]
    if missing and len(missing) == len(identifiers):
        return replace(current, result=_code_not_found(missing, current, deps))
    return replace(current, exact_chunks=_exact_chunks(identifiers, current, deps))


async def _bm25_query(state: AskState, deps: AskDeps) -> str:
    """Çeviri yalnız soru dili ile belge dilleri farklıysa yapılır."""
    question = state.request.question
    targets = deps.catalog.languages(_search_domain(state))
    if deps.translator is None or all(target == state.language for target in targets):
        return question
    try:
        return await asyncio.wait_for(
            deps.translator(question, state.language, targets), deps.translation_limit_seconds
        )
    except Exception:
        logger.warning("Sorgu çevirisi kullanılamadı; özgün soruyla aranıyor", exc_info=True)
        return question


def _with_exact_chunks(state: AskState, found: Sequence[Hit], top_k: int) -> tuple[Hit, ...]:
    exact = [Hit(chunk=chunk, score=1.0) for chunk in state.exact_chunks]
    known = {hit.chunk.chunk_id for hit in exact}
    return tuple([*exact, *(hit for hit in found if hit.chunk.chunk_id not in known)][:top_k])


async def retrieve(state: AskState, deps: AskDeps) -> AskState:
    query = state.request.question
    found = await deps.retriever.search(
        query, await _bm25_query(state, deps), state.scope, deps.top_k, state.request.access
    )
    hits = _with_exact_chunks(state, found, deps.top_k)
    if not hits:
        return replace(state, result=NotFound())
    return replace(state, hits=hits)


async def generate(state: AskState, deps: AskDeps) -> AskState:
    citations = tuple(_citation(hit) for hit in state.hits)
    messages = [
        {"role": "system", "content": deps.system_prompt},
        {
            "role": "user",
            "content": build_user_message(state.hits, state.request.question, state.language),
        },
    ]
    try:
        stream = await deps.answer_client.stream(messages)
    except ServiceUnavailable:
        logger.exception("Cevap servisine ulaşılamadı")
        return replace(state, result=Failed(reason=_SERVICE_DOWN, citations=citations))
    current = replace(state, cost_usd=stream.cost_usd, provider=stream.provider)
    parsed = parse_answer(stream.content, stream.finish)
    if isinstance(parsed, ParseFailure):
        logger.warning("Model çıktısı okunamadı: %s %s", parsed.reason, parsed.detail)
        return replace(current, result=Failed(reason=_MODEL_FAILED, citations=citations))
    return replace(current, answer=parsed)


def _answered_item(item: ModelItem, check: ItemCheck, hits: Sequence[Hit]) -> AnsweredItem:
    numbers = [n for n in check.source_numbers if 1 <= n <= len(hits)]
    code_hit = (
        hits[item.code_source_no - 1]
        if item.code_source_no is not None and 1 <= item.code_source_no <= len(hits)
        else None
    )
    return AnsweredItem(
        text=item.text,
        citations=tuple(_citation(hits[number - 1]) for number in dict.fromkeys(numbers)),
        verified=check.ok,
        from_figure=check.from_figure,
        code=code_hit.chunk.text if check.ok and code_hit is not None else None,
        problems=check.problems,
    )


def _clarification(
    answer: ModelAnswer, verification: AnswerVerification, state: AskState, deps: AskDeps
) -> Clarify:
    documents = list(
        dict.fromkeys(state.hits[n - 1].chunk.doc_id for n in verification.clarify_options)
    )
    show_choices = len(documents) >= _MIN_CLARIFY_DOCUMENTS and not state.request.doc_ids
    return Clarify(
        question=answer.clarify.question if answer.clarify else "",
        options=tuple(
            ClarifyChoice(doc_id=doc_id, label=deps.catalog.title(doc_id)) for doc_id in documents
        )
        if show_choices
        else (),
    )


async def verify(state: AskState, deps: AskDeps) -> AskState:
    assert state.answer is not None
    answer = state.answer
    verification = verify_answer(answer, to_prompt_sources(state.hits))
    if verification.status is VerificationStatus.NOT_FOUND:
        return replace(state, result=NotFound())
    if verification.status is VerificationStatus.CLARIFY:
        return replace(state, result=_clarification(answer, verification, state, deps))
    if answer.kind is not AnswerKind.ANSWER:
        citations = tuple(_citation(hit) for hit in state.hits)
        return replace(state, result=Failed(reason=_MODEL_FAILED, citations=citations))
    items = tuple(
        _answered_item(item, check, state.hits)
        for item, check in zip(answer.items, verification.items, strict=True)
    )
    result = Answered(
        status=verification.status,
        items=items,
        has_conflict=answer.has_conflict,
        problems=verification.problems,
    )
    return replace(state, result=result)
