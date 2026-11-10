"""OCR parçalarını satır ve tabloya çevirir."""

from collections.abc import Sequence
from dataclasses import dataclass, replace

from visual_agent.domain.document import Box, SourceLocation
from visual_agent.ingest.elements import Element, ElementKind
from visual_agent.ingest.two_reading import contains_token

_LINE_OVERLAP_RATIO = 0.5
_MIN_TABLE_LINES = 2
_MIN_TABLE_COLUMNS = 2


@dataclass(frozen=True)
class OcrSegment:
    text: str
    left: float
    top: float
    right: float
    bottom: float

    @property
    def middle(self) -> float:
        return (self.top + self.bottom) / 2


def group_lines(segments: Sequence[OcrSegment]) -> list[list[OcrSegment]]:
    """Dikey olarak örtüşen parçaları soldan sağa sıralı satırlarda toplar."""
    lines: list[list[OcrSegment]] = []
    for segment in sorted(segments, key=lambda item: item.top):
        height = segment.bottom - segment.top
        line = next(
            (
                candidate
                for candidate in lines
                if abs(candidate[0].middle - segment.middle) <= height * _LINE_OVERLAP_RATIO
            ),
            None,
        )
        if line is None:
            lines.append([segment])
        else:
            line.append(segment)
    return [sorted(line, key=lambda item: item.left) for line in lines]


def _anchor_line(lines: Sequence[Sequence[OcrSegment]]) -> Sequence[OcrSegment]:
    return max(lines, key=len) if lines else ()


def _is_table(lines: Sequence[Sequence[OcrSegment]]) -> bool:
    columns = len(_anchor_line(lines))
    if len(lines) < _MIN_TABLE_LINES or columns < _MIN_TABLE_COLUMNS:
        return False
    return sum(len(line) == columns for line in lines) * 2 >= len(lines)


def _aligned(line: Sequence[OcrSegment], anchors: Sequence[OcrSegment]) -> dict[int, str]:
    """Okunamayan hücreler olabildiği için parçalar en yakın sütuna yerleştirilir."""
    cells: dict[int, str] = {}
    for item in line:
        column = min(range(len(anchors)), key=lambda index: abs(anchors[index].left - item.left))
        cells[column] = f"{cells[column]} {item.text}" if column in cells else item.text
    return cells


def _row_text(cells: dict[int, str], headers: dict[int, str]) -> str:
    return " | ".join(
        f"{headers[column]}: {text}" if column in headers else text
        for column, text in sorted(cells.items())
    )


def _line_box(line: Sequence[OcrSegment], image_box: Box) -> Box:
    return replace_box(
        image_box,
        left=min(item.left for item in line),
        top=min(item.top for item in line),
        right=max(item.right for item in line),
        bottom=max(item.bottom for item in line),
    )


def image_skip_reason(box: Box, min_area_ratio: float, min_side_points: float) -> str | None:
    """Görsel okunmayacaksa kullanıcıya gösterilecek neden; okunacaksa None."""
    width, height = box.right - box.left, box.bottom - box.top
    side = min(width, height)
    area_ratio = width * height / (box.page_width * box.page_height or 1.0)
    reasons = []
    if side < min_side_points:
        reasons.append(f"kısa kenarı {side:.0f} pt, en az {min_side_points:.0f} pt gerekir")
    if area_ratio < min_area_ratio:
        percent = f"{area_ratio * 100:.1f}".replace(".", ",")
        minimum = f"{min_area_ratio * 100:.0f}"
        reasons.append(f"alanı sayfanın %{percent} kadarı, en az %{minimum} gerekir")
    return "; ".join(reasons) or None


def replace_box(box: Box, *, left: float, top: float, right: float, bottom: float) -> Box:
    return box.model_copy(update={"left": left, "top": top, "right": right, "bottom": bottom})


def _element(kind: ElementKind, text: str, box: Box) -> Element:
    return Element(kind, text, SourceLocation(page=box.page, boxes=(box,)), from_ocr=True)


def lines_to_elements(lines: Sequence[Sequence[OcrSegment]], image_box: Box) -> list[Element]:
    """Sütunları tutarlı görsel tablo sayılır; ilk satırı başlıktır."""
    if _is_table(lines):
        anchors = _anchor_line(lines)
        headers = _aligned(lines[0], anchors)
        return [
            _element(
                ElementKind.TABLE_ROW,
                _row_text(_aligned(line, anchors), headers),
                _line_box(line, image_box),
            )
            for line in lines[1:]
        ]
    return [
        _element(
            ElementKind.FIGURE, " ".join(item.text for item in line), _line_box(line, image_box)
        )
        for line in lines
    ]


def with_uncertain_tokens(element: Element, tokens: Sequence[str]) -> Element:
    return replace(
        element,
        ocr_uncertain=tuple(token for token in tokens if contains_token(element.text, token)),
    )
