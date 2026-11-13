"""Sohbet bağlamı: soruyu tamamlar, sonraki tura ne taşınacağını belirler."""

import asyncio
import logging
from dataclasses import replace

from visual_agent.ask.deps import AskDeps
from visual_agent.ask.intent import common_small_talk
from visual_agent.ask.steps import AskState
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.conversation.grounding import is_grounded
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.result import Answered, Clarify
from visual_agent.verification.text import compact_identifier, identifiers_in

logger = logging.getLogger(__name__)

_CONTEXT_STATUSES = (VerificationStatus.VERIFIED, VerificationStatus.PARTIAL)
_CANNOT_COMPLETE = (
    "Soruyu önceki konuşmayla birleştiremedim. Model ya da konuyu da yazarak yeniden sorar mısınız?"
)


def _unresolved(state: AskState) -> AskState:
    return replace(state, context_resolved=False, result=Clarify(question=_CANNOT_COMPLETE))


def _codes_in(text: str, deps: AskDeps) -> set[str]:
    """Kodlar yazılışından bağımsız karşılaştırılır; söylenen kodlar da sayılır."""
    codes = identifiers_in(text) | deps.identifiers.codes_in_speech(text)
    return {compact_identifier(code) for code in codes}


async def resolve_context(state: AskState, deps: AskDeps) -> AskState:
    """Tamamlanamayan takip sorusu tahminle aranmaz; kullanıcıya geri sorulur."""
    request = state.request
    context = request.context
    if context is None or deps.rewriter is None or common_small_talk(request.question):
        return state
    try:
        rewrite = await asyncio.wait_for(
            deps.rewriter(context.question, request.question), deps.rewrite_limit_seconds
        )
    except Exception:
        logger.warning("Takip sorusu tamamlanamadı", exc_info=True)
        return _unresolved(state)
    if not rewrite.follows:
        return state
    if not is_grounded(rewrite.question, (request.question, context.question)):
        logger.warning("Tamamlanan soruda kullanıcının söylemediği değer var")
        return _unresolved(state)
    if request.on_event is not None:
        request.on_event({"type": "resolved", "question": rewrite.question})
    has_new_identifier = bool(_codes_in(request.question, deps) - _codes_in(context.question, deps))
    return replace(
        state,
        resolved_question=rewrite.question,
        inherited_doc_ids=() if has_new_identifier else context.doc_ids,
    )


def _from_verified(state: AskState, result: Answered) -> ConversationContext | None:
    citations = [c for item in result.items if item.verified for c in item.citations]
    documents = {citation.doc_id: citation.title for citation in citations}
    if not documents:
        return None
    return ConversationContext(
        question=state.question, doc_ids=tuple(documents), titles=tuple(documents.values())
    )


def _scope_context(state: AskState, catalog: DocumentCatalog) -> ConversationContext:
    """Bağlama o turun sorusu ve kapsamı girer; her belgenin adıyla.

    Ad katalogdan, katalogda yoksa (silinmiş belge) aramadan ya da önceki bağlamdan gelir.
    Tur yeni bir kodla bütün belgelerde arandıysa kapsam boştur; önceki konunun belgeleri
    taşınmaz.
    """
    previous = state.request.context
    # İstemcinin gönderdiği bağlamda ad olmayabilir; eksik ad boş sayılır.
    known = dict(zip(previous.doc_ids, previous.titles, strict=False)) if previous else {}
    known |= {hit.chunk.doc_id: hit.chunk.title for hit in state.hits}
    scope = state.scope or ()
    titles = tuple(catalog.find_title(doc) or known.get(doc, "") for doc in scope)
    return ConversationContext(question=state.question, doc_ids=scope, titles=titles)


def next_context(state: AskState, catalog: DocumentCatalog) -> ConversationContext | None:
    """Cevaplanan turda kullanıcının sorusu bağlama girer; netleştirme soruyu bekletir.

    Belgeler yalnız doğrulanmış cümlelerin kaynaklarından gelir. Cevap gizlendiyse soru yine
    bağlama girer, belgeler o turda aranan belgelerdir: sonraki takip sorusu kullanıcının son
    sorusuyla ve o sorunun kapsamıyla tamamlanır.
    """
    result = state.result
    if isinstance(result, Answered):
        usable = result.status in _CONTEXT_STATUSES
        verified = _from_verified(state, result) if usable else None
        return verified or _scope_context(state, catalog)
    if isinstance(result, Clarify) and state.context_resolved:
        return _scope_context(state, catalog)
    return state.request.context
