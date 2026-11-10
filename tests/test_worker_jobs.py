import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from apps.worker.jobs import DocumentProcessor
from visual_agent.catalog.repository import DocumentStatus, StoredDocument
from visual_agent.catalog.snapshot import SnapshotProvider
from visual_agent.domain.document import Chunk, ChunkKind, DocumentMeta, SourceLocation
from visual_agent.ingest.pipeline import IngestReport, IngestResult


def _chunk(text: str = "Merhaba dünya bu bir metin") -> Chunk:
    return Chunk(
        chunk_id="d:0",
        doc_id="d",
        kind=ChunkKind.TEXT,
        text=text,
        title="PNT-4417 föy",
        location=SourceLocation(page=1),
    )


REPORT = IngestReport(
    doc_id="d",
    page_count=1,
    page_kinds={},
    ocr_pages=(),
    uncertain_values=0,
    chunks_by_kind={"text": 1},
    warnings=(),
)


@dataclass
class FakeRepository:
    queued: list[StoredDocument] = field(default_factory=list)
    ready: list[tuple[str, Sequence[Chunk], str | None]] = field(default_factory=list)
    failed: list[tuple[str, str]] = field(default_factory=list)
    version_value: str = "1"
    load_calls: int = 0
    ready_error: Exception | None = None
    failed_error: Exception | None = None
    requeues: list[str] = field(default_factory=list)

    async def claim_next(self) -> StoredDocument | None:
        return self.queued.pop(0) if self.queued else None

    async def requeue(self, doc_id: str) -> None:
        self.requeues.append(doc_id)

    async def mark_ready(
        self,
        doc_id: str,
        language: str,
        chunks: Sequence[Chunk],
        report: IngestReport,
        display_pdf: str | None,
    ) -> None:
        if self.ready_error is not None:
            raise self.ready_error
        self.ready.append((doc_id, chunks, display_pdf))

    async def mark_failed(self, doc_id: str, message: str) -> None:
        if self.failed_error is not None:
            raise self.failed_error
        self.failed.append((doc_id, message))

    async def version(self) -> str:
        return self.version_value

    async def load_ready(self) -> tuple[list[DocumentMeta], list[Chunk]]:
        self.load_calls += 1
        return [DocumentMeta(doc_id="d", title="PNT-4417 föy")], [_chunk()]


@dataclass
class FakeIndexer:
    indexed: list[tuple[str, int]] = field(default_factory=list)
    error: Exception | None = None
    removed: list[str] = field(default_factory=list)
    remove_error: Exception | None = None

    async def index(self, doc_id: str, access: Sequence[str], chunks: Sequence[Chunk]) -> None:
        if self.error is not None:
            raise self.error
        self.indexed.append((doc_id, len(chunks)))

    async def remove(self, doc_id: str) -> None:
        if self.remove_error is not None:
            raise self.remove_error
        self.removed.append(doc_id)


def document(tmp_path: Path) -> StoredDocument:
    path = tmp_path / "d" / "original.pdf"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"%PDF-1.7")
    return StoredDocument(
        doc_id="d",
        title="Föy",
        filename="a.pdf",
        status=DocumentStatus.PROCESSING,
        stored_path=str(path),
    )


def make_processor(
    repository: FakeRepository, indexer: FakeIndexer, display: Path | None, error: bool = False
) -> DocumentProcessor:
    def ingest(path: Path, meta: DocumentMeta, work: Path) -> IngestResult:
        if error:
            raise RuntimeError("gizli araç hatası")
        return IngestResult(chunks=(_chunk(),), report=REPORT, display_pdf=display)

    return DocumentProcessor(repository, indexer, ingest)


def test_no_job_means_nothing_was_done() -> None:
    processor = make_processor(FakeRepository(), FakeIndexer(), None)

    assert asyncio.run(processor.process_next()) is False


def test_successful_job_is_indexed_and_marked_ready(tmp_path: Path) -> None:
    repository, indexer = FakeRepository(queued=[document(tmp_path)]), FakeIndexer()
    processor = make_processor(repository, indexer, None)

    assert asyncio.run(processor.process_next()) is True

    assert indexer.indexed == [("d", 1)]
    assert repository.ready[0][0] == "d"
    assert repository.failed == []


def test_display_pdf_is_kept_next_to_the_original(tmp_path: Path) -> None:
    item = document(tmp_path)
    temporary = tmp_path / "gecici.pdf"
    temporary.write_bytes(b"%PDF-display")
    repository = FakeRepository(queued=[item])
    processor = make_processor(repository, FakeIndexer(), temporary)

    asyncio.run(processor.process_next())

    display = repository.ready[0][2]
    assert display is not None
    assert Path(display).parent == Path(item.stored_path).parent
    assert Path(display).read_bytes() == b"%PDF-display"


def test_document_is_not_ready_if_indexing_fails(tmp_path: Path) -> None:
    repository = FakeRepository(queued=[document(tmp_path)])
    processor = make_processor(repository, FakeIndexer(error=RuntimeError("qdrant")), None)

    asyncio.run(processor.process_next())

    assert repository.ready == []
    assert repository.failed[0][0] == "d"


def test_vectors_are_removed_when_the_database_rejects_the_document(tmp_path: Path) -> None:
    repository = FakeRepository(
        queued=[document(tmp_path)], ready_error=ValueError("geçersiz karakter")
    )
    indexer = FakeIndexer()
    processor = make_processor(repository, indexer, None)

    assert asyncio.run(processor.process_next()) is True

    assert indexer.removed == ["d"]
    assert repository.failed[0][0] == "d"


def test_vectors_stay_when_the_document_is_marked_ready(tmp_path: Path) -> None:
    indexer = FakeIndexer()
    processor = make_processor(FakeRepository(queued=[document(tmp_path)]), indexer, None)

    asyncio.run(processor.process_next())

    assert indexer.removed == []


def test_document_is_still_failed_when_vector_cleanup_fails(tmp_path: Path) -> None:
    repository = FakeRepository(queued=[document(tmp_path)], ready_error=ValueError("geçersiz"))
    indexer = FakeIndexer(remove_error=ConnectionError("qdrant"))
    processor = make_processor(repository, indexer, None)

    asyncio.run(processor.process_next())

    assert repository.failed[0][0] == "d"


def test_document_is_requeued_after_a_database_outage(tmp_path: Path) -> None:
    outage = ConnectionError("veritabanı kilitli")
    repository = FakeRepository(
        queued=[document(tmp_path)], ready_error=outage, failed_error=outage
    )
    processor = make_processor(repository, FakeIndexer(), None)

    async def run() -> None:
        with pytest.raises(ConnectionError):
            await processor.process_next()
        assert repository.requeues == []
        await processor.process_next()

    asyncio.run(run())

    assert repository.requeues == ["d"]


def test_requeue_runs_only_once_after_an_outage(tmp_path: Path) -> None:
    outage = ConnectionError("veritabanı kilitli")
    repository = FakeRepository(
        queued=[document(tmp_path)], ready_error=outage, failed_error=outage
    )
    processor = make_processor(repository, FakeIndexer(), None)

    async def run() -> None:
        with pytest.raises(ConnectionError):
            await processor.process_next()
        await processor.process_next()
        await processor.process_next()

    asyncio.run(run())

    assert repository.requeues == ["d"]


def test_failure_message_does_not_expose_internal_errors(tmp_path: Path) -> None:
    repository = FakeRepository(queued=[document(tmp_path)])
    processor = make_processor(repository, FakeIndexer(), None, error=True)

    asyncio.run(processor.process_next())

    assert "gizli" not in repository.failed[0][1]


def test_snapshot_is_reused_until_documents_change() -> None:
    repository = FakeRepository()
    provider = SnapshotProvider(repository)

    async def run() -> None:
        first = await provider.current()
        assert await provider.current() is first
        repository.version_value = "2"
        assert await provider.current() is not first

    asyncio.run(run())

    assert repository.load_calls == 2


def test_snapshot_exposes_catalog_and_identifiers() -> None:
    snapshot = asyncio.run(SnapshotProvider(FakeRepository()).current())

    assert snapshot.catalog.title("d") == "PNT-4417 föy"
    assert snapshot.identifiers.lookup("PNT-4417") == ("d:0",)
