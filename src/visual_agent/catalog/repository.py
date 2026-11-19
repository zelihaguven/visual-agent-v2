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
    WAITING_READER = "waiting_reader"
    """Taranmış sayfaların okuyucusu yok; belge indekslenmedi, okuyucu gelince yeniden işlenir."""
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
    topic: str | None = None
    """Arayüzün belgeyi gruplamak için kullandığı konu adı; henüz verilmediyse None."""


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
_COLUMNS = (
    "doc_id, title, filename, status, stored_path, language, display_pdf, report, error, topic"
)
_ADDED_COLUMNS = {"topic": "TEXT"}
"""Sonradan eklenen sütunlar: var olan veritabanına açılışta eklenir."""
_VISIBLE = "status != 'deleting'"


def stored_relative(path: str, doc_id: str) -> str:
    """Belge dosyasının kayıttaki yolu: belge klasörüne göre, düz eğik çizgiyle
    ("<doc_id>/original.pdf"). Windows'ta yazılmış "data\\documents\\<doc_id>\\..." ve mutlak
    yollar da böyle olur: yol belge kimliğinden itibaren alınır. Veri bilgisayarlar arasında
    taşınabilir (ters eğik çizgi Mac'te ayırıcı değildir)."""
    parts = [part for part in path.replace("\\", "/").split("/") if part]
    return "/".join(parts[parts.index(doc_id) :]) if doc_id in parts else path


def _relocate_paths(connection: sqlite3.Connection) -> None:
    """Eski kayıtların yolları bir kez dönüştürülür; dönüşmüş kayıt değişmez."""
    rows = connection.execute("SELECT doc_id, stored_path, display_pdf FROM documents").fetchall()
    for row in rows:
        stored = stored_relative(row["stored_path"], row["doc_id"])
        display = row["display_pdf"] and stored_relative(row["display_pdf"], row["doc_id"])
        if (stored, display) != (row["stored_path"], row["display_pdf"]):
            connection.execute(
                "UPDATE documents SET stored_path = ?, display_pdf = ? WHERE doc_id = ?",
                (stored, display, row["doc_id"]),
            )


def _add_missing_columns(connection: sqlite3.Connection) -> None:
    present = {row["name"] for row in connection.execute("PRAGMA table_info(documents)")}
    for name, kind in _ADDED_COLUMNS.items():
        if name not in present:
            connection.execute(f"ALTER TABLE documents ADD COLUMN {name} {kind}")


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
    """storage: belge klasörü. Verilirse dosya yolları kayıtta ona göre (düz eğik çizgiyle)
    tutulur ve okunurken onunla birleştirilir; verilmezse yollar olduğu gibi kalır (testler)."""

    def __init__(self, database: SqliteDatabase, storage: Path | None = None) -> None:
        self._db = database
        self._storage = storage

    async def migrate(self) -> None:
        await self._db.migrate(_SCHEMA)
        await self._db.run(_add_missing_columns)
        if self._storage is not None:
            await self._db.run(lambda connection: _transaction(connection, _relocate_paths))

    def _stored(self, path: str | None, doc_id: str) -> str | None:
        if path is None or self._storage is None:
            return path
        return stored_relative(path, doc_id)

    def _resolved(self, path: str | None) -> str | None:
        if path is None or self._storage is None:
            return path
        return str(self._storage / path)

    def _document(self, row: sqlite3.Row) -> StoredDocument:
        report = row["report"]
        return StoredDocument(
            doc_id=row["doc_id"],
            title=row["title"],
            filename=row["filename"],
            status=DocumentStatus(row["status"]),
            stored_path=self._resolved(row["stored_path"]) or "",
            language=row["language"],
            display_pdf=self._resolved(row["display_pdf"]),
            report=json.loads(report) if report else None,
            error=row["error"],
            topic=row["topic"],
        )

    async def topics(self) -> list[str]:
        """Verilmiş konular, çok kullanılandan aza."""
        rows = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT topic FROM documents WHERE topic IS NOT NULL AND {_VISIBLE}"  # noqa: S608
                " GROUP BY topic ORDER BY COUNT(*) DESC, topic"
            ).fetchall()
        )
        return [row["topic"] for row in rows]

    async def without_topic(self, skip: Sequence[str] = ()) -> StoredDocument | None:
        """Konusu olmayan en eski hazır belge; skip'tekiler atlanır."""
        marks = ", ".join("?" * len(skip))
        excluded = f" AND doc_id NOT IN ({marks})" if skip else ""
        row = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT {_COLUMNS} FROM documents WHERE status = 'ready'"  # noqa: S608
                f" AND topic IS NULL{excluded} ORDER BY created_at, rowid LIMIT 1",
                tuple(skip),
            ).fetchone()
        )
        return self._document(row) if row else None

    async def headings(self, doc_id: str, max_chars: int) -> str:
        """Belgenin bölüm başlıkları, belgedeki sırasıyla (konu adı için). Buluta yalnız bunlar
        gider, parçaların metni gitmez (karar kaydı: konu adlandırıcı)."""
        rows = await self._db.run(
            lambda connection: connection.execute(
                "SELECT payload FROM chunks WHERE doc_id = ? ORDER BY position", (doc_id,)
            ).fetchall()
        )
        sections = dict.fromkeys(
            section for row in rows if (section := _to_chunk(row["payload"]).section)
        )
        return "\n".join(sections)[:max_chars]

    async def topic_counts(self) -> list[tuple[str, int]]:
        rows = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT topic, COUNT(*) AS n FROM documents WHERE topic IS NOT NULL"  # noqa: S608
                f" AND {_VISIBLE} GROUP BY topic ORDER BY n DESC, topic"
            ).fetchall()
        )
        return [(row["topic"], row["n"]) for row in rows]

    async def rename_topic(self, old: str, new: str) -> None:
        await self._db.run(
            lambda connection: connection.execute(
                "UPDATE documents SET topic = ? WHERE topic = ?", (new, old)
            )
        )

    async def set_topic(self, doc_id: str, topic: str) -> None:
        await self._db.run(
            lambda connection: connection.execute(
                "UPDATE documents SET topic = ? WHERE doc_id = ?", (topic, doc_id)
            )
        )

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
                    self._stored(document.stored_path, document.doc_id),
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
        return [self._document(row) for row in rows]

    async def get_document(self, doc_id: str) -> StoredDocument | None:
        row = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT {_COLUMNS} FROM documents WHERE doc_id = ? AND {_VISIBLE}",  # noqa: S608
                (doc_id,),
            ).fetchone()
        )
        return self._document(row) if row else None

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
        return self._document(row) if row else None

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
                (language, report_json, self._stored(display_pdf, doc_id), doc_id),
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

    async def mark_failed(self, doc_id: str, message: str, waiting: bool = False) -> bool:
        """Arada silinen belgenin durumu ezilmez; o durumda False döner. waiting: belge bozuk
        değil, taranmış sayfaların okuyucusunu bekliyor."""
        status = DocumentStatus.WAITING_READER if waiting else DocumentStatus.FAILED
        updated: int = await self._db.run(
            lambda connection: (
                connection.execute(
                    f"UPDATE documents SET status = ?, error = ?, updated_at = {_NOW}"  # noqa: S608
                    " WHERE doc_id = ? AND status = 'processing'",
                    (status.value, message, doc_id),
                ).rowcount
            )
        )
        return updated > 0

    async def reprocess(self, doc_id: str) -> StoredDocument | None:
        """Hazır ya da işlenemeyen belge kuyruğa döner; sıradaki ya da işlenene dokunulmaz."""
        row = await self._db.run(
            lambda connection: connection.execute(
                f"UPDATE documents SET status = 'queued', error = NULL, updated_at = {_NOW}"  # noqa: S608
                " WHERE doc_id = ? AND status IN ('ready', 'failed', 'waiting_reader')"
                f" RETURNING {_COLUMNS}",
                (doc_id,),
            ).fetchone()
        )
        return self._document(row) if row else None

    async def mark_deleting(self, doc_id: str) -> StoredDocument | None:
        """Silme ilk adımda kayda yazılır: belge listeden, katalogdan ve aramadan hemen çıkar."""
        row = await self._db.run(
            lambda connection: connection.execute(
                f"UPDATE documents SET status = 'deleting', updated_at = {_NOW}"  # noqa: S608
                f" WHERE doc_id = ? RETURNING {_COLUMNS}",
                (doc_id,),
            ).fetchone()
        )
        return self._document(row) if row else None

    async def deleting_documents(self) -> list[StoredDocument]:
        """Temizliği yarım kalan silmeler; açılışta yeniden denenir."""
        rows = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT {_COLUMNS} FROM documents WHERE status = 'deleting'"  # noqa: S608
            ).fetchall()
        )
        return [self._document(row) for row in rows]

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


def open_repository(path: Path, storage: Path | None = None) -> DocumentRepository:
    return DocumentRepository(SqliteDatabase(path), storage)
