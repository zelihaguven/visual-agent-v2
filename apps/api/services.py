"""Gerçek bağımlılıkları kurar: SQLite, Qdrant, modeller ve OpenRouter."""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import httpx
from qdrant_client import AsyncQdrantClient

from apps.api.main import ApiServices
from apps.api.voice import fixed_notice_texts, fixed_reply_texts
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.orchestrator import answer_question
from visual_agent.catalog.repository import open_repository
from visual_agent.catalog.snapshot import SnapshotProvider
from visual_agent.domain.result import AskOutcome, Failed
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
from visual_agent.retrieval.hybrid import HybridRetriever
from visual_agent.retrieval.qdrant_store import QdrantChunkStore
from visual_agent.settings import Settings
from visual_agent.voice.client import CachingVoice, OpenRouterVoice, Voice

logger = logging.getLogger(__name__)

COLLECTION = "documents"
_MISSING_KEY = "Cevap servisi yapılandırılmamış. OpenRouter anahtarını ekleyin."


@dataclass(frozen=True)
class _ModelClients:
    retriever: HybridRetriever
    answer: AnswerClient
    translator: Translator
    rewriter: Rewriter
    intent_classifier: IntentClassifier
    system_prompt: str


class AskRuntime:
    """Ağır modeller ilk soruda bir kez yüklenir; API hızlı açılır."""

    def __init__(
        self,
        settings: Settings,
        http: httpx.AsyncClient,
        store: QdrantChunkStore,
        snapshots: SnapshotProvider,
    ) -> None:
        self._settings = settings
        self._http = http
        self._store = store
        self._snapshots = snapshots
        self._clients: _ModelClients | None = None
        self._lock = asyncio.Lock()

    async def _build_clients(self, api_key: str) -> _ModelClients:
        from visual_agent.retrieval.encoders import BgeM3Dense, Bm25Sparse

        settings = self._settings
        url = str(settings.openrouter_url).rstrip("/")
        dense, sparse = await asyncio.gather(
            asyncio.to_thread(BgeM3Dense), asyncio.to_thread(Bm25Sparse)
        )
        await self._store.ensure_collection(dense.size)
        index = await fetch_zdr_index(self._http, url, api_key)
        providers, ignored = select_providers(
            settings.answer_model, settings.answer_providers, index
        )
        answer = AnswerClient(
            self._http,
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
        translation, translation_ignored = select_providers(
            settings.translation_model, settings.translation_providers, index
        )
        helper_model = JsonModel(
            self._http, url, api_key, settings.translation_model, translation, translation_ignored
        )
        return _ModelClients(
            retriever=HybridRetriever(dense, sparse, self._store),
            answer=answer,
            translator=make_translator(helper_model),
            rewriter=make_rewriter(helper_model),
            intent_classifier=make_intent_classifier(helper_model),
            system_prompt=load_answer_prompt(),
        )

    async def _ensure_clients(self, api_key: str) -> _ModelClients:
        async with self._lock:
            if self._clients is None:
                self._clients = await self._build_clients(api_key)
            return self._clients

    async def warm_up(self) -> None:
        """Ağır modeller açılışta yüklenir; ilk soru, selam bile olsa, beklemez."""
        key = self._settings.openrouter_api_key
        if key is None or not key.get_secret_value():
            return
        try:
            await self._ensure_clients(key.get_secret_value())
        except Exception:
            logger.warning("Modeller açılışta yüklenemedi; ilk soruda denenecek", exc_info=True)

    async def ask(self, request: AskRequest) -> AskOutcome:
        key = self._settings.openrouter_api_key
        if key is None or not key.get_secret_value():
            return AskOutcome(result=Failed(reason=_MISSING_KEY), timings={})
        clients = await self._ensure_clients(key.get_secret_value())
        snapshot = await self._snapshots.current()
        deps = AskDeps(
            catalog=snapshot.catalog,
            identifiers=snapshot.identifiers,
            retriever=clients.retriever,
            answer_client=clients.answer,
            system_prompt=clients.system_prompt,
            translator=clients.translator,
            rewriter=clients.rewriter,
            intent_classifier=clients.intent_classifier,
        )
        return await answer_question(request, deps)


def _make_voice(settings: Settings, http: httpx.AsyncClient) -> Voice | None:
    key = settings.openrouter_api_key
    if key is None or not key.get_secret_value():
        return None
    openrouter = OpenRouterVoice(
        http=http,
        base_url=str(settings.openrouter_url).rstrip("/"),
        api_key=key.get_secret_value(),
        stt_model=settings.stt_model,
        stt_language=settings.stt_language,
        tts_model=settings.tts_model,
        tts_voice=settings.tts_voice,
        tts_format=settings.tts_format,
    )
    return CachingVoice(openrouter, (*fixed_reply_texts(), *fixed_notice_texts()))


@asynccontextmanager
async def open_services(settings: Settings) -> AsyncIterator[ApiServices]:
    repository = open_repository(Path(settings.database_path))
    await repository.migrate()
    qdrant = AsyncQdrantClient(url=str(settings.qdrant_url))
    storage = Path(settings.storage_directory)
    storage.mkdir(parents=True, exist_ok=True)
    async with httpx.AsyncClient() as http:
        runtime = AskRuntime(
            settings, http, QdrantChunkStore(qdrant, COLLECTION), SnapshotProvider(repository)
        )
        warm_up = asyncio.create_task(runtime.warm_up())
        try:
            yield ApiServices(
                repository=repository,
                ask=runtime.ask,
                storage_directory=storage,
                voice=_make_voice(settings, http),
                health_checks={
                    "database": repository.ping,
                    "qdrant": qdrant.get_collections,
                },
            )
        finally:
            warm_up.cancel()
            await qdrant.close()
