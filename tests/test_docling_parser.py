"""Docling yolunun gezinme kuralları, sahte bir docling belgesiyle (CI'da docling kurulu değil)."""

from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from visual_agent.domain.document import DocumentMeta
from visual_agent.ingest import docling_parser
from visual_agent.ingest.chunking import build_chunks
from visual_agent.ingest.elements import ElementKind


@dataclass
class _BBox:
    top: float

    def to_top_left_origin(self, page_height: float) -> Any:
        return SimpleNamespace(l=0.0, t=self.top, r=100.0, b=self.top + 10)


@dataclass
class _Item:
    label: str
    text: str
    top: float
    content_layer: str = "body"
    prov: list[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.prov = [SimpleNamespace(page_no=1, bbox=_BBox(self.top))]


class _Document:
    pages = {1: SimpleNamespace(size=SimpleNamespace(width=600.0, height=800.0))}

    def __init__(self, items: list[_Item]) -> None:
        self._items = items

    def iterate_items(self, included_content_layers: set[str] | None = None) -> Any:
        layers = included_content_layers or {"body"}
        return ((item, 0) for item in self._items if item.content_layer in layers)


def _parse(monkeypatch: pytest.MonkeyPatch, items: list[_Item]) -> list[Any]:
    document = _Document(items)
    converter = SimpleNamespace(convert=lambda path: SimpleNamespace(document=document))
    monkeypatch.setattr(docling_parser, "_converter", lambda: converter)
    return docling_parser.parse_with_docling(Path("belge.pdf"))


def test_model_code_in_the_page_header_names_the_section(monkeypatch: pytest.MonkeyPatch) -> None:
    """B6: Word'den dönen dikim-word'de docling ilk satırı ("CKT-7308 ölçü föyü") üst bilgi
    sayıyordu; yalnız gövde gezildiği için kod hiçbir parçaya geçmiyordu (A4, B4)."""
    elements = _parse(
        monkeypatch,
        [
            _Item("page_header", "CKT-7308 ölçü föyü", 10, content_layer="furniture"),
            _Item("section_header", "Ölçü tablosu", 40),
            _Item("text", "Kalça | L: 52,5", 60),
            _Item("page_footer", "Sayfa 1 / 1", 780, content_layer="furniture"),
        ],
    )

    assert [(element.kind, element.text) for element in elements] == [
        (ElementKind.HEADING, "CKT-7308 ölçü föyü"),
        (ElementKind.HEADING, "Ölçü tablosu"),
        (ElementKind.TEXT, "Kalça | L: 52,5"),
    ]
    [chunk] = build_chunks(elements, DocumentMeta(doc_id="d", title="dikim-word", language="tr"))
    assert "CKT-7308" in chunk.section


def test_page_header_without_a_code_and_other_furniture_are_dropped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    elements = _parse(
        monkeypatch,
        [
            _Item("page_header", "Gizli - Şirket içi", 10, content_layer="furniture"),
            _Item("text", "Gövde metni", 60),
            _Item("text", "Sayfa altı metni", 780, content_layer="furniture"),
        ],
    )

    assert [element.text for element in elements] == ["Gövde metni"]
