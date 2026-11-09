"""Sohbet bağlamı: soruyu tamamlar, sonraki tura ne taşınacağını belirler."""

import asyncio
import logging
from dataclasses import replace

from visual_agent.ask.deps import AskDeps
from visual_agent.ask.steps import AskState
from visual_agent.conversation.grounding import is_grounded
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.result import Answered, Clarify
from visual_agent.verification.text import identifiers_in

logger = logging.getLogger(__name__)

_CANNOT_COMPLETE = (
    "Soruyu önceki konuşmayla birleştiremedim. Model ya da konuyu da yazarak yeniden sorar mısınız?"
)


def _unresolved(state: AskState) -> AskState:
    return replace(state, context_resolved=False, result=Clarify(question=_CANNOT_COMPLETE))


async def resolve_context(state: AskState, deps: AskDeps) -> AskState:
    """Tamamlanamayan takip sorusu tahminle aranmaz; kullanıcıya geri sorulur."""
    request = state.request
    context = request.context
    if context is None or deps.rewriter is None:
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
    has_new_identifier = bool(identifiers_in(request.question) - identifiers_in(context.question))
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


def next_context(state: AskState) -> ConversationContext | None:
    """Yalnız doğrulanmış cevap bağlamı değiştirir; netleştirme soruyu bekletir."""
    result = state.result
    previous = state.request.context
    if isinstance(result, Answered):
        verified = result.status.value == "verified"
        return (_from_verified(state, result) if verified else None) or previous
    if isinstance(result, Clarify) and state.context_resolved:
        return ConversationContext(question=state.question, doc_ids=state.scope or ())
    return previous
