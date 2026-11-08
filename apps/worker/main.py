"""Belge işleme işçisi. A3'e kadar yalnız kuyruğu bekleyen döngüdür."""

import asyncio
import logging
import signal
import threading
from collections.abc import Callable
from pathlib import Path

from apps.worker.jobs import DocumentProcessor
from visual_agent.domain.document import DocumentMeta
from visual_agent.ingest.pipeline import IngestResult
from visual_agent.settings import Settings

logger = logging.getLogger(__name__)


def run_worker(
    stop: threading.Event,
    poll_seconds: float,
    process_next: Callable[[], bool] = lambda: False,
) -> int:
    """İş varsa beklemeden sürer, yoksa bekler; tamamlanan bekleme sayısını döndürür."""
    polls = 0
    while not stop.is_set():
        if process_next():
            continue
        if stop.wait(poll_seconds):
            break
        polls += 1
    return polls


async def _open_processor(settings: Settings) -> DocumentProcessor:
    import asyncpg
    from qdrant_client import AsyncQdrantClient

    from apps.api.services import COLLECTION
    from apps.worker.indexing import LazyIndexer
    from visual_agent.catalog.repository import DocumentRepository
    from visual_agent.ingest.pipeline import ingest_document
    from visual_agent.ingest.tools import default_tools
    from visual_agent.retrieval.qdrant_store import QdrantChunkStore

    pool = await asyncpg.create_pool(str(settings.database_url))
    repository = DocumentRepository(pool)
    await repository.migrate()
    store = QdrantChunkStore(AsyncQdrantClient(url=str(settings.qdrant_url)), COLLECTION)
    tools = default_tools()

    def ingest(path: Path, meta: DocumentMeta, work: Path) -> IngestResult:
        return ingest_document(path, meta, tools, work)

    return DocumentProcessor(repository, LazyIndexer(store), ingest)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    stop = threading.Event()

    def request_stop(signum: int, _frame: object) -> None:
        logger.info("Durdurma sinyali alındı: %s", signal.Signals(signum).name)
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    logger.info("İşçi başladı")
    if settings.database_url is None:
        run_worker(stop, settings.worker_poll_seconds)
    else:
        loop = asyncio.new_event_loop()
        processor = loop.run_until_complete(_open_processor(settings))
        run_worker(
            stop,
            settings.worker_poll_seconds,
            lambda: loop.run_until_complete(processor.process_next()),
        )
    logger.info("İşçi durdu")


if __name__ == "__main__":
    main()
