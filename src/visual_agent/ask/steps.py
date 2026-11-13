"""Soru hattının adımları. Her adım yeni bir durum döndürür."""

import asyncio
import logging
import time
from collections.abc import Sequence
from dataclasses import dataclass, replace

from visual_agent.ask.agreement import agreed_answer, candidate_documents
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.language import detect_language
from visual_agent.ask.streaming import INCOMPLETE_MESSAGE, StreamAssembler
from visual_agent.domain.answer import (
    AnswerKind,
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
from visual_agent.generation.openrouter import AttemptRecord, ServiceUnavailable, StreamCallbacks
from visual_agent.generation.parse import ParseFailure, parse_answer
from visual_agent.generation.sources import build_user_message, to_prompt_sources
from visual_agent.verification.answer import (
    Sources,
    code_source_number,
    safe_clarify_question,
    verify_answer,
)
from visual_agent.verification.text import identifiers_in

logger = logging.getLogger(__name__)

_MAX_EXACT_CHUNKS_PER_IDENTIFIER = 2
_MIN_CLARIFY_DOCUMENTS = 2
_MAX_CLARIFY_DOCUMENTS = 4
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
    first_verified_seconds: float | None = None
    result: AskResult | None = None
    resolved_question: str | None = None
    inherited_doc_ids: tuple[str, ...] = ()
    scope_inherited: bool = False
    context_resolved: bool = True
    translate_seconds: float | None = None
    provider_attempts: int = 0
    provider_seconds: float = 0.0

    @property
    def question(self) -> str:
        return self.resolved_question or self.request.question


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
    codes = ", ".join(item.upper() for item in missing)
    choices = tuple(
        ClarifyChoice(doc_id=doc_id, label=deps.catalog.title(doc_id))
        for doc_id in suggested[:_MAX_CLARIFY_DOCUMENTS]
    )
    if suggested and state.scope_inherited:
        # Kod başka belgede var; arayüz "bu belgede yok" der ve "Tüm belgelerde ara" önerir.
        return NotFound(reason="", suggestions=choices)
    # Kod kapsam dışındaki bir belgede varsa (seçilen, adı geçen ya da önceki turun belgesi)
    # "belgelerde geçmiyor" denmez; o belge düğme olarak önerilir.
    place = "seçilen belgelerde" if suggested else "belgelerde"
    return NotFound(reason=f"{codes} {place} geçmiyor.", suggestions=choices)


CONTEXT_GONE_QUESTION = (
    "Önceki belge silinmiş ya da şu an yeniden işleniyor. Hangi belgeden soruyorsunuz?"
)


def _context_documents_gone(
    state: AskState, deps: AskDeps, allowed: Sequence[str], explicit: Sequence[str]
) -> bool:
    """Takip sorusunun belgelerinin hepsi gitti ve kullanıcı yeni belge ya da kod söylemedi.

    Tamamlanan soru kodu bağlamdan taşıdığı için yalnız kullanıcının kendi mesajına bakılır.
    """
    if not state.inherited_doc_ids or explicit:
        return False
    if any(doc in allowed for doc in state.inherited_doc_ids):
        return False
    own = state.request.question
    if deps.catalog.mentioned_in(own, allowed):
        return False
    return not (identifiers_in(own) or deps.identifiers.codes_in_speech(own))


async def resolve_scope(state: AskState, deps: AskDeps) -> AskState:
    """Kapsamı belirler; kod hiçbir yerde yoksa arama ve model çalışmadan durur."""
    request = state.request
    allowed = deps.catalog.visible_doc_ids(request.access)
    mentioned = deps.catalog.mentioned_in(state.question, allowed)
    explicit = tuple(doc for doc in request.doc_ids or () if doc in allowed)
    inherited = tuple(doc for doc in state.inherited_doc_ids if doc in allowed)
    scope = explicit or mentioned or inherited or None
    if _context_documents_gone(state, deps, allowed, explicit):
        return replace(
            state,
            allowed=allowed,
            scope=state.inherited_doc_ids,
            result=Clarify(question=CONTEXT_GONE_QUESTION),
        )
    current = replace(
        state,
        language=detect_language(state.question),
        allowed=allowed,
        scope=scope,
        scope_inherited=bool(inherited) and not explicit and not mentioned,
    )
    identifiers = sorted(
        identifiers_in(state.question) | deps.identifiers.codes_in_speech(state.question)
    )
    domain = _search_domain(current)
    missing = [item for item in identifiers if not deps.identifiers.lookup(item, domain)]
    if missing and len(missing) == len(identifiers):
        return replace(current, result=_code_not_found(missing, current, deps))
    return replace(current, exact_chunks=_exact_chunks(identifiers, current, deps))


async def _bm25_query(state: AskState, deps: AskDeps) -> tuple[str, float | None]:
    """Çeviri yalnız soru dili ile belge dilleri farklıysa yapılır; süresi ayrıca döner."""
    question = state.question
    targets = deps.catalog.languages(_search_domain(state))
    if deps.translator is None or all(target == state.language for target in targets):
        return question, None
    started = time.perf_counter()
    try:
        translated = await asyncio.wait_for(
            deps.translator(question, state.language, targets), deps.translation_limit_seconds
        )
    except Exception:
        logger.warning("Sorgu çevirisi kullanılamadı; özgün soruyla aranıyor", exc_info=True)
        translated = question
    return translated, time.perf_counter() - started


def _with_exact_chunks(state: AskState, found: Sequence[Hit], top_k: int) -> tuple[Hit, ...]:
    exact = [Hit(chunk=chunk, score=1.0) for chunk in state.exact_chunks]
    known = {hit.chunk.chunk_id for hit in exact}
    return tuple([*exact, *(hit for hit in found if hit.chunk.chunk_id not in known)][:top_k])


async def retrieve(state: AskState, deps: AskDeps) -> AskState:
    """Arama daima kapsamla sınırlıdır: katalogda yalnız hazır belgeler vardır."""
    domain = _search_domain(state)
    if not domain:
        return replace(state, result=NotFound())
    bm25_query, translate_seconds = await _bm25_query(state, deps)
    state = replace(state, translate_seconds=translate_seconds)
    found = await deps.retriever.search(
        state.question, bm25_query, domain, deps.top_k, state.request.access
    )
    hits = _with_exact_chunks(state, found, deps.top_k)
    if not hits:
        return replace(state, result=NotFound())
    if state.request.on_event is not None:
        sources = [_citation(hit).model_dump(mode="json") for hit in hits]
        state.request.on_event({"type": "sources", "sources": sources})
    return replace(state, hits=hits)


def _stream_callbacks(
    state: AskState, sources: Sources
) -> tuple[StreamAssembler | None, StreamCallbacks | None]:
    if state.request.on_event is None:
        return None, None
    assembler = StreamAssembler(sources, state.language, state.request.on_event)
    return assembler, StreamCallbacks(
        on_delta=assembler.feed, may_retry=assembler.may_retry, on_reset=assembler.reset
    )


def _partial_result(assembler: StreamAssembler, hits: Sequence[Hit], sources: Sources) -> Answered:
    return Answered(
        status=VerificationStatus.PARTIAL,
        items=tuple(
            _answered_item(item, check, hits, sources) for item, check in assembler.verified
        ),
        problems=(INCOMPLETE_MESSAGE,),
    )


def _with_attempts(state: AskState, attempts: Sequence[AttemptRecord]) -> AskState:
    """Sağlayıcı yedeğine düşüldü mü ve sağlayıcılar toplam ne kadar bekletti."""
    return replace(
        state,
        provider_attempts=len(attempts),
        provider_seconds=sum(attempt.seconds for attempt in attempts),
    )


async def generate(state: AskState, deps: AskDeps) -> AskState:
    citations = tuple(_citation(hit) for hit in state.hits)
    messages = [
        {"role": "system", "content": deps.system_prompt},
        {
            "role": "user",
            "content": build_user_message(state.hits, state.question, state.language),
        },
    ]
    sources = to_prompt_sources(state.hits, deps.catalog.language)
    assembler, callbacks = _stream_callbacks(state, sources)
    try:
        stream = await deps.answer_client.stream(messages, callbacks)
    except ServiceUnavailable as error:
        logger.exception("Cevap servisine ulaşılamadı")
        return replace(
            _with_attempts(state, error.attempts),
            result=Failed(reason=_SERVICE_DOWN, citations=citations),
        )
    current = replace(
        _with_attempts(state, stream.attempts),
        cost_usd=stream.cost_usd,
        provider=stream.provider,
        first_verified_seconds=assembler.first_verified_seconds if assembler else None,
    )
    if stream.incomplete and assembler is not None:
        assembler.interrupted()
        return replace(current, result=_partial_result(assembler, state.hits, sources))
    parsed = parse_answer(stream.content, stream.finish)
    if isinstance(parsed, ParseFailure):
        logger.warning("Model çıktısı okunamadı: %s %s", parsed.reason, parsed.detail)
        return replace(current, result=Failed(reason=_MODEL_FAILED, citations=citations))
    return replace(current, answer=parsed)


def _hit_at(number: int, hits: Sequence[Hit]) -> Hit | None:
    return hits[number - 1] if 1 <= number <= len(hits) else None


def _answered_item(
    item: ModelItem, check: ItemCheck, hits: Sequence[Hit], sources: Sources
) -> AnsweredItem:
    numbers = [n for n in check.source_numbers if 1 <= n <= len(hits)]
    number = code_source_number(item, sources)
    code_hit = _hit_at(number, hits) if number is not None else None
    return AnsweredItem(
        text=item.text,
        citations=tuple(_citation(hits[number - 1]) for number in dict.fromkeys(numbers)),
        verified=check.ok,
        from_figure=check.from_figure,
        code=code_hit.chunk.text if check.ok and code_hit is not None else None,
        problems=check.problems,
        source_quote=check.quote,
    )


def _clarification(
    answer: ModelAnswer, documents: Sequence[str], state: AskState, deps: AskDeps
) -> Clarify:
    """Belge düğmeleri yalnız 2-4 aday belgede gösterilir; daha çoğu listelenmez."""
    show_choices = (
        _MIN_CLARIFY_DOCUMENTS <= len(documents) <= _MAX_CLARIFY_DOCUMENTS
        and not state.request.doc_ids
    )
    return Clarify(
        question=safe_clarify_question(
            answer.clarify.question if answer.clarify else "", state.question, state.language
        ),
        options=tuple(
            ClarifyChoice(doc_id=doc_id, label=deps.catalog.title(doc_id)) for doc_id in documents
        )
        if show_choices
        else (),
    )


async def verify(state: AskState, deps: AskDeps) -> AskState:
    assert state.answer is not None
    answer = state.answer
    sources = to_prompt_sources(state.hits, deps.catalog.language)
    verification = verify_answer(answer, sources, state.language)
    if verification.status is VerificationStatus.NOT_FOUND:
        return replace(state, result=NotFound())
    if verification.status is VerificationStatus.CLARIFY:
        documents = candidate_documents(state.hits, verification.clarify_options)
        agreed, cost = await agreed_answer(
            state.question, state.language, state.hits, documents, deps, _citation
        )
        result = agreed or _clarification(answer, documents, state, deps)
        return replace(state, result=result, cost_usd=state.cost_usd + cost)
    if answer.kind is not AnswerKind.ANSWER:
        citations = tuple(_citation(hit) for hit in state.hits)
        return replace(state, result=Failed(reason=_MODEL_FAILED, citations=citations))
    items = tuple(
        _answered_item(item, check, state.hits, sources)
        for item, check in zip(answer.items, verification.items, strict=True)
    )
    result = Answered(
        status=verification.status,
        items=items,
        has_conflict=answer.has_conflict,
        problems=verification.problems,
    )
    return replace(state, result=result)
