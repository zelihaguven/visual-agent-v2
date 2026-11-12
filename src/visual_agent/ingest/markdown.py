"""Markdown: başlıklar düzeyleriyle bölüm olur, işaretler metinden çıkar, içerik kalır.

Kurallar biçim düzeyindedir (CommonMark ve tablolar). Vurgu, satır içi kod işareti ve
kaçış ters bölüsü metinden çıkar; bağlantının adresi metinde değilse parantez içinde
kalır, HTML olduğu gibi kalır (yalnız satır sonu etiketi satır sonu olur).
"""

import re
from collections.abc import Sequence

from markdown_it import MarkdownIt
from markdown_it.token import Token

from visual_agent.domain.document import SourceLocation
from visual_agent.ingest.elements import Element, ElementKind, labeled_row

_PARSER = MarkdownIt("commonmark", {"html": True}).enable("table")
_LINE_BREAK_TAG_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_MAILTO = "mailto:"


def _link_suffix(label: str, href: str) -> str:
    """Adres metinde yazmıyorsa içerik kaybolmasın diye eklenir."""
    target = href.removeprefix(_MAILTO)
    if not target or target.lower() == label.strip().lower():
        return ""
    return f" ({target})"


def inline_text(token: Token) -> str:
    """Satır içi öğelerin düz metni; satır sonları korunur."""
    parts: list[str] = []
    links: list[tuple[int, str]] = []
    for child in token.children or []:
        if child.type in ("text", "code_inline", "image"):
            parts.append(child.content)
        elif child.type in ("softbreak", "hardbreak"):
            parts.append("\n")
        elif child.type == "html_inline":
            parts.append("\n" if _LINE_BREAK_TAG_RE.fullmatch(child.content) else child.content)
        elif child.type == "link_open":
            links.append((len(parts), str(child.attrGet("href") or "")))
        elif child.type == "link_close" and links:
            start, href = links.pop()
            parts.append(_link_suffix("".join(parts[start:]), href))
    return "".join(parts).strip()


def _table_rows(tokens: Sequence[Token]) -> list[Element]:
    """İlk satır başlıktır; her gövde satırı ayrı tablo satırı öğesi olur."""
    rows: list[list[str]] = []
    for token in tokens:
        if token.type == "tr_open":
            rows.append([])
        elif token.type == "inline" and rows:
            rows[-1].append(inline_text(token))
    if not rows:
        return []
    labels, body = rows[0], rows[1:]
    texts = (labeled_row(labels, (row + [""] * len(labels))[: len(labels)]) for row in body)
    return [Element(ElementKind.TABLE_ROW, text, SourceLocation()) for text in texts if text]


def _closing_index(tokens: Sequence[Token], start: int, closing: str) -> int:
    for index in range(start, len(tokens)):
        if tokens[index].type == closing:
            return index
    return len(tokens) - 1


def _block_text(token: Token) -> str:
    return _LINE_BREAK_TAG_RE.sub("\n", token.content).strip()


def _leaf(token: Token, following: Token | None, marker: str) -> Element | None:
    """Başlık, paragraf, kod ya da HTML bloğu; diğer işaret öğeleri içerik taşımaz."""
    if token.type == "heading_open" and following is not None:
        text = inline_text(following)
        return Element(ElementKind.HEADING, text, SourceLocation(), level=int(token.tag[1:]))
    if token.type == "paragraph_open" and following is not None:
        return Element(ElementKind.TEXT, f"{marker}{inline_text(following)}", SourceLocation())
    if token.type in ("fence", "code_block"):
        return Element(ElementKind.CODE, token.content.rstrip(), SourceLocation())
    if token.type == "html_block":
        return Element(ElementKind.TEXT, _block_text(token), SourceLocation())
    return None


def parse_markdown(text: str) -> list[Element]:
    tokens = _PARSER.parse(text)
    elements: list[Element] = []
    marker = ""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.type == "table_open":
            end = _closing_index(tokens, index, "table_close")
            elements.extend(_table_rows(tokens[index:end]))
            index = end + 1
            continue
        if token.type == "list_item_open":
            # Sıralı listede madde numarası içeriktir (adım sırası); madde işareti değildir.
            marker = f"{token.info}{token.markup} " if token.info else ""
        following = tokens[index + 1] if index + 1 < len(tokens) else None
        element = _leaf(token, following, marker)
        if element is not None and element.text:
            elements.append(element)
        if token.type == "paragraph_open":
            marker = ""
        index += 1
    return elements
