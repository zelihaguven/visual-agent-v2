"""Soru hattı: sıralı adımlar. Bir adım sonuç üretirse hat orada durur."""

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, replace

from visual_agent.ask.context import next_context, resolve_context
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.intent import resolve_intent
from visual_agent.ask.related import with_related_headings
from visual_agent.ask.steps import AskState, generate, resolve_scope, retrieve, verify
from visual_agent.domain.result import AskOutcome, Failed

__all__ = ["AskDeps", "AskRequest", "answer_question"]

Step = Callable[[AskState, AskDeps], Awaitable[AskState]]


@dataclass(frozen=True)
class NamedStep:
    name: str
    run: Step


PIPELINE = (
    NamedStep("context", resolve_context),
    NamedStep("scope", resolve_scope),
    NamedStep("intent", resolve_intent),
    NamedStep("retrieve", retrieve),
    NamedStep("generate", generate),
    NamedStep("verify", verify),
)


def _split_translation(timings: dict[str, float], translate: float | None) -> dict[str, float]:
    """Çeviri arama adımının içinde çalışır; gecikme kararı için ayrı süre olarak görünür."""
    if translate is None or "retrieve" not in timings:
        return timings
    return {
        **timings,
        "retrieve": max(timings["retrieve"] - translate, 0.0),
        "translate": translate,
    }


async def answer_question(request: AskRequest, deps: AskDeps) -> AskOutcome:
    state = AskState(request=request)
    timings: dict[str, float] = {}
    for step in PIPELINE:
        started = time.perf_counter()
        if request.on_event is not None:
            request.on_event({"type": "status", "stage": step.name})
        state = await step.run(state, deps)
        timings = {**timings, step.name: time.perf_counter() - started}
        if state.result is not None:
            break
    result = state.result or Failed(reason="Cevap üretilemedi.")
    final = replace(state, result=with_related_headings(result, state.hits, state.language))
    timings = _split_translation(timings, final.translate_seconds)
    assert final.result is not None
    return AskOutcome(
        result=final.result,
        hits=final.hits,
        timings=timings,
        cost_usd=final.cost_usd,
        provider=final.provider,
        first_verified_seconds=final.first_verified_seconds,
        provider_attempts=final.provider_attempts,
        provider_seconds=final.provider_seconds,
        question=final.question,
        context=next_context(final),
        scope_inherited=final.scope_inherited,
    )
