"""Belge silme ve yeniden işleme: gerçek SQLite deposu, bellekteki Qdrant ve gerçek işçiyle."""

import asyncio
import dataclasses
import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from qdrant_client import AsyncQdrantClient

from apps.api.documents import delete_document, document_directory, retry_deletions
from apps.api.main import ApiServices, create_app
from apps.worker.indexing import LazyIndexer, SharedEncoders
from apps.worker.jobs import DocumentProcessor
from tests.test_ask_pipeline import FakeClient, FakeRetriever, answer_payload, make_deps
from visual_agent.ask.deps import AskRequest
from visual_agent.ask.orchestrator import answer_question
from visual_agent.catalog.repository import (
    DocumentRepository,
    DocumentStatus,
    StoredDocument,
    open_repository,
)
from visual_agent.catalog.snapshot import SnapshotProvider
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.document import Chunk, ChunkKind, DocumentMeta, SourceLocation
from visual_agent.domain.result import AskOutcome, Failed, NotFound
from visual_agent.ingest.pipeline import IngestReport, IngestResult
from visual_agent.retrieval.qdrant_store import QdrantChunkStore
from visual_agent.settings import Settings

REPORT = IngestReport(
    doc_id="d",
    page_count=1,
    page_kinds={},
    ocr_pages=(),
    uncertain_values=0,
    chunks_by_kind={"text": 1},
    warnings=(),
)


class FakeDense:
    size = 2

    def encode_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]


class FakeSparse:
    def encode_documents(self, texts: Sequence[str]) -> list[dict[int, float]]:
        return [{1: 1.0} for _ in texts]


def _chunk(doc_id: str) -> Chunk:
    return Chunk(
        chunk_id=f"{doc_id}:0",
        doc_id=doc_id,
        kind=ChunkKind.TEXT,
        text="PNT-1162 M beden bel 76 cm",
        title="Föy",
        location=SourceLocation(page=1),
    )


def _repository(tmp_path: Path) -> DocumentRepository:
    repository = open_repository(tmp_path / "katalog.db")
    asyncio.run(repository.migrate())
    return repository


def _stored(storage: Path, doc_id: str, status: DocumentStatus) -> StoredDocument:
    directory = storage / doc_id
    directory.mkdir(parents=True)
    original = directory / "original.pdf"
    original.write_bytes(b"%PDF-1.7")
    (directory / "display.pdf").write_bytes(b"%PDF-1.7")
    return StoredDocument(
        doc_id=doc_id,
        title="Föy",
        filename="foy.pdf",
        status=status,
        stored_path=str(original),
    )


def _ready(repository: DocumentRepository, storage: Path, doc_id: str) -> None:
    async def run() -> None:
        await repository.create_document(_stored(storage, doc_id, DocumentStatus.PROCESSING))
        await repository.mark_ready(doc_id, "tr", [_chunk(doc_id)], REPORT, None)

    asyncio.run(run())


class Vectors:
    def __init__(self, failures: int = 0) -> None:
        self.removed: list[str] = []
        self.failures = failures

    async def remove(self, doc_id: str) -> None:
        if self.failures:
            self.failures -= 1
            raise ConnectionError("qdrant kapalı")
        self.removed.append(doc_id)


def _client(repository: DocumentRepository, storage: Path, vectors: Vectors) -> TestClient:
    async def ask(request: AskRequest) -> AskOutcome:
        return AskOutcome(result=NotFound(reason="yok"), timings={})

    services = ApiServices(
        repository=repository,
        ask=ask,
        storage_directory=storage,
        remove_vectors=vectors.remove,
    )
    return TestClient(create_app(Settings(_env_file=None, web_directory=None), services))


def test_deleting_removes_record_chunks_vectors_and_files(tmp_path: Path) -> None:
    repository, storage, vectors = _repository(tmp_path), tmp_path / "belgeler", Vectors()
    _ready(repository, storage, "d")

    response = _client(repository, storage, vectors).delete("/api/documents/d")

    assert response.status_code == 204
    assert vectors.removed == ["d"]
    assert not (storage / "d").exists()
    assert asyncio.run(repository.list_documents()) == []
    assert asyncio.run(repository.deleting_documents()) == []
    assert asyncio.run(repository.get_chunk("d:0")) is None


def test_deleting_an_unknown_document_is_not_found(tmp_path: Path) -> None:
    client = _client(_repository(tmp_path), tmp_path / "belgeler", Vectors())

    assert client.delete("/api/documents/yok").status_code == 404


def test_failed_vector_cleanup_still_hides_the_document_and_is_retried(tmp_path: Path) -> None:
    repository, storage, vectors = _repository(tmp_path), tmp_path / "belgeler", Vectors(1)
    _ready(repository, storage, "d")

    response = _client(repository, storage, vectors).delete("/api/documents/d")

    assert response.status_code == 204
    assert asyncio.run(repository.list_documents()) == []
    assert asyncio.run(repository.load_ready()) == ([], [])
    assert [d.doc_id for d in asyncio.run(repository.deleting_documents())] == ["d"]

    finished = asyncio.run(retry_deletions(repository, vectors.remove, storage))

    assert finished == 1
    assert vectors.removed == ["d"]
    assert asyncio.run(repository.deleting_documents()) == []


def test_failed_file_cleanup_still_hides_the_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository, storage, vectors = _repository(tmp_path), tmp_path / "belgeler", Vectors()
    _ready(repository, storage, "d")

    def locked(path: Path) -> None:
        raise PermissionError("dosya başka bir süreçte açık")

    monkeypatch.setattr(shutil, "rmtree", locked)

    response = _client(repository, storage, vectors).delete("/api/documents/d")

    assert response.status_code == 204
    assert asyncio.run(repository.list_documents()) == []
    assert [d.doc_id for d in asyncio.run(repository.deleting_documents())] == ["d"]


def test_document_folder_never_leaves_the_storage_directory(tmp_path: Path) -> None:
    assert document_directory(tmp_path, "d") == (tmp_path / "d").resolve()
    for unsafe in ("..", "", "../disari"):
        with pytest.raises(ValueError):
            document_directory(tmp_path, unsafe)


def test_ready_or_failed_document_is_queued_again(tmp_path: Path) -> None:
    repository, storage = _repository(tmp_path), tmp_path / "belgeler"
    _ready(repository, storage, "d")

    response = _client(repository, storage, Vectors()).post("/api/documents/d/reprocess")

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    assert asyncio.run(repository.claim_next()) is not None


def test_reprocessing_a_document_in_progress_is_refused(tmp_path: Path) -> None:
    repository, storage = _repository(tmp_path), tmp_path / "belgeler"
    asyncio.run(repository.create_document(_stored(storage, "d", DocumentStatus.PROCESSING)))
    client = _client(repository, storage, Vectors())

    assert client.post("/api/documents/d/reprocess").status_code == 409
    assert client.post("/api/documents/yok/reprocess").status_code == 404


async def _points(store_client: AsyncQdrantClient) -> int:
    if not await store_client.collection_exists("test"):
        return 0
    return (await store_client.count("test")).count


def _processor(
    repository: Any, store: QdrantChunkStore, indexer: Any | None = None
) -> DocumentProcessor:
    def ingest(path: Path, meta: DocumentMeta, work: Path) -> IngestResult:
        return IngestResult(chunks=(_chunk(meta.doc_id),), report=REPORT, display_pdf=None)

    shared = SharedEncoders(lambda: (FakeDense(), FakeSparse()))
    return DocumentProcessor(repository, indexer or LazyIndexer(store, shared), ingest)


def test_deleted_before_vectors_are_written_leaves_nothing_behind(tmp_path: Path) -> None:
    repository, storage = _repository(tmp_path), tmp_path / "belgeler"

    async def run() -> int:
        qdrant = AsyncQdrantClient(":memory:")
        store = QdrantChunkStore(qdrant, "test")
        real = LazyIndexer(store, SharedEncoders(lambda: (FakeDense(), FakeSparse())))

        class DeletedDuringIngest:
            async def index(
                self, doc_id: str, access: Sequence[str], chunks: Sequence[Chunk]
            ) -> None:
                await delete_document(doc_id, repository, store.delete_document, storage)
                await real.index(doc_id, access, chunks)

            async def remove(self, doc_id: str) -> None:
                await real.remove(doc_id)

        await repository.create_document(_stored(storage, "d", DocumentStatus.QUEUED))
        await _processor(repository, store, DeletedDuringIngest()).process_next()
        return await _points(qdrant)

    assert asyncio.run(run()) == 0
    assert not (storage / "d").exists()
    assert asyncio.run(repository.deleting_documents()) == []
    assert asyncio.run(repository.list_documents()) == []


def test_deleted_after_vectors_are_written_leaves_nothing_behind(tmp_path: Path) -> None:
    repository, storage = _repository(tmp_path), tmp_path / "belgeler"

    async def run() -> int:
        qdrant = AsyncQdrantClient(":memory:")
        store = QdrantChunkStore(qdrant, "test")

        @dataclasses.dataclass
        class DeletedBeforeReady:
            inner: DocumentRepository

            def __getattr__(self, name: str) -> Any:
                return getattr(self.inner, name)

            async def mark_ready(self, doc_id: str, *args: Any) -> bool:
                await delete_document(doc_id, self.inner, store.delete_document, storage)
                return await self.inner.mark_ready(doc_id, *args)

        await repository.create_document(_stored(storage, "d", DocumentStatus.QUEUED))
        await _processor(DeletedBeforeReady(repository), store).process_next()
        return await _points(qdrant)

    assert asyncio.run(run()) == 0
    assert not (storage / "d").exists()
    assert asyncio.run(repository.deleting_documents()) == []


def test_search_catalog_forgets_a_deleted_document(tmp_path: Path) -> None:
    repository, storage = _repository(tmp_path), tmp_path / "belgeler"
    _ready(repository, storage, "d")
    _ready(repository, storage, "e")
    snapshots = SnapshotProvider(repository)

    async def run() -> tuple[tuple[str, ...], tuple[str, ...]]:
        before = (await snapshots.current()).catalog.visible_doc_ids(None)
        await delete_document("d", repository, Vectors().remove, storage)
        after = (await snapshots.current()).catalog.visible_doc_ids(None)
        return before, after

    before, after = asyncio.run(run())

    assert set(before) == {"d", "e"}
    assert after == ("e",)


def test_next_question_after_deleting_the_context_document_does_not_fail(
    tmp_path: Path,
) -> None:
    repository, storage = _repository(tmp_path), tmp_path / "belgeler"
    _ready(repository, storage, "d")
    snapshots = SnapshotProvider(repository)
    asyncio.run(delete_document("d", repository, Vectors().remove, storage))
    snapshot = asyncio.run(snapshots.current())
    retriever = FakeRetriever()
    deps = dataclasses.replace(
        make_deps(FakeClient(answer_payload("Bel 76 cm.")), retriever),
        catalog=snapshot.catalog,
        identifiers=snapshot.identifiers,
    )
    context = ConversationContext(question="PNT-1162 M beden bel kaç?", doc_ids=("d",))

    outcome = asyncio.run(answer_question(AskRequest("Peki kalça?", context=context), deps))

    assert not isinstance(outcome.result, Failed)


def test_queued_document_is_fully_deleted_before_any_vector_exists(tmp_path: Path) -> None:
    repository, storage = _repository(tmp_path), tmp_path / "belgeler"

    async def run() -> list[StoredDocument]:
        store = QdrantChunkStore(AsyncQdrantClient(":memory:"), "henuz-yok")
        await repository.create_document(_stored(storage, "d", DocumentStatus.QUEUED))
        await delete_document("d", repository, store.delete_document, storage)
        return await repository.deleting_documents()

    assert asyncio.run(run()) == []
    assert not (storage / "d").exists()
