import asyncio
import sqlite3
from pathlib import Path

import pytest

from visual_agent.catalog.repository import (
    DocumentRepository,
    DocumentStatus,
    StoredDocument,
    connect,
    open_repository,
)
from visual_agent.domain.document import Chunk, ChunkKind, FrozenModel, SourceLocation


class Report(FrozenModel):
    pages: int


def _document(doc_id: str, status: DocumentStatus = DocumentStatus.QUEUED) -> StoredDocument:
    return StoredDocument(
        doc_id=doc_id,
        title=f"Belge {doc_id}",
        filename=f"{doc_id}.pdf",
        status=status,
        stored_path=f"/belgeler/{doc_id}.pdf",
        access=("all", "dikim"),
    )


def _chunk(doc_id: str, index: int, sheet: str | None = None) -> Chunk:
    location = SourceLocation(sheet=sheet, row=index) if sheet else SourceLocation(page=index + 1)
    return Chunk(
        chunk_id=f"{doc_id}:{index}",
        doc_id=doc_id,
        kind=ChunkKind.TABLE_ROW if sheet else ChunkKind.TEXT,
        text=f"Satır {index}",
        title=f"Belge {doc_id}",
        location=location,
    )


def _repository(tmp_path: Path) -> DocumentRepository:
    repository = open_repository(tmp_path / "veri" / "katalog.db")
    asyncio.run(repository.migrate())
    return repository


def test_database_file_is_created_in_wal_mode(tmp_path: Path) -> None:
    _repository(tmp_path)

    connection = connect(tmp_path / "veri" / "katalog.db")
    try:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    finally:
        connection.close()


def test_migrating_twice_keeps_existing_documents(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> list[StoredDocument]:
        await repository.create_document(_document("a"))
        await repository.migrate()
        return await repository.list_documents()

    assert [d.doc_id for d in asyncio.run(run())] == ["a"]


def test_created_document_is_read_back_unchanged(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> StoredDocument | None:
        await repository.create_document(_document("a"))
        return await repository.get_document("a")

    assert asyncio.run(run()) == _document("a")
    assert asyncio.run(repository.get_document("yok")) is None


def test_documents_are_listed_newest_first(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> list[str]:
        for doc_id in ("a", "b", "c"):
            await repository.create_document(_document(doc_id))
        return [d.doc_id for d in await repository.list_documents()]

    assert asyncio.run(run()) == ["c", "b", "a"]


def test_queue_hands_out_oldest_document_once(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> list[str | None]:
        await repository.create_document(_document("a"))
        await repository.create_document(_document("b"))
        claims = [await repository.claim_next() for _ in range(3)]
        return [claim.doc_id if claim else None for claim in claims]

    assert asyncio.run(run()) == ["a", "b", None]
    assert asyncio.run(repository.get_document("a")).status is DocumentStatus.PROCESSING  # type: ignore[union-attr]


def test_two_processes_on_the_same_file_never_claim_the_same_document(tmp_path: Path) -> None:
    first = _repository(tmp_path)
    second = open_repository(tmp_path / "veri" / "katalog.db")

    async def run() -> list[str]:
        for index in range(6):
            await first.create_document(_document(f"d{index}"))
        claims = await asyncio.gather(
            *(repository.claim_next() for repository in (first, second) * 4)
        )
        return [claim.doc_id for claim in claims if claim is not None]

    claimed = asyncio.run(run())
    assert sorted(claimed) == [f"d{index}" for index in range(6)]


def test_requeue_returns_only_the_given_processing_document(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> dict[str, DocumentStatus]:
        await repository.create_document(_document("a"))
        await repository.create_document(_document("b"))
        await repository.claim_next()
        await repository.claim_next()
        await repository.requeue("a")
        await repository.requeue("c")
        return {d.doc_id: d.status for d in await repository.list_documents()}

    assert asyncio.run(run()) == {"a": DocumentStatus.QUEUED, "b": DocumentStatus.PROCESSING}


def test_interrupted_documents_return_to_the_queue_on_start(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> list[DocumentStatus]:
        await repository.create_document(_document("a"))
        await repository.create_document(_document("b", DocumentStatus.FAILED))
        await repository.claim_next()
        await repository.requeue_interrupted()
        return [d.status for d in await repository.list_documents()]

    assert asyncio.run(run()) == [DocumentStatus.FAILED, DocumentStatus.QUEUED]


def test_ready_document_keeps_chunks_report_and_language(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    chunks = [_chunk("a", 0), _chunk("a", 1, sheet="Ölçüler"), _chunk("a", 2, sheet="Ölçüler")]

    async def run() -> None:
        await repository.create_document(_document("a"))
        await repository.claim_next()
        await repository.mark_ready("a", "en", chunks, Report(pages=3), "/belgeler/a.pdf")

    asyncio.run(run())
    stored = asyncio.run(repository.get_document("a"))
    assert stored is not None
    assert stored.status is DocumentStatus.READY
    assert stored.language == "en"
    assert stored.report == {"pages": 3}
    assert stored.display_pdf == "/belgeler/a.pdf"
    assert asyncio.run(repository.get_chunk("a:1")) == chunks[1]
    assert asyncio.run(repository.get_chunk("a:9")) is None
    assert asyncio.run(repository.sheet_chunks("a", "Ölçüler")) == chunks[1:]


def test_processing_again_replaces_previous_chunks(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> list[Chunk]:
        await repository.create_document(_document("a", DocumentStatus.PROCESSING))
        await repository.mark_ready(
            "a", "tr", [_chunk("a", 0), _chunk("a", 1)], Report(pages=1), None
        )
        await repository.reprocess("a")
        await repository.claim_next()
        await repository.mark_ready("a", "tr", [_chunk("a", 5)], Report(pages=1), None)
        return list((await repository.load_ready())[1])

    assert [chunk.chunk_id for chunk in asyncio.run(run())] == ["a:5"]


def test_failed_write_leaves_neither_chunks_nor_ready_status(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    duplicate = [_chunk("a", 0), _chunk("a", 0)]

    async def run() -> None:
        await repository.create_document(_document("a"))
        await repository.claim_next()
        await repository.mark_ready("a", "tr", duplicate, Report(pages=1), None)

    with pytest.raises(sqlite3.IntegrityError):
        asyncio.run(run())
    stored = asyncio.run(repository.get_document("a"))
    assert stored is not None and stored.status is DocumentStatus.PROCESSING
    assert asyncio.run(repository.get_chunk("a:0")) is None


def test_failure_message_is_recorded(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> StoredDocument | None:
        await repository.create_document(_document("a", DocumentStatus.PROCESSING))
        await repository.mark_failed("a", "Belge işlenemedi.")
        return await repository.get_document("a")

    stored = asyncio.run(run())
    assert stored is not None
    assert (stored.status, stored.error) == (DocumentStatus.FAILED, "Belge işlenemedi.")


def test_only_ready_documents_reach_the_search_catalog(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> tuple[list[str], list[str]]:
        await repository.create_document(_document("a", DocumentStatus.PROCESSING))
        await repository.create_document(_document("b", DocumentStatus.PROCESSING))
        await repository.mark_ready("a", "tr", [_chunk("a", 0)], Report(pages=1), None)
        await repository.mark_failed("b", "bozuk")
        documents, chunks = await repository.load_ready()
        return [d.doc_id for d in documents], [c.chunk_id for c in chunks]

    assert asyncio.run(run()) == (["a"], ["a:0"])


def test_ready_document_access_groups_reach_the_catalog(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> tuple[str, ...]:
        await repository.create_document(_document("a", DocumentStatus.PROCESSING))
        await repository.mark_ready("a", "tr", [], Report(pages=0), None)
        return (await repository.load_ready())[0][0].access

    assert asyncio.run(run()) == ("all", "dikim")


def test_version_changes_only_when_ready_documents_change(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> list[str]:
        versions = [await repository.version()]
        await repository.create_document(_document("a", DocumentStatus.PROCESSING))
        versions.append(await repository.version())
        await repository.mark_ready("a", "tr", [_chunk("a", 0)], Report(pages=1), None)
        versions.append(await repository.version())
        return versions

    empty, queued, ready = asyncio.run(run())
    assert empty == queued
    assert ready != queued


def test_ping_answers_when_the_file_is_reachable(tmp_path: Path) -> None:
    asyncio.run(_repository(tmp_path).ping())


def _ready_document(repository: DocumentRepository, doc_id: str) -> None:
    async def run() -> None:
        await repository.create_document(_document(doc_id, DocumentStatus.PROCESSING))
        await repository.mark_ready(
            doc_id, "tr", [_chunk(doc_id, 0, sheet="Ölçüler")], Report(pages=1), None
        )

    asyncio.run(run())


def test_document_being_deleted_disappears_everywhere_at_once(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    _ready_document(repository, "a")
    _ready_document(repository, "b")

    deleting = asyncio.run(repository.mark_deleting("a"))

    assert deleting is not None and deleting.doc_id == "a"
    assert [d.doc_id for d in asyncio.run(repository.list_documents())] == ["b"]
    assert asyncio.run(repository.get_document("a")) is None
    assert asyncio.run(repository.get_chunk("a:0")) is None
    assert asyncio.run(repository.sheet_chunks("a", "Ölçüler")) == []
    documents, chunks = asyncio.run(repository.load_ready())
    assert [d.doc_id for d in documents] == ["b"] and [c.doc_id for c in chunks] == ["b"]
    assert [d.doc_id for d in asyncio.run(repository.deleting_documents())] == ["a"]


def test_deleting_an_unknown_document_finds_nothing(tmp_path: Path) -> None:
    assert asyncio.run(_repository(tmp_path).mark_deleting("yok")) is None


def test_purge_removes_the_record_and_its_chunks(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    _ready_document(repository, "a")

    async def run() -> int:
        await repository.mark_deleting("a")
        await repository.purge("a")
        return len(await repository.deleting_documents())

    assert asyncio.run(run()) == 0
    connection = connect(tmp_path / "veri" / "katalog.db")
    try:
        assert connection.execute("SELECT count(*) FROM chunks").fetchone()[0] == 0
        assert connection.execute("SELECT count(*) FROM documents").fetchone()[0] == 0
    finally:
        connection.close()


def test_purge_never_removes_a_document_that_is_not_being_deleted(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    _ready_document(repository, "a")

    asyncio.run(repository.purge("a"))

    assert asyncio.run(repository.get_document("a")) is not None


def test_document_deleted_while_processing_is_never_marked_ready(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> bool:
        await repository.create_document(_document("a"))
        await repository.claim_next()
        await repository.mark_deleting("a")
        return await repository.mark_ready("a", "tr", [_chunk("a", 0)], Report(pages=1), None)

    assert asyncio.run(run()) is False
    assert [d.status for d in asyncio.run(repository.deleting_documents())] == [
        DocumentStatus.DELETING
    ]
    connection = connect(tmp_path / "veri" / "katalog.db")
    try:
        assert connection.execute("SELECT count(*) FROM chunks").fetchone()[0] == 0
    finally:
        connection.close()


def test_purged_document_cannot_come_back_from_the_worker(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> bool:
        await repository.create_document(_document("a"))
        await repository.claim_next()
        await repository.mark_deleting("a")
        await repository.purge("a")
        await repository.mark_failed("a", "geç kalan hata")
        return await repository.mark_ready("a", "tr", [_chunk("a", 0)], Report(pages=1), None)

    assert asyncio.run(run()) is False
    assert asyncio.run(repository.list_documents()) == []


def test_failure_does_not_overwrite_a_deletion(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> list[StoredDocument]:
        await repository.create_document(_document("a"))
        await repository.claim_next()
        await repository.mark_deleting("a")
        written = await repository.mark_failed("a", "geç kalan hata")
        assert written is False
        return await repository.deleting_documents()

    assert [d.doc_id for d in asyncio.run(run())] == ["a"]


@pytest.mark.parametrize("status", [DocumentStatus.READY, DocumentStatus.FAILED])
def test_ready_or_failed_document_can_be_processed_again(
    tmp_path: Path, status: DocumentStatus
) -> None:
    repository = _repository(tmp_path)

    async def run() -> StoredDocument | None:
        failed = _document("a", status).model_copy(update={"error": "eski hata"})
        await repository.create_document(failed)
        return await repository.reprocess("a")

    again = asyncio.run(run())

    assert again is not None
    assert (again.status, again.error) == (DocumentStatus.QUEUED, None)
    assert asyncio.run(repository.claim_next()) is not None


@pytest.mark.parametrize(
    "status", [DocumentStatus.QUEUED, DocumentStatus.PROCESSING, DocumentStatus.DELETING]
)
def test_queued_processing_or_deleted_document_is_not_reprocessed(
    tmp_path: Path, status: DocumentStatus
) -> None:
    repository = _repository(tmp_path)

    async def run() -> StoredDocument | None:
        await repository.create_document(_document("a", status))
        return await repository.reprocess("a")

    assert asyncio.run(run()) is None
    assert asyncio.run(repository.reprocess("yok")) is None


def test_failure_is_written_for_a_document_being_processed(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> bool:
        await repository.create_document(_document("a", DocumentStatus.PROCESSING))
        return await repository.mark_failed("a", "bozuk")

    assert asyncio.run(run()) is True
