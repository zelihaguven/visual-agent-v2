"""Kod ve teknik adların tam eşleşme indeksi: taramasız arama."""

import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from visual_agent.domain.document import Chunk
from visual_agent.verification.text import compact_identifier, identifiers_in

_SPOKEN_CODE_RE = re.compile(r"(?<!\w)[^\W\d_]{1,6}[-_\s]?\d+(?!\w)")

Posting = tuple[str, str]


@dataclass(frozen=True)
class IdentifierIndex:
    _postings: dict[str, tuple[Posting, ...]]
    _chunks: dict[str, Chunk]
    _aliases: dict[str, tuple[str, ...]]

    def _postings_of(self, identifier: str) -> tuple[Posting, ...]:
        keys = self._aliases.get(compact_identifier(identifier), ())
        return tuple(dict.fromkeys(posting for key in keys for posting in self._postings[key]))

    def lookup(self, identifier: str, doc_ids: Sequence[str] | None = None) -> tuple[str, ...]:
        return tuple(
            chunk_id
            for doc_id, chunk_id in self._postings_of(identifier)
            if doc_ids is None or doc_id in doc_ids
        )

    def chunks_for(self, identifier: str, doc_ids: Sequence[str] | None) -> tuple[Chunk, ...]:
        return tuple(self._chunks[chunk_id] for chunk_id in self.lookup(identifier, doc_ids))

    def documents_with(self, identifier: str) -> tuple[str, ...]:
        return tuple(dict.fromkeys(doc_id for doc_id, _ in self._postings_of(identifier)))

    def codes_in_speech(self, text: str) -> set[str]:
        """Yazıya çevirmede tiresi düşmüş ya da küçülmüş kodlar; yalnız belgede olanlar sayılır."""
        candidates = (compact_identifier(m.group(0)) for m in _SPOKEN_CODE_RE.finditer(text))
        return {self._aliases[key][0] for key in candidates if key in self._aliases}

    def codes_of(self, doc_id: str) -> tuple[str, ...]:
        """Belgedeki kodlar; sütun ve tablo adları kod sayılmaz."""
        codes = (
            identifier
            for identifier, postings in self._postings.items()
            if any(c.isdigit() for c in identifier) and any(d == doc_id for d, _ in postings)
        )
        return tuple(sorted(code.upper() for code in codes))


def build_identifier_index(chunks: Iterable[Chunk]) -> IdentifierIndex:
    postings: defaultdict[str, list[Posting]] = defaultdict(list)
    by_id: dict[str, Chunk] = {}
    for chunk in chunks:
        by_id[chunk.chunk_id] = chunk
        for identifier in identifiers_in(chunk.embed_text):
            postings[identifier].append((chunk.doc_id, chunk.chunk_id))
    aliases: defaultdict[str, list[str]] = defaultdict(list)
    for identifier in sorted(postings):
        aliases[compact_identifier(identifier)].append(identifier)
    return IdentifierIndex(
        {key: tuple(value) for key, value in postings.items()},
        by_id,
        {key: tuple(value) for key, value in aliases.items()},
    )
