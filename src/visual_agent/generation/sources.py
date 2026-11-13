"""Bulunan parçaları modele verilecek kaynaklara çevirir."""

from collections.abc import Callable, Sequence

from visual_agent.domain.answer import PromptSource
from visual_agent.domain.document import ChunkKind
from visual_agent.domain.result import Hit

_PART_LABELS = {ChunkKind.FIGURE: "şekil", ChunkKind.CODE: "kod"}
_CLOSING_TAG = "</kaynak"
_NEUTRAL_CLOSING_TAG = "< /kaynak"


def to_prompt_sources(
    hits: Sequence[Hit], language_of: Callable[[str], str]
) -> dict[int, PromptSource]:
    """language_of: belge kimliğinden katalogdaki dili."""
    return {
        number: PromptSource(
            number=number,
            text=hit.chunk.text,
            context=f"{hit.chunk.title} {hit.chunk.section}".strip(),
            ocr_uncertain=hit.chunk.ocr_uncertain,
            is_code=hit.chunk.kind is ChunkKind.CODE,
            from_ocr=hit.chunk.from_ocr,
            language=language_of(hit.chunk.doc_id),
        )
        for number, hit in enumerate(hits, start=1)
    }


def _attribute(value: str) -> str:
    return value.replace('"', "'")


def format_sources(hits: Sequence[Hit]) -> str:
    parts = []
    for number, hit in enumerate(hits, start=1):
        chunk = hit.chunk
        label = _PART_LABELS.get(chunk.kind)
        part = f' parça="{label}"' if label else ""
        text = chunk.text.replace(_CLOSING_TAG, _NEUTRAL_CLOSING_TAG)
        parts.append(
            f'<kaynak no="{number}" belge="{_attribute(chunk.title)}"{part} '
            f'bölüm="{_attribute(chunk.section)}">\n{text}\n</kaynak>'
        )
    return "<kaynaklar>\n" + "\n".join(parts) + "\n</kaynaklar>"


def build_user_message(hits: Sequence[Hit], question: str, language: str) -> str:
    return (
        f"{format_sources(hits)}\n\n<cevap_dili>{language.upper()}</cevap_dili>\n\n"
        f"<soru>\n{question}\n</soru>"
    )
