"""Netleştirme adayı belgeler aynı cevabı veriyorsa sormadan cevaplanır.

Model birden çok belge arasında netleştirme isterse, en üst sıradaki aday belgenin
parçalarıyla bir kez daha cevap istenir. Cevap ancak şu durumda gösterilir: her cümlesi
doğrulanır ve her alıntısı (en az birkaç kelime) diğer her aday belgenin parçalarında da
birebir geçer. O zaman bütün aday belgeler kaynak olarak gösterilir. Emin olunamayan her
durumda (kısa alıntı, komut, şekil, eksik ya da farklı metin, servis hatası) netleştirme
sorusu kalır.
"""

import logging
from collections.abc import Callable, Sequence

from visual_agent.ask.deps import AskDeps
from visual_agent.domain.answer import AnswerKind, ModelItem, VerificationStatus
from visual_agent.domain.result import Answered, AnsweredItem, Citation, Hit
from visual_agent.generation.openrouter import ServiceUnavailable
from visual_agent.generation.parse import ParseFailure, parse_answer
from visual_agent.generation.sources import build_user_message, to_prompt_sources
from visual_agent.verification.answer import verify_answer
from visual_agent.verification.quote import quote_matches

logger = logging.getLogger(__name__)

MIN_SHARED_QUOTE_WORDS = 3

Cite = Callable[[Hit], Citation]
LanguageOf = Callable[[str], str]


def candidate_documents(hits: Sequence[Hit], option_numbers: Sequence[int]) -> list[str]:
    """Netleştirme seçeneklerinin belgeleri, arama sırasıyla."""
    chosen = {hits[number - 1].chunk.doc_id for number in option_numbers}
    return list(dict.fromkeys(hit.chunk.doc_id for hit in hits if hit.chunk.doc_id in chosen))


def _shared_hit(quote: str, hits: Sequence[Hit], language_of: LanguageOf) -> Hit | None:
    if len(quote.split()) < MIN_SHARED_QUOTE_WORDS:
        return None
    return next(
        (
            hit
            for hit in hits
            if quote_matches(quote, hit.chunk.text, language_of(hit.chunk.doc_id))
        ),
        None,
    )


def _citations_elsewhere(
    item: ModelItem, others: Sequence[Sequence[Hit]], cite: Cite, language_of: LanguageOf
) -> list[Citation] | None:
    """Öğenin her alıntısı her diğer belgede geçiyorsa o belgelerin atıfları; yoksa None."""
    citations: list[Citation] = []
    for hits in others:
        for quote in item.quotes:
            found = _shared_hit(quote.text, hits, language_of)
            if found is None:
                return None
            citations.append(cite(found))
    return citations


def shared_answer(
    content: str,
    finish: str | None,
    first: Sequence[Hit],
    others: Sequence[Sequence[Hit]],
    cite: Cite,
    language: str,
    language_of: LanguageOf,
) -> Answered | None:
    """İlk belgeden gelen cevap bütün aday belgelerde birebir geçiyorsa cevap; yoksa None."""
    parsed = parse_answer(content, finish)
    if isinstance(parsed, ParseFailure) or parsed.kind is not AnswerKind.ANSWER:
        return None
    verification = verify_answer(parsed, to_prompt_sources(first, language_of), language)
    if verification.status is not VerificationStatus.VERIFIED:
        return None
    items = []
    for item, check in zip(parsed.items, verification.items, strict=True):
        if item.code_source_no is not None or not item.quotes:
            return None
        elsewhere = _citations_elsewhere(item, others, cite, language_of)
        if elsewhere is None:
            return None
        own = [cite(first[number - 1]) for number in check.source_numbers]
        unique = {citation.chunk_id: citation for citation in [*own, *elsewhere]}
        items.append(AnsweredItem(text=item.text, citations=tuple(unique.values()), verified=True))
    return Answered(status=VerificationStatus.VERIFIED, items=tuple(items))


async def agreed_answer(
    question: str,
    language: str,
    hits: Sequence[Hit],
    documents: Sequence[str],
    deps: AskDeps,
    cite: Cite,
) -> tuple[Answered | None, float]:
    """Aday belgeler aynı cevabı veriyorsa cevap ve ek isteğin maliyeti; vermiyorsa None."""
    if len(documents) < 2:
        return None, 0.0
    first = [hit for hit in hits if hit.chunk.doc_id == documents[0]]
    others = [[hit for hit in hits if hit.chunk.doc_id == doc] for doc in documents[1:]]
    messages = [
        {"role": "system", "content": deps.system_prompt},
        {"role": "user", "content": build_user_message(first, question, language)},
    ]
    try:
        stream = await deps.answer_client.stream(messages)
    except ServiceUnavailable:
        logger.warning("Aday belgelerin cevabı karşılaştırılamadı; netleştirme soruluyor")
        return None, 0.0
    if stream.incomplete:
        return None, stream.cost_usd
    shared = shared_answer(
        stream.content, stream.finish, first, others, cite, language, deps.catalog.language
    )
    return shared, stream.cost_usd
