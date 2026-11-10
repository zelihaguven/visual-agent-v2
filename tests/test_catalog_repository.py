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
        await repository.create_document(_document("a"))
        await repository.mark_ready(
            "a", "tr", [_chunk("a", 0), _chunk("a", 1)], Report(pages=1), None
        )
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
        await repository.create_document(_document("a"))
        await repository.mark_failed("a", "Belge işlenemedi.")
        return await repository.get_document("a")

    stored = asyncio.run(run())
    assert stored is not None
    assert (stored.status, stored.error) == (DocumentStatus.FAILED, "Belge işlenemedi.")


def test_only_ready_documents_reach_the_search_catalog(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> tuple[list[str], list[str]]:
        await repository.create_document(_document("a"))
        await repository.create_document(_document("b"))
        await repository.mark_ready("a", "tr", [_chunk("a", 0)], Report(pages=1), None)
        await repository.mark_ready("b", "tr", [_chunk("b", 0)], Report(pages=1), None)
        await repository.mark_failed("b", "bozuk")
        documents, chunks = await repository.load_ready()
        return [d.doc_id for d in documents], [c.chunk_id for c in chunks]

    assert asyncio.run(run()) == (["a"], ["a:0"])


def test_ready_document_access_groups_reach_the_catalog(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> tuple[str, ...]:
        await repository.create_document(_document("a"))
        await repository.mark_ready("a", "tr", [], Report(pages=0), None)
        return (await repository.load_ready())[0][0].access

    assert asyncio.run(run()) == ("all", "dikim")


def test_version_changes_only_when_ready_documents_change(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    async def run() -> list[str]:
        versions = [await repository.version()]
        await repository.create_document(_document("a"))
        versions.append(await repository.version())
        await repository.mark_ready("a", "tr", [_chunk("a", 0)], Report(pages=1), None)
        versions.append(await repository.version())
        return versions

    empty, queued, ready = asyncio.run(run())
    assert empty == queued
    assert ready != queued


def test_ping_answers_when_the_file_is_reachable(tmp_path: Path) -> None:
    asyncio.run(_repository(tmp_path).ping())
