"""Soru hattının model istemcileri ve bağımlılıkları; uygulama ve ölçüm aynı yerden kurar."""

from dataclasses import dataclass

import httpx

from visual_agent.ask.deps import AskDeps, Retriever
from visual_agent.catalog.identifiers import IdentifierIndex
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.generation.intent import IntentClassifier, make_intent_classifier
from visual_agent.generation.json_model import JsonModel
from visual_agent.generation.openrouter import (
    AnswerClient,
    AnswerClientOptions,
    fetch_zdr_index,
    select_providers,
)
from visual_agent.generation.prompts import load_answer_prompt, load_answer_schema
from visual_agent.generation.rewrite import Rewriter, make_rewriter
from visual_agent.generation.translate import Translator, make_translator
from visual_agent.settings import Settings


@dataclass(frozen=True)
class ModelClients:
    answer: AnswerClient
    translator: Translator
    rewriter: Rewriter
    intent_classifier: IntentClassifier
    system_prompt: str


async def build_model_clients(
    http: httpx.AsyncClient, settings: Settings, api_key: str
) -> ModelClients:
    """Yalnız veri saklamayan (ZDR) sağlayıcılarla cevap ve yardımcı model istemcileri."""
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
    helper, helper_ignored = select_providers(
        settings.helper_model, settings.helper_providers, index
    )
    helper_model = JsonModel(http, url, api_key, settings.helper_model, helper, helper_ignored)
    return ModelClients(
        answer=answer,
        translator=make_translator(helper_model),
        rewriter=make_rewriter(helper_model),
        intent_classifier=make_intent_classifier(helper_model),
        system_prompt=load_answer_prompt(),
    )


def ask_deps(
    catalog: DocumentCatalog,
    identifiers: IdentifierIndex,
    retriever: Retriever,
    clients: ModelClients,
) -> AskDeps:
    return AskDeps(
        catalog=catalog,
        identifiers=identifiers,
        retriever=retriever,
        answer_client=clients.answer,
        system_prompt=clients.system_prompt,
        translator=clients.translator,
        rewriter=clients.rewriter,
        intent_classifier=clients.intent_classifier,
    )
