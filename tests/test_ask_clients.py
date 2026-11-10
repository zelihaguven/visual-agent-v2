"""Uygulama ve ölçüm model istemcilerini aynı yerden kurar."""

import asyncio

import httpx
import pytest

from tests.test_ask_pipeline import FakeRetriever, make_deps
from visual_agent.ask.clients import ModelClients, ask_deps, build_model_clients
from visual_agent.generation.openrouter import ServiceUnavailable
from visual_agent.settings import Settings

ANSWER_MODEL = "google/gemma-4-26b-a4b-it"
ZDR = {
    "data": [
        {"model_id": ANSWER_MODEL, "tag": "deepinfra", "safety_retention": False},
        {"model_id": ANSWER_MODEL, "tag": "venice", "safety_retention": False},
        {"model_id": ANSWER_MODEL, "tag": "risky", "safety_retention": True},
    ]
}


def _settings(answer_model: str = ANSWER_MODEL) -> Settings:
    return Settings(
        _env_file=None,
        answer_model=answer_model,
        answer_providers=("deepinfra", "venice", "parasail"),
        translation_model=ANSWER_MODEL,
        translation_providers=("venice",),
    )


def _build(settings: Settings, requests: list[httpx.Request]) -> ModelClients:
    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=ZDR)

    async def run() -> ModelClients:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http:
            return await build_model_clients(http, settings, "anahtar")

    return asyncio.run(run())


def test_only_zdr_providers_from_the_settings_are_used() -> None:
    requests: list[httpx.Request] = []

    clients = _build(_settings(), requests)

    assert [str(r.url) for r in requests] == ["https://openrouter.ai/api/v1/endpoints/zdr"]
    options = clients.answer._options
    assert options.providers == ("deepinfra", "venice")
    assert options.ignored_providers == ("risky",)
    assert clients.system_prompt


def test_a_model_without_a_zdr_endpoint_is_refused() -> None:
    with pytest.raises(ServiceUnavailable, match="ZDR"):
        _build(_settings(answer_model="baska/model"), [])


def test_ask_deps_wire_every_client() -> None:
    clients = _build(_settings(), [])
    base = make_deps(None)  # type: ignore[arg-type]
    retriever = FakeRetriever()

    deps = ask_deps(base.catalog, base.identifiers, retriever, clients)

    assert (deps.retriever, deps.answer_client, deps.system_prompt) == (
        retriever,
        clients.answer,
        clients.system_prompt,
    )
    assert (deps.translator, deps.rewriter, deps.intent_classifier) == (
        clients.translator,
        clients.rewriter,
        clients.intent_classifier,
    )
