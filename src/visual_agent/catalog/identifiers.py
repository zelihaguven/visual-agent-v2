"""Kod ve teknik adların tam eşleşme indeksi: taramasız arama."""

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from visual_agent.domain.document import Chunk
from visual_agent.verification.text import fold_identifier, identifiers_in


@dataclass(frozen=True)
class IdentifierIndex:
    _postings: dict[str, tuple[tuple[str, str], ...]]
    _chunks: dict[str, Chunk]

    def lookup(self, identifier: str, doc_ids: Sequence[str] | None = None) -> tuple[str, ...]:
        postings = self._postings.get(fold_identifier(identifier), ())
        return tuple(
            chunk_id for doc_id, chunk_id in postings if doc_ids is None or doc_id in doc_ids
        )

    def chunks_for(self, identifier: str, doc_ids: Sequence[str] | None) -> tuple[Chunk, ...]:
        return tuple(self._chunks[chunk_id] for chunk_id in self.lookup(identifier, doc_ids))

    def documents_with(self, identifier: str) -> tuple[str, ...]:
        postings = self._postings.get(fold_identifier(identifier), ())
        return tuple(dict.fromkeys(doc_id for doc_id, _ in postings))


def build_identifier_index(chunks: Iterable[Chunk]) -> IdentifierIndex:
    postings: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    by_id: dict[str, Chunk] = {}
    for chunk in chunks:
        by_id[chunk.chunk_id] = chunk
        for identifier in identifiers_in(chunk.embed_text):
            postings[identifier].append((chunk.doc_id, chunk.chunk_id))
    return IdentifierIndex({key: tuple(value) for key, value in postings.items()}, by_id)
