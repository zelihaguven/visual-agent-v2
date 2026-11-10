"""Kuyruktaki belgeyi işler, indeksler ve hazır işaretler."""

import asyncio
import logging
import shutil
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol

from visual_agent.ask.language import detect_language
from visual_agent.catalog.repository import StoredDocument
from visual_agent.domain.document import Chunk, DocumentMeta
from visual_agent.ingest.external import MissingTool
from visual_agent.ingest.formats import UnsupportedFormat
from visual_agent.ingest.pipeline import IngestReport, IngestResult

logger = logging.getLogger(__name__)

_LANGUAGE_SAMPLE_CHUNKS = 40
_GENERIC_FAILURE = "Belge işlenemedi. Dosyanın bozuk olmadığını kontrol edip yeniden yükleyin."
_DISPLAY_NAME = "display.pdf"

Ingest = Callable[[Path, DocumentMeta, Path], IngestResult]


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
    ) -> None: ...

    async def mark_failed(self, doc_id: str, message: str) -> None: ...


class Indexer(Protocol):
    async def index(self, doc_id: str, access: Sequence[str], chunks: Sequence[Chunk]) -> None: ...

    async def remove(self, doc_id: str) -> None: ...


def _document_language(chunks: Sequence[Chunk], fallback: str) -> str:
    sample = " ".join(chunk.text for chunk in chunks[:_LANGUAGE_SAMPLE_CHUNKS])
    return detect_language(sample) if sample else fallback


class DocumentProcessor:
    def __init__(self, repository: JobRepository, indexer: Indexer, ingest: Ingest) -> None:
        self._repository = repository
        self._indexer = indexer
        self._ingest = ingest
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
        except (UnsupportedFormat, MissingTool) as error:
            await self._repository.mark_failed(document.doc_id, str(error))
        except Exception:
            logger.exception("Belge işlenemedi: %s", document.doc_id)
            await self._repository.mark_failed(document.doc_id, _GENERIC_FAILURE)

    async def _process(self, document: StoredDocument) -> None:
        source = Path(document.stored_path)
        meta = DocumentMeta(
            doc_id=document.doc_id,
            title=document.title,
            language=document.language,
            access=document.access,
        )
        with tempfile.TemporaryDirectory() as work:
            result = await asyncio.to_thread(self._ingest, source, meta, Path(work))
            display = self._keep_display_pdf(result.display_pdf, source)
        await self._indexer.index(document.doc_id, document.access, result.chunks)
        try:
            await self._repository.mark_ready(
                document.doc_id,
                _document_language(result.chunks, document.language),
                result.chunks,
                result.report,
                display,
            )
        except Exception:
            await self._discard_vectors(document.doc_id)
            raise

    async def _discard_vectors(self, doc_id: str) -> None:
        """Temizlik başarısız olsa da belge hazır sayılmadığı için aramaya girmez."""
        try:
            await self._indexer.remove(doc_id)
        except Exception:
            logger.exception("Belgenin vektörleri temizlenemedi: %s", doc_id)

    @staticmethod
    def _keep_display_pdf(display_pdf: Path | None, source: Path) -> str | None:
        if display_pdf is None:
            return None
        if display_pdf == source:
            return str(source)
        target = source.parent / _DISPLAY_NAME
        shutil.copyfile(display_pdf, target)
        return str(target)
