"""Alıntının kaynakla birebir eşleşmesi; yalnız biçim farkı (quote_form) yok sayılır."""

from visual_agent.verification.text import CUT_CITATION_RE, quote_form

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
    wanted_label, wanted_value = quote_form(label), quote_form(value)
    return any(
        quote_form(cell_label) == wanted_label and wanted_value in quote_form(cell_value)
        for line in source.splitlines()
        for cell_label, cell_value in _labeled_cells(line)
    )


def _cut_prefix_matches(quote: str, normalized_source: str) -> bool:
    """Uzunluk sınırına dayanıp sonu bozulan alıntının başı kaynakla örtüşüyorsa kabul eder."""
    if len(quote) < QUOTE_LIMIT - _CUT_MARGIN:
        return False
    normalized = quote_form(quote)
    words = normalized.split(" ")
    for count in range(len(words) - 1, 0, -1):
        head = " ".join(words[:count])
        if head in normalized_source:
            return len(normalized) - len(head) <= _CUT_MAX_TAIL
    return False


def quote_matches(quote: str, source: str) -> bool:
    without_citation = CUT_CITATION_RE.sub("", quote)
    normalized_quote = quote_form(without_citation)
    if not normalized_quote:
        return False
    normalized_source = quote_form(source)
    return (
        normalized_quote in normalized_source
        or field_quote_matches(without_citation, source)
        or _cut_prefix_matches(quote, normalized_source)
    )
