"""Kullanıcıya gösterilen belge adı: ham dosya adı yerine okunur başlık.

Yalnız gösterim içindir; arama, istem ve doğrulama belgenin kayıtlı başlığını kullanmaya
devam eder. Kural biçim düzeyindedir: Markdown belgesi birinci düzey başlıkla başlıyorsa
ve kullanıcı yüklerken başlık vermediyse o başlık gösterilir; diğer belgelerde kayıtlı
başlık kalır.
"""

import asyncio
import re
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from visual_agent.catalog.repository import StoredDocument

MARKDOWN_SUFFIX = ".md"
_HEAD_BYTES = 4096
_MAX_NAME_CHARS = 200
_HEADING_RE = re.compile(r"^#[ \t]+(?P<text>.+?)[ \t]*#*[ \t]*$")
_EMPHASIS_RE = re.compile(r"(\*\*|__|`)")

FindDocument = Callable[[str], Awaitable[StoredDocument | None]]
Event = dict[str, Any]


def markdown_title(head: str) -> str | None:
    """Metnin ilk dolu satırı birinci düzey başlıksa başlığın düz metni."""
    for line in head.lstrip("﻿").splitlines():
        if line.strip():
            match = _HEADING_RE.match(line.strip())
            if match is None:
                return None
            text = _EMPHASIS_RE.sub("", match.group("text")).strip()
            return text[:_MAX_NAME_CHARS] or None
    return None


def _read_head(path: Path) -> str:
    try:
        with path.open("rb") as stream:
            return stream.read(_HEAD_BYTES).decode("utf-8", errors="ignore")
    except OSError:
        return ""


def _readable(document: StoredDocument, head: str) -> str:
    if document.title != Path(document.filename).stem:
        return document.title
    return markdown_title(head) or document.title


class DocumentNames:
    """Belge adlarını bir kez okur ve saklar; belge bulunamazsa gelen ad kalır."""

    def __init__(self) -> None:
        self._names: dict[str, str] = {}

    async def name(self, doc_id: str, fallback: str, find: FindDocument) -> str:
        if doc_id in self._names:
            return self._names[doc_id]
        document = await find(doc_id)
        if document is None:
            return fallback
        path = Path(document.stored_path)
        head = (
            await asyncio.to_thread(_read_head, path)
            if path.suffix.lower() == MARKDOWN_SUFFIX
            else ""
        )
        self._names[doc_id] = _readable(document, head)
        return self._names[doc_id]

    async def _citations(self, citations: list[dict[str, Any]], find: FindDocument) -> None:
        for citation in citations:
            citation["title"] = await self.name(citation["doc_id"], citation["title"], find)

    async def _result(self, result: dict[str, Any], find: FindDocument) -> None:
        for item in result.get("items", []):
            await self._citations(item.get("citations", []), find)
        await self._citations(result.get("citations", []), find)
        for option in [*result.get("options", []), *result.get("suggestions", [])]:
            option["label"] = await self.name(option["doc_id"], option["label"], find)
        if result.get("kind") == "inventory":
            for document in result.get("documents", []):
                document["title"] = await self.name(document["doc_id"], document["title"], find)

    async def rename(self, event: Event, find: FindDocument) -> Event:
        """Olaydaki belge adlarını okunur adla değiştirir; diğer alanlara dokunmaz."""
        if event.get("type") == "sources":
            await self._citations(event["sources"], find)
        elif event.get("type") == "done":
            await self._result(event["result"], find)
            context = event.get("context")
            if context is not None:
                # İstemcinin gönderdiği bağlam geri dönebilir; onda ad eksik olabilir.
                titles = [*context["titles"], *[""] * len(context["doc_ids"])]
                context["titles"] = [
                    await self.name(doc_id, title, find)
                    for doc_id, title in zip(context["doc_ids"], titles, strict=False)
                ]
        return event
