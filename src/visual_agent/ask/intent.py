"""Selamlaşma ve envanter soruları aramaya gitmeden cevaplanır."""

import asyncio
import logging
import re
from collections.abc import Sequence
from dataclasses import replace

from visual_agent.ask.deps import AskDeps
from visual_agent.ask.steps import AskState
from visual_agent.catalog.memory import DocumentCatalog, squash
from visual_agent.domain.result import AskResult, Inventory, InventoryDocument, SmallTalk
from visual_agent.generation.intent import Intent
from visual_agent.verification.text import identifiers_in, normalize

logger = logging.getLogger(__name__)

_MAX_LISTED_CODES = 200
MAX_LISTED_DOCUMENTS = 4
_MIN_TOPIC_WORDS = 2
_MAX_TOPIC_WORDS = 4
_WORD_RE = re.compile(r"\w+")
SMALL_TALK_REPLIES: dict[str, dict[Intent, str]] = {
    "tr": {
        "greeting": "Merhaba, nasıl yardımcı olabilirim?",
        "how_are_you": "İyiyim, teşekkürler. Nasıl yardımcı olabilirim?",
        "thanks": "Rica ederim. Başka bir sorunuz var mı?",
        "goodbye": "Görüşmek üzere, iyi çalışmalar.",
        "about_to_ask": "Tabii, sorunuzu dinliyorum.",
    },
    "en": {
        "greeting": "Hello, how can I help?",
        "how_are_you": "I am well, thank you. How can I help?",
        "thanks": "You are welcome. Anything else?",
        "goodbye": "Goodbye, have a good day.",
        "about_to_ask": "Sure, go ahead.",
    },
}

_ANNOUNCING_RE = re.compile(
    r"(?:(?:merhaba|merhabalar|selam|selamlar|günaydın|iyi günler|iyi akşamlar"
    r"|tamam|peki|şimdi)[\s,.!]+)*"
    r"(?:(?:sana|size)\s+)?"
    r"(?:bir\s+(?:şey|soru)\s+(?:soracağım|soracaktım|sormak\s+istiyorum|sormak\s+istiyordum)"
    r"|soru\s+soracağım"
    r"|bir\s+sorum\s+(?:var|olacak|olacaktı))"
)

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
    **dict.fromkeys(("i want to ask something", "i have a question"), "about_to_ask"),
}


def common_small_talk(question: str) -> Intent | None:
    """Sık selamlar modele sorulmaz: anında ve her seferinde aynı tanınır."""
    text = normalize(question).strip(" .,!?…")
    return "about_to_ask" if _ANNOUNCING_RE.fullmatch(text) else _COMMON_SMALL_TALK.get(text)


def _topic_phrases(question: str) -> set[str]:
    """Sorudaki 2-4 kelimelik ardışık öbekler; tek kelime belge adı gibi aranmaz."""
    words = _WORD_RE.findall(normalize(question))
    return {
        squash(" ".join(words[start : start + size]))
        for size in range(_MIN_TOPIC_WORDS, _MAX_TOPIC_WORDS + 1)
        for start in range(len(words) - size + 1)
    }


def topic_documents(
    question: str, allowed: Sequence[str], catalog: DocumentCatalog
) -> tuple[str, ...]:
    """Başlığında sorudaki bir öbek geçen belgeler; hiçbirinde geçmiyorsa hepsi."""
    phrases = _topic_phrases(question)
    matched = tuple(
        doc_id
        for doc_id in allowed
        if any(phrase in squash(catalog.title(doc_id)) for phrase in phrases)
    )
    return matched or tuple(allowed)


def _build_inventory(state: AskState, deps: AskDeps) -> Inventory:
    """Sayılar kayıtlardan gelir; dörtten çok belge varsa belgeler listelenmez."""
    documents = []
    for doc_id in topic_documents(state.question, state.allowed, deps.catalog):
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
        documents=tuple(documents) if len(documents) <= MAX_LISTED_DOCUMENTS else (),
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
    common = common_small_talk(state.question)
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
