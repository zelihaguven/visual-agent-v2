"""Belge kaydı. Kalıcı depo, belge yükleme ile birlikte A5'te eklenir."""

import re
from collections.abc import Iterable

from visual_agent.domain.document import UNDETECTED_LANGUAGE, DocumentMeta
from visual_agent.verification.text import identifiers_in

_MIN_TITLE_WORDS_FOR_MATCH = 2
_SQUASH_RE = re.compile(r"[\s\-_.]+")
_TURKISH_FOLD = str.maketrans({"I": "ı", "İ": "i"})


def squash(text: str) -> str:
    """Boşluk, tire ve nokta farklarını yok sayan karşılaştırma biçimi."""
    return _SQUASH_RE.sub("", text.translate(_TURKISH_FOLD).lower()).replace("ı", "i")


class DocumentCatalog:
    def __init__(self) -> None:
        self._documents: dict[str, DocumentMeta] = {}

    def add(self, meta: DocumentMeta) -> None:
        self._documents = {**self._documents, meta.doc_id: meta}

    def title(self, doc_id: str) -> str:
        return self._documents[doc_id].title

    def find_title(self, doc_id: str) -> str | None:
        """Silinmiş belgede None."""
        meta = self._documents.get(doc_id)
        return meta.title if meta is not None else None

    def doc_ids(self) -> tuple[str, ...]:
        return tuple(self._documents)

    def language(self, doc_id: str) -> str:
        meta = self._documents.get(doc_id)
        return meta.language if meta is not None else UNDETECTED_LANGUAGE

    def languages(self, doc_ids: Iterable[str]) -> list[str]:
        return list(dict.fromkeys(self._documents[doc_id].language for doc_id in doc_ids))

    def _names(self, meta: DocumentMeta) -> list[str]:
        names = [*identifiers_in(meta.title)]
        if len(meta.title.split()) >= _MIN_TITLE_WORDS_FOR_MATCH:
            names.append(meta.title)
        return names

    def mentioned_in(self, question: str, allowed: Iterable[str]) -> tuple[str, ...]:
        """Soruda başlığı ya da başlığındaki kodu geçen belgeler."""
        target = squash(question)
        return tuple(
            doc_id
            for doc_id in allowed
            if any(squash(name) in target for name in self._names(self._documents[doc_id]))
        )

    def is_document_name(self, identifier: str, doc_ids: Iterable[str]) -> bool:
        """Kod, verilen belgelerden birinin başlığındaki kod mu."""
        return any(
            squash(identifier) == squash(known)
            for doc_id in doc_ids
            for known in identifiers_in(self._documents[doc_id].title)
        )
