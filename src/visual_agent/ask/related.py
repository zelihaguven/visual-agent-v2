"""Doğrudan cevap yoksa getirilen parçaların başlıkları gösterilir.

Yalnız arama sırasındaki belge ve bölüm adları yazılır; parçaların içeriğinden hiçbir şey
cevap gibi aktarılmaz.
"""

from collections.abc import Sequence

from visual_agent.domain.result import AskResult, Hit, NotFound

MAX_RELATED = 4
_LEADS = {
    "tr": "Doğrudan cevap bulunamadı. Aramada en yakın çıkan başlıklar: ",
    "en": "No direct answer was found. Closest headings in the search: ",
}


def _heading(hit: Hit) -> str:
    chunk = hit.chunk
    return chunk.section or chunk.title


def with_related_headings(result: AskResult, hits: Sequence[Hit], language: str) -> AskResult:
    """Gerekçesiz "bulunamadı" sonucuna en fazla dört başlık ve belgesi eklenir."""
    if not isinstance(result, NotFound) or result.reason or not hits:
        return result
    headings = list(dict.fromkeys(_heading(hit) for hit in hits))[:MAX_RELATED]
    documents = tuple(dict.fromkeys(hit.chunk.doc_id for hit in hits))[:MAX_RELATED]
    lead = _LEADS.get(language, _LEADS["tr"])
    return NotFound(
        reason=lead + "; ".join(headings) + ".",
        suggested_doc_ids=result.suggested_doc_ids or documents,
    )
