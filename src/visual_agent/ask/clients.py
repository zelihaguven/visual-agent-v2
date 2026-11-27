"""Soru hattının model istemcileri ve bağımlılıkları; uygulama ve ölçüm aynı yerden kurar."""

import httpx

from visual_agent.ask.deps import AskDeps, Retriever
from visual_agent.catalog.identifiers import IdentifierIndex
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.generation.helpers import (
    JsonModel,
    make_intent_classifier,
    make_rewriter,
    make_translator,
)
from visual_agent.generation.openrouter import (
    AnswerClient,
    AnswerClientOptions,
    ZdrEntry,
    fetch_zdr_index,
    select_providers,
)
from visual_agent.generation.prompts import load_answer_prompt, load_answer_schema
from visual_agent.settings import Settings


def helper_model(
    http: httpx.AsyncClient, settings: Settings, api_key: str, index: dict[str, ZdrEntry]
) -> JsonModel:
    """Yardımcı model (çeviri, takip tamamlama, niyet, konu adı); yalnız ZDR sağlayıcılarla."""
    providers, ignored = select_providers(settings.helper_model, settings.helper_providers, index)
    url = str(settings.openrouter_url).rstrip("/")
    return JsonModel(http, url, api_key, settings.helper_model, providers, ignored)


async def build_ask_deps(
    http: httpx.AsyncClient,
    settings: Settings,
    api_key: str,
    catalog: DocumentCatalog,
    identifiers: IdentifierIndex,
    retriever: Retriever,
) -> AskDeps:
    """Yalnız veri saklamayan (ZDR) sağlayıcılarla cevap ve yardımcı model istemcileri.

    Model istemcileri bir kez kurulur; katalog değişince çağıran `dataclasses.replace` ile
    yalnız `catalog` ve `identifiers` alanlarını yeniler."""
    url = str(settings.openrouter_url).rstrip("/")
    index = await fetch_zdr_index(http, url, api_key)
    providers, ignored = select_providers(settings.answer_model, settings.answer_providers, index)
    answer = AnswerClient(
        http,
        base_url=url,
        api_key=api_key,
        options=AnswerClientOptions(
            model=settings.answer_model,
            providers=providers,
            ignored_providers=ignored,
            schema=load_answer_schema(),
            max_tokens=settings.answer_max_tokens,
            first_token_seconds=settings.answer_first_token_seconds,
            runaway_whitespace_limit=settings.stream_runaway_limit,
        ),
    )
    # Tek yardımcı model üç işi yapar: BM25 çevirisi, takip sorusunu tamamlama, niyet.
    helper = helper_model(http, settings, api_key, index)
    return AskDeps(
        catalog=catalog,
        identifiers=identifiers,
        retriever=retriever,
        answer_client=answer,
        system_prompt=load_answer_prompt(),
        translator=make_translator(helper),
        rewriter=make_rewriter(helper),
        intent_classifier=make_intent_classifier(helper),
    )
