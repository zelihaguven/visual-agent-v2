"""Gerçek bağımlılıkları kurar: SQLite, Qdrant, modeller ve OpenRouter."""

import asyncio
import logging
from collections.abc import AsyncIterator, MutableMapping
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path

import httpx

from apps.api.documents import retry_deletions
from apps.api.main import ApiServices
from apps.api.question_log import open_log
from apps.api.voice import fixed_notice_texts, fixed_reply_texts
from apps.worker.indexing import LazyIndexer, SharedEncoders
from visual_agent.ask.clients import build_ask_deps
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.orchestrator import answer_question
from visual_agent.catalog.identifiers import SnapshotProvider, build_identifier_index
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.catalog.repository import DocumentRepository, open_repository
from visual_agent.domain.result import AskOutcome, Failed
from visual_agent.ingest.elements import IngestState
from visual_agent.retrieval.hybrid import HybridRetriever
from visual_agent.retrieval.qdrant_store import COLLECTION, QdrantChunkStore, open_client
from visual_agent.settings import Settings
from visual_agent.voice.client import CachingVoice, OpenRouterVoice, Voice

logger = logging.getLogger(__name__)

_MISSING_KEY = "Cevap servisi yapılandırılmamış. OpenRouter anahtarını ekleyin."


class AskRuntime:
    """Ağır modeller ilk soruda bir kez yüklenir; API hızlı açılır."""

    def __init__(
        self,
        settings: Settings,
        http: httpx.AsyncClient,
        store: QdrantChunkStore,
        snapshots: SnapshotProvider,
        encoders: SharedEncoders,
    ) -> None:
        self._settings = settings
        self._http = http
        self._store = store
        self._encoders = encoders
        self._snapshots = snapshots
        self._deps: AskDeps | None = None
        self._lock = asyncio.Lock()

    async def _build_deps(self, api_key: str) -> AskDeps:
        dense, sparse = await self._encoders.get()
        await self._store.ensure_collection(dense.size)
        retriever = HybridRetriever(dense, sparse, self._store)
        # Katalog burada okunmaz: her soruda güncel görüntüyle değiştirilir (`ask`).
        return await build_ask_deps(
            self._http,
            self._settings,
            api_key,
            DocumentCatalog(),
            build_identifier_index(()),
            retriever,
        )

    async def _ensure_deps(self, api_key: str) -> AskDeps:
        async with self._lock:
            if self._deps is None:
                self._deps = await self._build_deps(api_key)
            return self._deps

    async def warm_up(self) -> None:
        """Ağır modeller açılışta yüklenir; ilk soru, selam bile olsa, beklemez."""
        key = self._settings.openrouter_api_key
        if key is None or not key.get_secret_value():
            return
        try:
            await self._ensure_deps(key.get_secret_value())
        except Exception:
            logger.warning("Modeller açılışta yüklenemedi; ilk soruda denenecek", exc_info=True)

    async def ask(self, request: AskRequest) -> AskOutcome:
        key = self._settings.openrouter_api_key
        if key is None or not key.get_secret_value():
            return AskOutcome(result=Failed(reason=_MISSING_KEY), timings={})
        deps = await self._ensure_deps(key.get_secret_value())
        snapshot = await self._snapshots.current()
        deps = replace(deps, catalog=snapshot.catalog, identifiers=snapshot.identifiers)
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


async def _process_documents(
    repository: DocumentRepository,
    store: QdrantChunkStore,
    encoders: SharedEncoders,
    stop: asyncio.Event,
    settings: Settings,
    progress: MutableMapping[str, IngestState],
) -> None:
    """İşçi API sürecinde: gömülü Qdrant klasörü ve embedding modeli paylaşılır; okuma
    ilerlemesi `progress` sözlüğüyle API'ye geçer.

    İşçi modülleri burada yüklenir: belge işleme paketleri (ingest eki) kurulu olmayabilir.
    """
    await repository.requeue_interrupted()
    try:
        from apps.worker.jobs import DocumentProcessor
        from apps.worker.run import default_ingest, process_until_stopped
        from apps.worker.topics import open_topic_assigner

        ingest = await asyncio.to_thread(default_ingest, settings)
    except ImportError:
        logger.error(
            "Belge işleme paketleri kurulu değil; yüklenen belgeler kuyrukta bekleyecek."
            " Kurulum: uv sync --extra ingest --extra retrieval"
        )
        return
    topics = await open_topic_assigner(settings, repository)
    processor = DocumentProcessor(
        repository, LazyIndexer(store, encoders), ingest, topics, progress
    )
    logger.info("Belge işçisi API sürecinde başladı")
    # Konu verme belge işlemeyi beklemez: uzun bir taramayı işlerken eski belgeler adlandırılır.
    loops = [process_until_stopped(processor.process_next, stop, settings.worker_poll_seconds)]
    if topics is not None:
        loops.append(
            process_until_stopped(topics.assign_next_missing, stop, settings.worker_poll_seconds)
        )
    await asyncio.gather(*loops)


async def _retry_deletions(
    repository: DocumentRepository, store: QdrantChunkStore, storage: Path
) -> None:
    """Önceki çalışmada yarım kalan silmeler açılışta tamamlanır."""
    try:
        finished = await retry_deletions(repository, store.delete_document, storage)
    except Exception:
        logger.warning("Yarım kalan silmeler tamamlanamadı", exc_info=True)
        return
    if finished:
        logger.info("Yarım kalan %d silme tamamlandı", finished)


@asynccontextmanager
async def open_services(settings: Settings) -> AsyncIterator[ApiServices]:
    repository = open_repository(Path(settings.database_path), Path(settings.storage_directory))
    await repository.migrate()
    question_log = open_log(Path(settings.database_path))
    await question_log.migrate()
    qdrant = open_client(str(settings.qdrant_url), settings.qdrant_path)
    store = QdrantChunkStore(qdrant, COLLECTION)
    encoders = SharedEncoders()
    storage = Path(settings.storage_directory)
    storage.mkdir(parents=True, exist_ok=True)
    stop = asyncio.Event()
    progress: dict[str, IngestState] = {}
    async with httpx.AsyncClient() as http:
        runtime = AskRuntime(settings, http, store, SnapshotProvider(repository), encoders)
        background = [
            asyncio.create_task(runtime.warm_up()),
            asyncio.create_task(_retry_deletions(repository, store, storage)),
            asyncio.create_task(
                _process_documents(repository, store, encoders, stop, settings, progress)
            ),
        ]
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
                remove_vectors=store.delete_document,
                question_log=question_log,
                processing_progress=progress,
            )
        finally:
            stop.set()
            for task in background:
                task.cancel()
            await asyncio.gather(*background, return_exceptions=True)
            await qdrant.close()
