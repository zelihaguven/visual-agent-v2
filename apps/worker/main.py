"""Belge işleme işçisi: yerelde API sürecinin içinde, sunucuda ayrı süreç olarak çalışır."""

import asyncio
import logging
import signal
import threading
from collections.abc import Awaitable, Callable
from pathlib import Path

from apps.worker.jobs import DocumentProcessor, Ingest
from visual_agent.domain.document import DocumentMeta
from visual_agent.ingest.pipeline import IngestResult
from visual_agent.settings import Settings

logger = logging.getLogger(__name__)

EMBEDDED_QDRANT_REFUSED = (
    "Gömülü Qdrant klasörü tek sürece kilitlenir; ayrı işçi yalnız Qdrant sunucusuyla"
    " (VA_QDRANT_URL) çalışır. Yerelde işçi API sürecinin içinde çalışır."
)


def run_worker(
    stop: threading.Event,
    poll_seconds: float,
    process_next: Callable[[], bool] = lambda: False,
) -> int:
    """İş varsa beklemeden sürer, yoksa bekler; tamamlanan bekleme sayısını döndürür."""
    polls = 0
    while not stop.is_set():
        try:
            if process_next():
                continue
        except Exception:
            logger.warning("İş alınamadı; bir sonraki turda yeniden denenecek", exc_info=True)
        if stop.wait(poll_seconds):
            break
        polls += 1
    return polls


async def process_until_stopped(
    process_next: Callable[[], Awaitable[bool]], stop: asyncio.Event, poll_seconds: float
) -> int:
    """API içindeki işçi: run_worker ile aynı kural, olay döngüsünü bloklamadan."""
    polls = 0
    while not stop.is_set():
        try:
            if await process_next():
                continue
        except Exception:
            logger.warning("İş alınamadı; bir sonraki turda yeniden denenecek", exc_info=True)
        try:
            await asyncio.wait_for(stop.wait(), poll_seconds)
        except TimeoutError:
            polls += 1
    return polls


def default_ingest(settings: Settings) -> Ingest:
    """Belge işleme araçları ağırdır; yalnız işçi açılırken yüklenir. Eksik araç bildirilir."""
    from visual_agent.ingest.external import locate_tools
    from visual_agent.ingest.pipeline import ingest_document
    from visual_agent.ingest.tools import default_tools

    external = locate_tools(settings.soffice_path, settings.tesseract_path)
    for problem in external.problems():
        logger.warning(problem)
    tools = default_tools(external)

    def ingest(path: Path, meta: DocumentMeta, work: Path) -> IngestResult:
        return ingest_document(path, meta, tools, work)

    return ingest


async def _open_processor(settings: Settings) -> DocumentProcessor:
    from apps.worker.indexing import LazyIndexer, SharedEncoders
    from visual_agent.catalog.repository import open_repository
    from visual_agent.retrieval.qdrant_store import COLLECTION, QdrantChunkStore, open_client

    repository = open_repository(Path(settings.database_path))
    await repository.migrate()
    await repository.requeue_interrupted()
    store = QdrantChunkStore(open_client(str(settings.qdrant_url), None), COLLECTION)
    return DocumentProcessor(
        repository, LazyIndexer(store, SharedEncoders()), default_ingest(settings)
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    if settings.qdrant_path is not None:
        raise SystemExit(EMBEDDED_QDRANT_REFUSED)
    stop = threading.Event()

    def request_stop(signum: int, _frame: object) -> None:
        logger.info("Durdurma sinyali alındı: %s", signal.Signals(signum).name)
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    logger.info("İşçi başladı")
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
