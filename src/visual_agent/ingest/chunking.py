"""Öğeleri arama parçalarına dönüştürür."""

import re
from collections.abc import Iterable, Sequence

from visual_agent.domain.document import Chunk, ChunkKind, DocumentMeta, SourceLocation
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.verification.text import contains_token

CHUNK_MAX_CHARS = 900
_SECTION_SEPARATOR = " · "
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?:;])\s+")
_STANDALONE_KINDS = {
    ElementKind.TABLE_ROW: ChunkKind.TABLE_ROW,
    ElementKind.CODE: ChunkKind.CODE,
    ElementKind.FIGURE: ChunkKind.FIGURE,
}


def _split_long_text(text: str) -> list[str]:
    pieces: list[str] = []
    current = ""
    for sentence in _SENTENCE_BOUNDARY_RE.split(text):
        candidate = f"{current} {sentence}".strip()
        if len(candidate) <= CHUNK_MAX_CHARS:
            current = candidate
            continue
        if current:
            pieces.append(current)
        while len(sentence) > CHUNK_MAX_CHARS:
            cut = sentence.rfind(" ", 0, CHUNK_MAX_CHARS)
            cut = cut if cut > 0 else CHUNK_MAX_CHARS
            pieces.append(sentence[:cut])
            sentence = sentence[cut:].strip()
        current = sentence
    if current:
        pieces.append(current)
    return pieces


def _split_element(element: Element) -> list[Element]:
    if len(element.text) <= CHUNK_MAX_CHARS:
        return [element]
    return [
        Element(
            element.kind,
            piece,
            element.location,
            element.from_ocr,
            tuple(token for token in element.ocr_uncertain if contains_token(piece, token)),
        )
        for piece in _split_long_text(element.text)
    ]


def _can_merge(group: Sequence[Element], next_element: Element) -> bool:
    if not group or group[0].location.page != next_element.location.page:
        return False
    length = sum(len(element.text) + 1 for element in group) + len(next_element.text)
    return length <= CHUNK_MAX_CHARS


def _merge_group(group: Sequence[Element]) -> Element:
    first = group[0].location
    boxes = tuple(box for element in group for box in element.location.boxes)
    return Element(
        kind=ElementKind.TEXT,
        text=" ".join(element.text for element in group),
        location=SourceLocation(page=first.page, boxes=boxes, sheet=first.sheet, row=first.row),
        from_ocr=any(element.from_ocr for element in group),
        ocr_uncertain=tuple(token for element in group for token in element.ocr_uncertain),
    )


def _sectioned_chunks(elements: Iterable[Element]) -> list[tuple[Element, str]]:
    """Başlıkları bölüm adına çevirir, ardışık paragrafları birleştirir."""
    output: list[tuple[Element, str]] = []
    group: list[Element] = []
    document_heading = ""
    section = ""

    def flush() -> None:
        if group:
            output.append((_merge_group(group), section))
            group.clear()

    for element in elements:
        if element.kind is ElementKind.HEADING:
            flush()
            document_heading = document_heading or element.text
            section = (
                document_heading
                if element.text == document_heading
                else f"{document_heading}{_SECTION_SEPARATOR}{element.text}"
            )
        elif element.kind is ElementKind.TEXT:
            for piece in _split_element(element):
                if not _can_merge(group, piece):
                    flush()
                group.append(piece)
        else:
            flush()
            output.append((element, section))
    flush()
    return output


def build_chunks(elements: Iterable[Element], meta: DocumentMeta) -> list[Chunk]:
    return [
        Chunk(
            chunk_id=f"{meta.doc_id}:{index}",
            doc_id=meta.doc_id,
            kind=_STANDALONE_KINDS.get(element.kind, ChunkKind.TEXT),
            text=element.text,
            title=meta.title,
            section=section,
            location=element.location,
            generated=element.generated,
            ocr_uncertain=element.ocr_uncertain,
            from_ocr=element.from_ocr,
        )
        for index, (element, section) in enumerate(_sectioned_chunks(elements))
    ]
