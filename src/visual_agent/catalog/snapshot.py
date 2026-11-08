"""Belge kaydının okuma görüntüsü; belgeler değişince yenilenir."""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from visual_agent.catalog.identifiers import IdentifierIndex, build_identifier_index
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.domain.document import Chunk, DocumentMeta


class SnapshotSource(Protocol):
    async def version(self) -> str: ...

    async def load_ready(self) -> tuple[Sequence[DocumentMeta], Sequence[Chunk]]: ...


@dataclass(frozen=True)
class CatalogSnapshot:
    version: str
    catalog: DocumentCatalog
    identifiers: IdentifierIndex


class SnapshotProvider:
    def __init__(self, source: SnapshotSource) -> None:
        self._source = source
        self._current: CatalogSnapshot | None = None
        self._lock = asyncio.Lock()

    async def current(self) -> CatalogSnapshot:
        version = await self._source.version()
        if self._current is not None and self._current.version == version:
            return self._current
        async with self._lock:
            if self._current is None or self._current.version != version:
                self._current = await self._load(version)
            return self._current

    async def _load(self, version: str) -> CatalogSnapshot:
        documents, chunks = await self._source.load_ready()
        catalog = DocumentCatalog()
        for document in documents:
            catalog.add(document)
        return CatalogSnapshot(version, catalog, build_identifier_index(chunks))
