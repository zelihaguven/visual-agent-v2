"""Belgelerin ve parçaların SQLite'ta kalıcı kaydı; belge işleme kuyruğu da buradadır.

API ve işçi ayrı süreç olabilir: dosya WAL kipinde açılır, kilitli dosyada beklenir.
"""

import asyncio
import json
import sqlite3
from collections.abc import Callable, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any

from visual_agent.domain.document import Chunk, DocumentMeta, FrozenModel

_BUSY_TIMEOUT_SECONDS = 30.0
_NOW = "strftime('%Y-%m-%dT%H:%M:%f', 'now')"


class DocumentStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETING = "deleting"


class StoredDocument(FrozenModel):
    doc_id: str
    title: str
    filename: str
    status: DocumentStatus
    stored_path: str
    language: str = "tr"
    display_pdf: str | None = None
    report: dict[str, Any] | None = None
    error: str | None = None


_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'tr',
    display_pdf TEXT,
    report TEXT,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT ({_NOW}),
    updated_at TEXT NOT NULL DEFAULT ({_NOW})
);
CREATE INDEX IF NOT EXISTS documents_status_idx ON documents (status, created_at);
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents (doc_id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS chunks_doc_idx ON chunks (doc_id, position);
"""
_COLUMNS = "doc_id, title, filename, status, stored_path, language, display_pdf, report, error"
_VISIBLE = "status != 'deleting'"


def _to_document(row: sqlite3.Row) -> StoredDocument:
    report = row["report"]
    return StoredDocument(
        doc_id=row["doc_id"],
        title=row["title"],
        filename=row["filename"],
        status=DocumentStatus(row["status"]),
        stored_path=row["stored_path"],
        language=row["language"],
        display_pdf=row["display_pdf"],
        report=json.loads(report) if report else None,
        error=row["error"],
    )


def _to_chunk(payload: str) -> Chunk:
    return Chunk.model_validate_json(payload)


def connect(path: Path) -> sqlite3.Connection:
    """Her işlem kendi bağlantısını açar; açık işlemi olan başka süreç varsa beklenir."""
    connection = sqlite3.connect(path, timeout=_BUSY_TIMEOUT_SECONDS, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA synchronous = NORMAL")
    return connection


class SqliteDatabase:
    """Engelleyen SQLite çağrılarını olay döngüsünün dışında çalıştırır."""

    def __init__(self, path: Path) -> None:
        self.path = path

    async def run[T](self, work: Callable[[sqlite3.Connection], T]) -> T:
        return await asyncio.to_thread(self._run, work)

    def _run[T](self, work: Callable[[sqlite3.Connection], T]) -> T:
        connection = connect(self.path)
        try:
            return work(connection)
        finally:
            connection.close()

    async def migrate(self, schema: str) -> None:
        def apply(connection: sqlite3.Connection) -> None:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(schema)

        self.path.parent.mkdir(parents=True, exist_ok=True)
        await self.run(apply)


def _transaction[T](connection: sqlite3.Connection, work: Callable[[sqlite3.Connection], T]) -> T:
    """Yazma kilidi baştan alınır: iki süreç aynı satırı aynı anda değiştiremez."""
    connection.execute("BEGIN IMMEDIATE")
    try:
        result = work(connection)
    except BaseException:
        connection.execute("ROLLBACK")
        raise
    connection.execute("COMMIT")
    return result


class DocumentRepository:
    def __init__(self, database: SqliteDatabase) -> None:
        self._db = database

    async def migrate(self) -> None:
        await self._db.migrate(_SCHEMA)

    async def ping(self) -> None:
        await self._db.run(lambda connection: connection.execute("SELECT 1").fetchone())

    async def create_document(self, document: StoredDocument) -> None:
        await self._db.run(
            lambda connection: connection.execute(
                "INSERT INTO documents"
                " (doc_id, title, filename, status, stored_path, language)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (
                    document.doc_id,
                    document.title,
                    document.filename,
                    document.status.value,
                    document.stored_path,
                    document.language,
                ),
            )
        )

    async def list_documents(self) -> list[StoredDocument]:
        rows = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT {_COLUMNS} FROM documents WHERE {_VISIBLE}"  # noqa: S608
                " ORDER BY created_at DESC, rowid DESC"
            ).fetchall()
        )
        return [_to_document(row) for row in rows]

    async def get_document(self, doc_id: str) -> StoredDocument | None:
        row = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT {_COLUMNS} FROM documents WHERE doc_id = ? AND {_VISIBLE}",  # noqa: S608
                (doc_id,),
            ).fetchone()
        )
        return _to_document(row) if row else None

    async def get_chunk(self, chunk_id: str) -> Chunk | None:
        row = await self._db.run(
            lambda connection: connection.execute(
                "SELECT c.payload FROM chunks c JOIN documents d USING (doc_id)"
                " WHERE c.chunk_id = ? AND d.status != 'deleting'",
                (chunk_id,),
            ).fetchone()
        )
        return _to_chunk(row["payload"]) if row else None

    async def sheet_chunks(self, doc_id: str, sheet: str) -> list[Chunk]:
        rows = await self._db.run(
            lambda connection: connection.execute(
                "SELECT c.payload FROM chunks c JOIN documents d USING (doc_id)"
                " WHERE c.doc_id = ? AND d.status != 'deleting'"
                " AND json_extract(c.payload, '$.location.sheet') = ? ORDER BY c.position",
                (doc_id, sheet),
            ).fetchall()
        )
        return [_to_chunk(row["payload"]) for row in rows]

    async def requeue_interrupted(self) -> None:
        """İşçi işlerken durduysa belge açılışta yeniden kuyruğa girer."""
        await self._db.run(
            lambda connection: connection.execute(
                f"UPDATE documents SET status = 'queued', updated_at = {_NOW}"  # noqa: S608
                " WHERE status = 'processing'"
            )
        )

    async def requeue(self, doc_id: str) -> None:
        """Sonucu yazılamayan tek belgeyi kuyruğa döndürür; diğer işçilerin işine dokunmaz."""
        await self._db.run(
            lambda connection: connection.execute(
                f"UPDATE documents SET status = 'queued', updated_at = {_NOW}"  # noqa: S608
                " WHERE doc_id = ? AND status = 'processing'",
                (doc_id,),
            )
        )

    async def claim_next(self) -> StoredDocument | None:
        """Tek cümlelik güncelleme bölünmez: birden çok işçi aynı belgeyi alamaz."""
        row = await self._db.run(
            lambda connection: connection.execute(
                f"UPDATE documents SET status = 'processing', updated_at = {_NOW}"  # noqa: S608
                " WHERE doc_id = (SELECT doc_id FROM documents WHERE status = 'queued'"
                " ORDER BY created_at, rowid LIMIT 1)"
                f" RETURNING {_COLUMNS}"
            ).fetchone()
        )
        return _to_document(row) if row else None

    async def mark_ready(
        self,
        doc_id: str,
        language: str,
        chunks: Sequence[Chunk],
        report: Any,
        display_pdf: str | None,
    ) -> bool:
        """Yalnız işlenmekte olan belge hazır olur; arada silinen belge için False döner."""
        rows = [
            (chunk.chunk_id, doc_id, position, chunk.model_dump_json())
            for position, chunk in enumerate(chunks)
        ]
        report_json = report.model_dump_json()

        def write(connection: sqlite3.Connection) -> bool:
            updated = connection.execute(
                "UPDATE documents SET status = 'ready', language = ?, report = ?,"  # noqa: S608
                f" display_pdf = ?, error = NULL, updated_at = {_NOW}"
                " WHERE doc_id = ? AND status = 'processing'",
                (language, report_json, display_pdf, doc_id),
            ).rowcount
            if not updated:
                return False
            connection.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
            connection.executemany(
                "INSERT INTO chunks (chunk_id, doc_id, position, payload) VALUES (?, ?, ?, ?)",
                rows,
            )
            return True

        return await self._db.run(lambda connection: _transaction(connection, write))

    async def mark_failed(self, doc_id: str, message: str) -> bool:
        """Arada silinen belgenin durumu ezilmez; o durumda False döner."""
        updated: int = await self._db.run(
            lambda connection: (
                connection.execute(
                    f"UPDATE documents SET status = 'failed', error = ?, updated_at = {_NOW}"  # noqa: S608
                    " WHERE doc_id = ? AND status = 'processing'",
                    (message, doc_id),
                ).rowcount
            )
        )
        return updated > 0

    async def reprocess(self, doc_id: str) -> StoredDocument | None:
        """Hazır ya da işlenemeyen belge kuyruğa döner; sıradaki ya da işlenene dokunulmaz."""
        row = await self._db.run(
            lambda connection: connection.execute(
                f"UPDATE documents SET status = 'queued', error = NULL, updated_at = {_NOW}"  # noqa: S608
                " WHERE doc_id = ? AND status IN ('ready', 'failed')"
                f" RETURNING {_COLUMNS}",
                (doc_id,),
            ).fetchone()
        )
        return _to_document(row) if row else None

    async def mark_deleting(self, doc_id: str) -> StoredDocument | None:
        """Silme ilk adımda kayda yazılır: belge listeden, katalogdan ve aramadan hemen çıkar."""
        row = await self._db.run(
            lambda connection: connection.execute(
                f"UPDATE documents SET status = 'deleting', updated_at = {_NOW}"  # noqa: S608
                f" WHERE doc_id = ? RETURNING {_COLUMNS}",
                (doc_id,),
            ).fetchone()
        )
        return _to_document(row) if row else None

    async def deleting_documents(self) -> list[StoredDocument]:
        """Temizliği yarım kalan silmeler; açılışta yeniden denenir."""
        rows = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT {_COLUMNS} FROM documents WHERE status = 'deleting'"  # noqa: S608
            ).fetchall()
        )
        return [_to_document(row) for row in rows]

    async def purge(self, doc_id: str) -> None:
        """Vektörler ve dosyalar silindikten sonra kayıt parçalarıyla birlikte kalkar."""
        await self._db.run(
            lambda connection: connection.execute(
                "DELETE FROM documents WHERE doc_id = ? AND status = 'deleting'", (doc_id,)
            )
        )

    async def version(self) -> str:
        """Hazır belgeler değiştiğinde değişen kısa damga."""
        row = await self._db.run(
            lambda connection: connection.execute(
                "SELECT count(*) AS total, max(updated_at) AS changed FROM documents"
                " WHERE status = 'ready'"
            ).fetchone()
        )
        return f"{row['total']}:{row['changed']}" if row else ""

    async def load_ready(self) -> tuple[list[DocumentMeta], list[Chunk]]:
        def read(connection: sqlite3.Connection) -> tuple[list[sqlite3.Row], list[sqlite3.Row]]:
            documents = connection.execute(
                "SELECT doc_id, title, language FROM documents WHERE status = 'ready'"
            ).fetchall()
            chunks = connection.execute(
                "SELECT c.payload FROM chunks c JOIN documents d USING (doc_id)"
                " WHERE d.status = 'ready' ORDER BY c.doc_id, c.position"
            ).fetchall()
            return documents, chunks

        documents, chunks = await self._db.run(
            lambda connection: _transaction_read(connection, read)
        )
        return (
            [
                DocumentMeta(
                    doc_id=row["doc_id"],
                    title=row["title"],
                    language=row["language"],
                )
                for row in documents
            ],
            [_to_chunk(row["payload"]) for row in chunks],
        )


def _transaction_read[T](
    connection: sqlite3.Connection, work: Callable[[sqlite3.Connection], T]
) -> T:
    """İki okuma aynı anlık görüntüden yapılır; arada yazılan belge yarım görünmez."""
    connection.execute("BEGIN")
    try:
        return work(connection)
    finally:
        connection.execute("COMMIT")


def open_repository(path: Path) -> DocumentRepository:
    return DocumentRepository(SqliteDatabase(path))
