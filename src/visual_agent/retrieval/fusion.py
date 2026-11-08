"""Arama kollarının belirli sırayla birleştirilmesi."""

import re
from collections.abc import Sequence
from dataclasses import dataclass

from visual_agent.domain.document import Chunk

_RRF_K = 2
_MIN_TOC_LEADERS = 2
_TOC_LEADER_RE = re.compile(r"\.{5,}\s*\d+")
_TOC_LINE_RE = re.compile(r"\s*[\w\-. ()/]{3,80}?\s*\.{5,}\s*\d+\s*")


@dataclass(frozen=True)
class ScoredChunk:
    chunk: Chunk
    score: float


def is_table_of_contents(text: str) -> bool:
    return len(_TOC_LEADER_RE.findall(text)) >= _MIN_TOC_LEADERS or bool(
        _TOC_LINE_RE.fullmatch(text)
    )


def rrf_fuse(
    dense: Sequence[ScoredChunk], sparse: Sequence[ScoredChunk], limit: int
) -> list[ScoredChunk]:
    """Eşitlikte önce dense skoru, sonra parça kimliği belirler; sonuç her koşuda aynıdır."""
    fused: dict[str, float] = {}
    chunks: dict[str, Chunk] = {}
    for arm in (dense, sparse):
        for rank, item in enumerate(arm):
            chunk_id = item.chunk.chunk_id
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (rank + _RRF_K)
            chunks.setdefault(chunk_id, item.chunk)
    dense_scores = {item.chunk.chunk_id: item.score for item in dense}
    order = sorted(
        fused,
        key=lambda chunk_id: (
            -fused[chunk_id],
            -dense_scores.get(chunk_id, float("-inf")),
            chunk_id,
        ),
    )
    return [ScoredChunk(chunks[chunk_id], fused[chunk_id]) for chunk_id in order[:limit]]
