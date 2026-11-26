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
            is_table_row=hit.chunk.kind is ChunkKind.TABLE_ROW,
            from_ocr=hit.chunk.from_ocr,
            language=language_of(hit.chunk.doc_id),
            title=hit.chunk.title,
        )
        for number, hit in enumerate(hits, start=1)
    }


def _attribute(value: str) -> str:
    return value.replace('"', "'")


def _document_names(hits: Sequence[Hit]) -> dict[str, str]:
    """Belgenin modele görünen adı. Aynı adla yüklenmiş farklı belgeler ayırt edilir ("Föy",
    "Föy (2)"): model belge sayısına göre karar verir (istem, 7. kural) ve aynı adlı iki
    belgeyi tek belge sanmamalı. Üretilen ad başka bir belgenin gerçek adıyla çakışmaz."""
    titles = {hit.chunk.doc_id: hit.chunk.title for hit in reversed(hits)}
    names: dict[str, str] = {}
    used = set(titles.values())
    seen: set[str] = set()
    for doc_id in dict.fromkeys(hit.chunk.doc_id for hit in hits):
        title, name, number = titles[doc_id], titles[doc_id], 1
        while name in seen or (number > 1 and name in used):
            number += 1
            name = f"{title} ({number})"
        seen.add(name)
        names[doc_id] = name
    return names


def format_sources(hits: Sequence[Hit]) -> str:
    parts = []
    names = _document_names(hits)
    for number, hit in enumerate(hits, start=1):
        chunk = hit.chunk
        label = _PART_LABELS.get(chunk.kind)
        part = f' parça="{label}"' if label else ""
        text = chunk.text.replace(_CLOSING_TAG, _NEUTRAL_CLOSING_TAG)
        parts.append(
            f'<kaynak no="{number}" belge="{_attribute(names[chunk.doc_id])}"{part} '
            f'bölüm="{_attribute(chunk.section)}">\n{text}\n</kaynak>'
        )
    return "<kaynaklar>\n" + "\n".join(parts) + "\n</kaynaklar>"


def build_user_message(hits: Sequence[Hit], question: str, language: str) -> str:
    return (
        f"{format_sources(hits)}\n\n<cevap_dili>{language.upper()}</cevap_dili>\n\n"
        f"<soru>\n{question}\n</soru>"
    )
