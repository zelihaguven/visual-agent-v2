"""Belge işleme işçisinin döngüsü ve işleme işlevi; işçi API sürecinin içinde çalışır."""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from apps.worker.jobs import Ingest
from visual_agent.domain.document import DocumentMeta
from visual_agent.ingest.pipeline import IngestResult
from visual_agent.settings import Settings

logger = logging.getLogger(__name__)


async def process_until_stopped(
    process_next: Callable[[], Awaitable[bool]], stop: asyncio.Event, poll_seconds: float
) -> int:
    """İş varsa beklemeden sürer, yoksa bekler; tamamlanan bekleme sayısını döndürür."""
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
    from visual_agent.ingest.page_reader import CloudConfig, page_reader_from_setting
    from visual_agent.ingest.pipeline import ingest_document
    from visual_agent.ingest.tools import default_tools

    external = locate_tools(settings.soffice_path, settings.tesseract_path)
    for problem in external.problems():
        logger.warning(problem)
    key = settings.openrouter_api_key
    cloud = None
    if key is not None and key.get_secret_value():
        cloud = CloudConfig(
            base_url=str(settings.openrouter_url).rstrip("/"),
            api_key=key.get_secret_value(),
            cache=Path(settings.reader_cache_directory),
            reader_model=settings.reader_model,
            figure_check_model=settings.reader_figure_check_model,
        )
    tools = default_tools(external, page_reader_from_setting(settings.page_reader), cloud)

    def ingest(path: Path, meta: DocumentMeta, work: Path) -> IngestResult:
        return ingest_document(path, meta, tools, work)

    return ingest
