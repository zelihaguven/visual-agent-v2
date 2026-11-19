"""Hazır belgelere konu adı verir. Başarısız olursa belge yine hazırdır; konu sonra denenir.

Konu adı belge işlemenin parçası değildir: ayrı modelle, ayrı hata davranışıyla çalışır. Yeni
belge işlendikten hemen sonra adlandırılır; konusu olmayan eski belgeler işçi boşken birer birer
adlandırılır, yeniden işleme gerekmez.
"""

import asyncio
import logging
from collections.abc import Sequence
from typing import Protocol

import httpx

from visual_agent.ask.clients import helper_model
from visual_agent.catalog.repository import StoredDocument
from visual_agent.generation.openrouter import fetch_zdr_index
from visual_agent.generation.topic import (
    TopicMerger,
    TopicNamer,
    make_topic_merger,
    make_topic_namer,
)
from visual_agent.settings import Settings

logger = logging.getLogger(__name__)

_HEADINGS_CHARS = 1500
_NAME_SECONDS = 20.0
_MERGE_SECONDS = 60.0
_MIN_TOPICS_TO_MERGE = 3


class TopicRepository(Protocol):
    async def topics(self) -> list[str]: ...

    async def without_topic(self, skip: Sequence[str] = ()) -> StoredDocument | None: ...

    async def headings(self, doc_id: str, max_chars: int) -> str: ...

    async def set_topic(self, doc_id: str, topic: str) -> None: ...

    async def get_document(self, doc_id: str) -> StoredDocument | None: ...

    async def topic_counts(self) -> list[tuple[str, int]]: ...

    async def rename_topic(self, old: str, new: str) -> None: ...


class TopicAssigner:
    def __init__(
        self, repository: TopicRepository, namer: TopicNamer, merger: TopicMerger | None = None
    ) -> None:
        self._repository = repository
        self._namer = namer
        self._merger = merger
        self._failed: set[str] = set()
        """Bu çalışmada adlandırılamayan belgeler; her turda yeniden sorulmaz."""
        self._merged = False
        """Benzer konular bu çalışmada bir kez birleştirilir (eksik konu kalmayınca)."""

    async def assign(self, document: StoredDocument) -> bool:
        """Belgeye konu verildiyse True. Hata işçiyi durdurmaz."""
        try:
            headings = await self._repository.headings(document.doc_id, _HEADINGS_CHARS)
            existing = await self._repository.topics()
            topic = await asyncio.wait_for(
                self._namer(document.title, headings, existing), _NAME_SECONDS
            )
        except Exception:
            logger.warning("Belgeye konu verilemedi: %s", document.doc_id, exc_info=True)
            topic = None
        if topic is None:
            self._failed.add(document.doc_id)
            return False
        await self._repository.set_topic(document.doc_id, topic)
        return True

    async def assign_ready(self, doc_id: str) -> None:
        """Yeni işlenen belge; konusu varsa (yeniden işleme) dokunulmaz."""
        document = await self._repository.get_document(doc_id)
        if document is not None and document.topic is None:
            await self.assign(document)

    async def assign_next_missing(self) -> bool:
        """Konusu olmayan bir eski belgeyi adlandırır; iş yapıldıysa True."""
        document = await self._repository.without_topic(skip=tuple(self._failed))
        if document is None:
            if not self._merged:
                self._merged = True
                await self.merge_similar()
            return False
        return await self.assign(document)

    async def merge_similar(self) -> int:
        """Aynı türden belgeleri anlatan konu adlarını birleştirir; değişen ad sayısı döner."""
        if self._merger is None:
            return 0
        try:
            counts = await self._repository.topic_counts()
            if len(counts) < _MIN_TOPICS_TO_MERGE:
                return 0
            mapping = await asyncio.wait_for(self._merger(counts), _MERGE_SECONDS)
        except Exception:
            logger.warning("Benzer konular birleştirilemedi", exc_info=True)
            return 0
        for old, new in mapping.items():
            await self._repository.rename_topic(old, new)
        if mapping:
            logger.info("Konular birleştirildi: %s", mapping)
        return len(mapping)


async def open_topic_assigner(
    settings: Settings, repository: TopicRepository
) -> TopicAssigner | None:
    """Yardımcı modelle (ZDR) konu adlandırıcı; anahtar yoksa ya da açılamazsa konu verilmez."""
    key = settings.openrouter_api_key
    api_key = key.get_secret_value().strip() if key is not None else ""
    if not api_key:
        logger.info("Belgelere konu verilmiyor: API anahtarı yok; dosya türüne göre gruplanır.")
        return None
    http = httpx.AsyncClient(timeout=_MERGE_SECONDS)
    try:
        index = await fetch_zdr_index(http, str(settings.openrouter_url).rstrip("/"), api_key)
        model = helper_model(http, settings, api_key, index)
    except Exception:
        logger.warning("Konu adlandırıcı açılamadı; belgeler türe göre gruplanır.", exc_info=True)
        await http.aclose()
        return None
    return TopicAssigner(repository, make_topic_namer(model), make_topic_merger(model))
