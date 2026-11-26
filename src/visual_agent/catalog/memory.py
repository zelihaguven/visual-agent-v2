"""Bellekteki belge kataloğu: hazır belgelerin adı, dili ve kodları (SQLite kaydından kurulur)."""

import re
from collections.abc import Iterable

from visual_agent.domain.document import UNDETECTED_LANGUAGE, DocumentMeta
from visual_agent.verification.text import identifiers_in, model_numbers, turkish_lower

_MIN_TITLE_WORDS_FOR_MATCH = 2
_SQUASH_RE = re.compile(r"[\s\-_.]+")


def squash(text: str) -> str:
    """Boşluk, tire ve nokta farklarını yok sayan karşılaştırma biçimi."""
    return _SQUASH_RE.sub("", turkish_lower(text, merge_dotless_i=True))


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
        """Soruda başlığı, başlığındaki kodu ya da başlığındaki sayısal model numarası (harfsiz,
        en az 5 haneli; ör. dosya adındaki "6013448") birebir geçen belgeler."""
        target = squash(question)
        numbers = model_numbers(question)
        return tuple(
            doc_id
            for doc_id in allowed
            if any(squash(name) in target for name in self._names(self._documents[doc_id]))
            or numbers & model_numbers(self._documents[doc_id].title)
        )

    def without_names(self, text: str, doc_ids: Iterable[str]) -> str:
        """Belgelerin başlığındaki kodlar ve sayısal model numaraları metinden çıkar (kesmeli
        ekiyle: "6013448'in"). Belgeyi seçmişlerdir; belge içinde ayırt edici değillerdir ve aramayı
        onları metninde taşıyan satıra çekerler. Metin boş kalırsa olduğu gibi döner."""
        titles = [self._documents[doc_id].title for doc_id in doc_ids]
        names = {name for title in titles for name in identifiers_in(title) | model_numbers(title)}
        stripped = text
        for name in sorted(names, key=len, reverse=True):
            pattern = rf"(?<![^\W_]){re.escape(name)}(?:['’]\w+)?(?![^\W_])"
            stripped = re.sub(pattern, " ", stripped, flags=re.IGNORECASE)
        stripped = " ".join(stripped.split())
        return stripped if re.search(r"[^\W_]", stripped) else text

    def is_document_name(self, identifier: str, doc_ids: Iterable[str]) -> bool:
        """Kod, verilen belgelerden birinin başlığındaki kod mu."""
        return any(
            squash(identifier) == squash(known)
            for doc_id in doc_ids
            for known in identifiers_in(self._documents[doc_id].title)
        )
