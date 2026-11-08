"""Alıntının kaynakla birebir eşleşmesi."""

from visual_agent.verification.text import CUT_CITATION_RE, normalize

QUOTE_LIMIT = 150
_CUT_MARGIN = 15
_CUT_MAX_TAIL = 20
_CELL_SEPARATOR = " | "
_LABEL_SEPARATOR = ": "
_MAX_LABEL_LENGTH = 80


def _labeled_cells(line: str) -> list[tuple[str, str]]:
    cells = []
    for part in (piece.strip() for piece in line.split(_CELL_SEPARATOR)):
        label, separator, value = part.partition(_LABEL_SEPARATOR)
        if separator and len(label) <= _MAX_LABEL_LENGTH:
            cells.append((label.strip(), value.strip()))
    return cells


def field_quote_matches(quote: str, source: str) -> bool:
    """Etiketli hücre alıntısı, aynı etiketin hücresinde bitişik geçmelidir."""
    label, separator, value = quote.strip().partition(_LABEL_SEPARATOR)
    value = value.strip()
    if not separator or not value or "|" in value or "|" in label:
        return False
    wanted_label, wanted_value = normalize(label), normalize(value)
    return any(
        normalize(cell_label) == wanted_label and wanted_value in normalize(cell_value)
        for line in source.splitlines()
        for cell_label, cell_value in _labeled_cells(line)
    )


def _cut_prefix_matches(quote: str, normalized_source: str) -> bool:
    """Uzunluk sınırına dayanıp sonu bozulan alıntının başı kaynakla örtüşüyorsa kabul eder."""
    if len(quote) < QUOTE_LIMIT - _CUT_MARGIN:
        return False
    normalized = normalize(quote)
    words = normalized.split(" ")
    for count in range(len(words) - 1, 0, -1):
        head = " ".join(words[:count])
        if head in normalized_source:
            return len(normalized) - len(head) <= _CUT_MAX_TAIL
    return False


def quote_matches(quote: str, source: str) -> bool:
    without_citation = CUT_CITATION_RE.sub("", quote)
    normalized_quote = normalize(without_citation)
    if not normalized_quote:
        return False
    normalized_source = normalize(source)
    return (
        normalized_quote in normalized_source
        or field_quote_matches(without_citation, source)
        or _cut_prefix_matches(quote, normalized_source)
    )
