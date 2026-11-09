"""Belgelerin ve parçaların Postgres'te kalıcı kaydı; belge işleme kuyruğu da buradadır."""

import json
from collections.abc import Sequence
from enum import StrEnum
from typing import Any

import asyncpg

from visual_agent.domain.document import Chunk, DocumentMeta, FrozenModel


class DocumentStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class StoredDocument(FrozenModel):
    doc_id: str
    title: str
    filename: str
    status: DocumentStatus
    stored_path: str
    language: str = "tr"
    access: tuple[str, ...] = ("all",)
    display_pdf: str | None = None
    report: dict[str, Any] | None = None
    error: str | None = None


_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'tr',
    access TEXT[] NOT NULL DEFAULT ARRAY['all'],
    display_pdf TEXT,
    report JSONB,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS documents_status_idx ON documents (status, created_at);
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents (doc_id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS chunks_doc_idx ON chunks (doc_id, position);
"""
_COLUMNS = (
    "doc_id, title, filename, status, stored_path, language, access, display_pdf, report, error"
)


def _to_document(row: asyncpg.Record) -> StoredDocument:
    report = row["report"]
    return StoredDocument(
        doc_id=row["doc_id"],
        title=row["title"],
        filename=row["filename"],
        status=DocumentStatus(row["status"]),
        stored_path=row["stored_path"],
        language=row["language"],
        access=tuple(row["access"]),
        display_pdf=row["display_pdf"],
        report=json.loads(report) if report else None,
        error=row["error"],
    )


def _to_chunk(payload: str) -> Chunk:
    return Chunk.model_validate_json(payload)


class DocumentRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def migrate(self) -> None:
        await self._pool.execute(_SCHEMA)

    async def create_document(self, document: StoredDocument) -> None:
        await self._pool.execute(
            "INSERT INTO documents (doc_id, title, filename, status, stored_path, language, access)"
            " VALUES ($1, $2, $3, $4, $5, $6, $7)",
            document.doc_id,
            document.title,
            document.filename,
            document.status.value,
            document.stored_path,
            document.language,
            list(document.access),
        )

    async def list_documents(self) -> list[StoredDocument]:
        rows = await self._pool.fetch(
            f"SELECT {_COLUMNS} FROM documents ORDER BY created_at DESC"  # noqa: S608
        )
        return [_to_document(row) for row in rows]

    async def get_document(self, doc_id: str) -> StoredDocument | None:
        row = await self._pool.fetchrow(
            f"SELECT {_COLUMNS} FROM documents WHERE doc_id = $1",  # noqa: S608
            doc_id,
        )
        return _to_document(row) if row else None

    async def get_chunk(self, chunk_id: str) -> Chunk | None:
        payload = await self._pool.fetchval(
            "SELECT payload::text FROM chunks WHERE chunk_id = $1", chunk_id
        )
        return _to_chunk(payload) if payload else None

    async def sheet_chunks(self, doc_id: str, sheet: str) -> list[Chunk]:
        rows = await self._pool.fetch(
            "SELECT payload::text AS payload FROM chunks WHERE doc_id = $1"
            " AND payload->'location'->>'sheet' = $2 ORDER BY position",
            doc_id,
            sheet,
        )
        return [_to_chunk(row["payload"]) for row in rows]

    async def requeue_interrupted(self) -> None:
        """İşçi işlerken durduysa belge açılışta yeniden kuyruğa girer."""
        await self._pool.execute(
            "UPDATE documents SET status = 'queued', updated_at = now() WHERE status = 'processing'"
        )

    async def claim_next(self) -> StoredDocument | None:
        """Birden çok işçi aynı belgeyi alamaz."""
        row = await self._pool.fetchrow(
            "UPDATE documents SET status = 'processing', updated_at = now() WHERE doc_id = ("  # noqa: S608
            " SELECT doc_id FROM documents WHERE status = 'queued'"
            " ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1"
            f") RETURNING {_COLUMNS}"
        )
        return _to_document(row) if row else None

    async def mark_ready(
        self,
        doc_id: str,
        language: str,
        chunks: Sequence[Chunk],
        report: Any,
        display_pdf: str | None,
    ) -> None:
        async with self._pool.acquire() as connection, connection.transaction():
            await connection.execute("DELETE FROM chunks WHERE doc_id = $1", doc_id)
            await connection.executemany(
                "INSERT INTO chunks (chunk_id, doc_id, position, payload)"
                " VALUES ($1, $2, $3, $4::jsonb)",
                [
                    (chunk.chunk_id, doc_id, position, chunk.model_dump_json())
                    for position, chunk in enumerate(chunks)
                ],
            )
            await connection.execute(
                "UPDATE documents SET status = 'ready', language = $2, report = $3::jsonb,"
                " display_pdf = $4, error = NULL, updated_at = now() WHERE doc_id = $1",
                doc_id,
                language,
                report.model_dump_json(),
                display_pdf,
            )

    async def mark_failed(self, doc_id: str, message: str) -> None:
        await self._pool.execute(
            "UPDATE documents SET status = 'failed', error = $2, updated_at = now()"
            " WHERE doc_id = $1",
            doc_id,
            message,
        )

    async def version(self) -> str:
        """Hazır belgeler değiştiğinde değişen kısa damga."""
        row = await self._pool.fetchrow(
            "SELECT count(*) AS total, max(updated_at) AS changed FROM documents"
            " WHERE status = 'ready'"
        )
        return f"{row['total']}:{row['changed']}" if row else ""

    async def load_ready(self) -> tuple[list[DocumentMeta], list[Chunk]]:
        documents = await self._pool.fetch(
            "SELECT doc_id, title, language, access FROM documents WHERE status = 'ready'"
        )
        chunks = await self._pool.fetch(
            "SELECT c.payload::text AS payload FROM chunks c JOIN documents d USING (doc_id)"
            " WHERE d.status = 'ready' ORDER BY c.doc_id, c.position"
        )
        return (
            [
                DocumentMeta(
                    doc_id=row["doc_id"],
                    title=row["title"],
                    language=row["language"],
                    access=tuple(row["access"]),
                )
                for row in documents
            ],
            [_to_chunk(row["payload"]) for row in chunks],
        )
