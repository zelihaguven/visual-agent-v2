"""Selamlaşma ve envanter soruları aramaya gitmeden cevaplanır."""

import asyncio
import logging
from dataclasses import replace

from visual_agent.ask.deps import AskDeps
from visual_agent.ask.steps import AskState
from visual_agent.domain.result import AskResult, Inventory, InventoryDocument, SmallTalk
from visual_agent.generation.intent import Intent
from visual_agent.verification.text import identifiers_in, normalize

logger = logging.getLogger(__name__)

_MAX_LISTED_CODES = 200
SMALL_TALK_REPLIES: dict[str, dict[Intent, str]] = {
    "tr": {
        "greeting": "Merhaba, nasıl yardımcı olabilirim?",
        "how_are_you": "İyiyim, teşekkürler. Nasıl yardımcı olabilirim?",
        "thanks": "Rica ederim. Başka bir sorunuz var mı?",
        "goodbye": "Görüşmek üzere, iyi çalışmalar.",
    },
    "en": {
        "greeting": "Hello, how can I help?",
        "how_are_you": "I am well, thank you. How can I help?",
        "thanks": "You are welcome. Anything else?",
        "goodbye": "Goodbye, have a good day.",
    },
}

_COMMON_SMALL_TALK: dict[str, Intent] = {
    **dict.fromkeys(
        ("merhaba", "merhabalar", "selam", "selamlar", "günaydın", "iyi günler", "iyi akşamlar"),
        "greeting",
    ),
    **dict.fromkeys(("hello", "hi", "hey", "good morning"), "greeting"),
    **dict.fromkeys(
        ("nasılsın", "nasılsınız", "merhaba, nasılsın", "merhaba nasılsın", "selam nasılsın"),
        "how_are_you",
    ),
    **dict.fromkeys(("naber", "how are you"), "how_are_you"),
    **dict.fromkeys(
        ("teşekkürler", "teşekkür ederim", "sağ ol", "sağol", "sağ olun", "eyvallah"), "thanks"
    ),
    **dict.fromkeys(("thanks", "thank you"), "thanks"),
    **dict.fromkeys(
        ("görüşürüz", "hoşça kal", "hoşça kalın", "iyi çalışmalar", "bye", "goodbye"), "goodbye"
    ),
}


def _common_small_talk(question: str) -> Intent | None:
    """Sık selamlar modele sorulmaz: anında ve her seferinde aynı tanınır."""
    return _COMMON_SMALL_TALK.get(normalize(question).strip(" .,!?…"))


def _build_inventory(state: AskState, deps: AskDeps) -> Inventory:
    documents = []
    for doc_id in state.allowed:
        codes = deps.identifiers.codes_of(doc_id)
        documents.append(
            InventoryDocument(
                doc_id=doc_id,
                title=deps.catalog.title(doc_id),
                codes=codes[:_MAX_LISTED_CODES],
                code_count=len(codes),
            )
        )
    return Inventory(
        documents=tuple(documents),
        document_count=len(documents),
        code_count=sum(document.code_count for document in documents),
    )


def _result_for(intent: Intent, state: AskState, deps: AskDeps) -> AskResult | None:
    if intent == "inventory":
        return _build_inventory(state, deps)
    replies = SMALL_TALK_REPLIES.get(state.language, SMALL_TALK_REPLIES["tr"])
    return SmallTalk(text=replies[intent]) if intent in replies else None


async def _classified(state: AskState, deps: AskDeps) -> Intent:
    if state.request.doc_ids:
        return "question"
    common = _common_small_talk(state.question)
    if common is not None:
        return common
    classifier = deps.intent_classifier
    if classifier is None or identifiers_in(state.question):
        return "question"
    try:
        return await asyncio.wait_for(classifier(state.question), deps.intent_limit_seconds)
    except Exception:
        logger.warning("Mesajın türü anlaşılamadı", exc_info=True)
        return "question"


async def resolve_intent(state: AskState, deps: AskDeps) -> AskState:
    """İçinde kod geçen mesajlar belge sorusudur; denetim gecikme eklemez."""
    result = _result_for(await _classified(state, deps), state, deps)
    if result is not None:
        return replace(state, result=result)
    if state.request.on_event is not None:
        state.request.on_event({"type": "searching"})
    return state
