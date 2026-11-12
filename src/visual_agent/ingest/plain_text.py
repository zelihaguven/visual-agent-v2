"""Düz metin, markdown ve SQL dosyaları."""

import re
from pathlib import Path

from visual_agent.domain.document import SourceLocation
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.formats import InputFormat
from visual_agent.ingest.markdown import parse_markdown

_COMMENT_PREFIX = "--"
_BLANK_LINES_RE = re.compile(r"\n\s*\n")
_SECTION_SEPARATOR = " · "


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1254")


def _heading(comments: list[str]) -> Element:
    text = _SECTION_SEPARATOR.join(dict.fromkeys(comments))
    return Element(ElementKind.HEADING, text, SourceLocation())


def _parse_sql(text: str) -> list[Element]:
    elements: list[Element] = []
    comments: list[str] = []
    code: list[str] = []

    def flush_code() -> None:
        if code:
            elements.append(Element(ElementKind.CODE, "\n".join(code), SourceLocation()))
            code.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(_COMMENT_PREFIX):
            flush_code()
            comments.append(stripped.removeprefix(_COMMENT_PREFIX).strip())
        elif not stripped:
            flush_code()
        else:
            if comments:
                elements.append(_heading(comments))
                comments = []
            code.append(line.rstrip())
    flush_code()
    return elements


def parse_plain_text(path: Path, input_format: InputFormat) -> list[Element]:
    text = _read_text(path)
    if input_format is InputFormat.SQL:
        return _parse_sql(text)
    if input_format is InputFormat.MARKDOWN:
        return parse_markdown(text)
    return [
        Element(ElementKind.TEXT, paragraph.strip(), SourceLocation())
        for paragraph in _BLANK_LINES_RE.split(text)
        if paragraph.strip()
    ]
