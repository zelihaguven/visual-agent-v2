"""Öğeleri arama parçalarına dönüştürür."""

import re
from collections.abc import Iterable, Sequence

from visual_agent.domain.document import Box, Chunk, ChunkKind, DocumentMeta, SourceLocation
from visual_agent.ingest.elements import SECTION_SEPARATOR, Element, ElementKind
from visual_agent.verification.text import contains_token, identifiers_in

CHUNK_MAX_CHARS = 900
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


HeadingPath = tuple[tuple[int, str], ...]
_ROOT_LEVEL = 0
_UNKNOWN_LEVEL = 99


def _next_path(path: HeadingPath, heading: Element, after_content: bool = False) -> HeadingPath:
    """Düzeyi bilinen başlık kendi düzeyindeki ve altındaki başlıkların yerini alır.

    Düzeyi bilinmeyen başlık belgenin ilk başlığının altına girer; ilk başlığın aynısıysa
    bölüm yalnız ilk başlıktır. Belgenin ilk başlığı içerikten sonra geliyor ve kod taşımıyorsa
    (after_content) belge başlığı değildir: düzeyi bilinmeyen başlıklar kardeştir, her biri
    öncekinin yerini alır.
    """
    if heading.level is not None:
        kept = tuple(item for item in path if item[0] < heading.level)
        return (*kept, (heading.level, heading.text))
    if not path:
        return ((_UNKNOWN_LEVEL if after_content else _ROOT_LEVEL, heading.text),)
    root = path[0]
    if root[0] == _UNKNOWN_LEVEL:
        return ((_UNKNOWN_LEVEL, heading.text),)
    return (root,) if heading.text == root[1] else (root, (_UNKNOWN_LEVEL, heading.text))


def _sectioned_chunks(elements: Iterable[Element]) -> list[tuple[Element, str, tuple[str, ...]]]:
    """Başlıkları bölüm yoluna çevirir, ardışık paragrafları birleştirir. Bölüm yolundaki
    başlıkların belirsiz okunan değerleri de döner: başlık parça olmadığı için bölüm adında
    kalan belirsiz kod ("iGML-6473") yoksa cümlede doğrulanmış geçebilirdi."""
    output: list[tuple[Element, str, tuple[str, ...]]] = []
    group: list[Element] = []
    path: HeadingPath = ()
    heading_uncertain: dict[str, tuple[str, ...]] = {}
    page_headings: dict[int | None, list[_PlacedHeading]] = {}

    def uncertain_of(of: HeadingPath) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(token for _, text in of for token in heading_uncertain.get(text, ()))
        )

    def flush() -> None:
        if group:
            output.append((_merge_group(group), _section(path), uncertain_of(path)))
            group.clear()

    for element in elements:
        if element.kind is ElementKind.HEADING:
            flush()
            # Kod taşıyan ilk başlık içerikten sonra da gelse belge başlığıdır (kod bölüm yolunda
            # kalmalı: kod dizini ve cevap denetimi onu bağlamdan okur).
            after_content = bool(output) and not identifiers_in(element.text)
            before, path = path, _next_path(path, element, after_content)
            heading_uncertain[element.text] = element.ocr_uncertain
            placed = page_headings.setdefault(element.location.page, [])
            placed.append((_page_box(element), before, path))
        elif element.kind is ElementKind.TEXT:
            for piece in _split_element(element):
                if not _can_merge(group, piece):
                    flush()
                group.append(piece)
        else:
            flush()
            own = path
            if element.kind is ElementKind.TABLE_ROW:
                own = _row_path(path, element, page_headings.get(element.location.page, []))
            section = SECTION_SEPARATOR.join(p for p in (_section(own), element.context) if p)
            output.append((element, section, uncertain_of(own)))
    flush()
    return output


def _section(path: HeadingPath) -> str:
    return SECTION_SEPARATOR.join(text for _, text in path)


_PlacedHeading = tuple[Box | None, HeadingPath, HeadingPath]
"""Sayfadaki başlık: kutusu, kendisinden önceki ve sonraki bölüm yolu."""


def _page_box(element: Element) -> Box | None:
    page = element.location.page
    return next((box for box in element.location.boxes if box.page == page), None)


def _row_path(path: HeadingPath, row: Element, headings: Sequence[_PlacedHeading]) -> HeadingPath:
    """Tablo satırının bölümü: aynı sayfada satırın üstünde başlayan ve yatayda satırla örtüşen
    en yakın başlığın yolu. Yan yana tablolarda okuma sırası başlıkları önce, tabloları sonra
    verebilir; son başlık öbür tablonun başlığıdır (QM s.16). Üstünde örtüşen başlık yoksa
    sayfanın başlıkları devralınmaz: yol sayfadaki ilk başlıktan öncekidir. Satırın ya da
    sayfadaki bir başlığın kutusu yoksa (Markdown, Excel) bölüm okuma sırasındaki son başlıktır."""
    box = _page_box(row)
    if box is None or not headings or any(heading is None for heading, _, _ in headings):
        return path
    above = [
        (heading, after)
        for heading, _, after in headings
        if heading is not None
        and heading.top < box.top
        and heading.left < box.right
        and box.left < heading.right
    ]
    if above:
        return max(above, key=lambda item: item[0].bottom)[1]
    return headings[0][1]


def _location(element: Element, section: str) -> SourceLocation:
    """Sayfası ve sayfa adı olmayan kaynağın konumu bölüm yoludur."""
    location = element.location
    if location.page is None and location.sheet is None and section:
        return location.model_copy(update={"section": section})
    return location


def build_chunks(elements: Iterable[Element], meta: DocumentMeta) -> list[Chunk]:
    return [
        Chunk(
            chunk_id=f"{meta.doc_id}:{index}",
            doc_id=meta.doc_id,
            kind=_STANDALONE_KINDS.get(element.kind, ChunkKind.TEXT),
            text=element.text,
            title=meta.title,
            section=section,
            location=_location(element, section),
            ocr_uncertain=tuple(dict.fromkeys((*element.ocr_uncertain, *section_uncertain))),
            from_ocr=element.from_ocr,
            table_note=element.context,
        )
        for index, (element, section, section_uncertain) in enumerate(_sectioned_chunks(elements))
    ]
