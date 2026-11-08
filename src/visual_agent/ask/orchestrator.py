"""Soru hattı: sıralı adımlar. Bir adım sonuç üretirse hat orada durur."""

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, replace

from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.steps import AskState, generate, resolve_scope, retrieve, verify
from visual_agent.domain.result import AskOutcome, Failed

__all__ = ["AskDeps", "AskRequest", "answer_question"]

Step = Callable[[AskState, AskDeps], Awaitable[AskState]]


@dataclass(frozen=True)
class NamedStep:
    name: str
    run: Step


PIPELINE = (
    NamedStep("scope", resolve_scope),
    NamedStep("retrieve", retrieve),
    NamedStep("generate", generate),
    NamedStep("verify", verify),
)


async def answer_question(request: AskRequest, deps: AskDeps) -> AskOutcome:
    state = AskState(request=request)
    timings: dict[str, float] = {}
    for step in PIPELINE:
        started = time.perf_counter()
        state = await step.run(state, deps)
        timings = {**timings, step.name: time.perf_counter() - started}
        if state.result is not None:
            break
    final = replace(state, result=state.result or Failed(reason="Cevap üretilemedi."))
    assert final.result is not None
    return AskOutcome(
        result=final.result,
        hits=final.hits,
        timings=timings,
        cost_usd=final.cost_usd,
        provider=final.provider,
    )
