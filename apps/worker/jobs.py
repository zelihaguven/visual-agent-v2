"""Kuyruktaki belgeyi işler, indeksler ve hazır işaretler."""

import asyncio
import logging
import shutil
import tempfile
from collections.abc import Callable, MutableMapping, Sequence
from pathlib import Path
from typing import Protocol

from apps.worker.topics import TopicAssigner
from visual_agent.ask.language import document_language
from visual_agent.catalog.repository import StoredDocument
from visual_agent.domain.document import UNDETECTED_LANGUAGE, Chunk, DocumentMeta
from visual_agent.ingest.external import ConversionFailed, MissingTool, ReaderUnavailable
from visual_agent.ingest.formats import UnsupportedFormat
from visual_agent.ingest.page_reader import READ_PROGRESS, ReadProgress
from visual_agent.ingest.pipeline import IngestReport, IngestResult

logger = logging.getLogger(__name__)

_GENERIC_FAILURE = "Belge işlenemedi. Dosyanın bozuk olmadığını kontrol edip yeniden yükleyin."
_DISPLAY_NAME = "display.pdf"

Ingest = Callable[[Path, DocumentMeta, Path], IngestResult]
ReadingProgress = tuple[str, int, int]
"""İşlenen belgenin okuyucu adımı: ("page" ya da "image", okunan, toplam)."""


class JobRepository(Protocol):
    async def claim_next(self) -> StoredDocument | None: ...

    async def requeue(self, doc_id: str) -> None: ...

    async def mark_ready(
        self,
        doc_id: str,
        language: str,
        chunks: Sequence[Chunk],
        report: IngestReport,
        display_pdf: str | None,
    ) -> bool: ...

    async def mark_failed(self, doc_id: str, message: str, waiting: bool = False) -> bool: ...

    async def purge(self, doc_id: str) -> None: ...


class Indexer(Protocol):
    async def index(self, doc_id: str, chunks: Sequence[Chunk]) -> None: ...

    async def remove(self, doc_id: str) -> None: ...


class DocumentProcessor:
    def __init__(
        self,
        repository: JobRepository,
        indexer: Indexer,
        ingest: Ingest,
        topics: TopicAssigner | None = None,
        progress: MutableMapping[str, ReadingProgress] | None = None,
    ) -> None:
        """progress: işlenen belgenin okuma ilerlemesi buraya yazılır (API okur); iş bitince
        silinir. Bellektedir: uygulama yeniden başlarsa iş de baştan başlar."""
        self._repository = repository
        self._indexer = indexer
        self._ingest = ingest
        self._topics = topics
        self._progress = progress
        self._interrupted: str | None = None

    async def process_next(self) -> bool:
        """Bir iş işlendiyse True döndürür; sonucu yazılamayan iş sonra kuyruğa döner."""
        if self._interrupted is not None:
            await self._repository.requeue(self._interrupted)
            self._interrupted = None
        document = await self._repository.claim_next()
        if document is None:
            return False
        try:
            await self._process_and_record(document)
        except Exception:
            self._interrupted = document.doc_id
            raise
        return True

    async def _process_and_record(self, document: StoredDocument) -> None:
        try:
            await self._process(document)
        except ReaderUnavailable as error:
            # Belge bozuk değil: okuyucu gelince "Yeniden işle" ile okunur.
            await self._fail(document, str(error), waiting=True)
        except (UnsupportedFormat, MissingTool, ConversionFailed) as error:
            await self._fail(document, str(error))
        except Exception:
            logger.exception("Belge işlenemedi: %s", document.doc_id)
            await self._fail(document, _GENERIC_FAILURE)
        finally:
            if self._progress is not None:
                self._progress.pop(document.doc_id, None)

    def _progress_sink(self, doc_id: str) -> ReadProgress | None:
        board = self._progress
        if board is None:
            return None

        def record(kind: str, done: int, total: int) -> None:
            board[doc_id] = (kind, done, total)

        return record

    async def _fail(self, document: StoredDocument, message: str, waiting: bool = False) -> None:
        """Belge işlenirken silindiyse hata yazılmaz; geride kalanları işçi temizler."""
        if not await self._repository.mark_failed(document.doc_id, message, waiting):
            await self._discard_deleted(document)

    async def _process(self, document: StoredDocument) -> None:
        source = Path(document.stored_path)
        # Belgenin dili yeniden işlemede de parçalardan belirlenir (aşağıda document_language).
        meta = DocumentMeta(
            doc_id=document.doc_id,
            title=document.title,
            language=UNDETECTED_LANGUAGE,
        )
        with tempfile.TemporaryDirectory() as work:
            # to_thread bağlamı kopyalar: okuyucu ilerlemeyi bu belgenin kaydına yazar.
            token = READ_PROGRESS.set(self._progress_sink(document.doc_id))
            try:
                result = await asyncio.to_thread(self._ingest, source, meta, Path(work))
            finally:
                READ_PROGRESS.reset(token)
            display = self._keep_display_pdf(result.display_pdf, source)
        await self._indexer.index(document.doc_id, result.chunks)
        try:
            ready = await self._repository.mark_ready(
                document.doc_id,
                document_language(result.chunks, document.language),
                result.chunks,
                result.report,
                display,
            )
        except Exception:
            await self._discard_vectors(document.doc_id)
            raise
        if not ready:
            await self._discard_deleted(document)
        elif self._topics is not None:
            await self._topics.assign_ready(document.doc_id)

    async def _discard_vectors(self, doc_id: str) -> bool:
        """Temizlik başarısız olsa da belge hazır sayılmadığı için aramaya girmez."""
        try:
            await self._indexer.remove(doc_id)
        except Exception:
            logger.exception("Belgenin vektörleri temizlenemedi: %s", doc_id)
            return False
        return True

    async def _discard_deleted(self, document: StoredDocument) -> None:
        """Belge işlenirken silindi: bu işin yazdığı vektörler ve dosyalar da kalmaz."""
        logger.info("Belge işlenirken silindi, sonucu atılıyor: %s", document.doc_id)
        vectors_removed = await self._discard_vectors(document.doc_id)
        directory = Path(document.stored_path).parent
        if directory.name == document.doc_id:
            shutil.rmtree(directory, ignore_errors=True)
        if vectors_removed and not directory.exists():
            await self._repository.purge(document.doc_id)

    @staticmethod
    def _keep_display_pdf(display_pdf: Path | None, source: Path) -> str | None:
        if display_pdf is None:
            return None
        if display_pdf == source:
            return str(source)
        target = source.parent / _DISPLAY_NAME
        shutil.copyfile(display_pdf, target)
        return str(target)
