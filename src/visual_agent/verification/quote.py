"""Alıntının kaynakla birebir eşleşmesi; yalnız biçim farkı yok sayılır.

İki yol denenir: birebir yol (tırnak ve boşluk dışında biçime dokunmaz) ve sade yol (kaynakta
yalnız eşli markdown işaretleri, alıntıda bütün ** ve ters tırnaklar kalkar). Kaynak biçimi
(markdown, PDF, Word) denetimde bilinmez; bu yüzden kaynakta eşsiz işaret içerik sayılır.
"""

from collections.abc import Callable

from visual_agent.verification.text import (
    CUT_CITATION_RE,
    quote_form,
    quote_plain_form,
    source_plain_form,
)

QUOTE_LIMIT = 150
_CUT_MARGIN = 15
_CUT_MAX_TAIL = 20
_CELL_SEPARATOR = " | "
_LABEL_SEPARATOR = ": "
_MAX_LABEL_LENGTH = 80

Form = Callable[[str], str]
_WAYS: tuple[tuple[Form, Form], ...] = (
    (quote_form, quote_form),
    (quote_plain_form, source_plain_form),
)


def _labeled_cells(line: str) -> list[tuple[str, str]]:
    cells = []
    for part in (piece.strip() for piece in line.split(_CELL_SEPARATOR)):
        label, separator, value = part.partition(_LABEL_SEPARATOR)
        if separator and len(label) <= _MAX_LABEL_LENGTH:
            cells.append((label.strip(), value.strip()))
    return cells


def _field_matches(quote: str, source: str, quote_way: Form, source_way: Form) -> bool:
    label, separator, value = quote.strip().partition(_LABEL_SEPARATOR)
    value = value.strip()
    if not separator or not value or "|" in value or "|" in label:
        return False
    wanted_label, wanted_value = quote_way(label), quote_way(value)
    return any(
        source_way(cell_label) == wanted_label and wanted_value in source_way(cell_value)
        for line in source.splitlines()
        for cell_label, cell_value in _labeled_cells(line)
    )


def field_quote_matches(quote: str, source: str) -> bool:
    """Etiketli hücre alıntısı, aynı etiketin hücresinde bitişik geçmelidir."""
    return any(_field_matches(quote, source, q, s) for q, s in _WAYS)


def _cut_prefix_matches(quote: str, normalized_source: str, quote_way: Form) -> bool:
    """Uzunluk sınırına dayanıp sonu bozulan alıntının başı kaynakla örtüşüyorsa kabul eder."""
    if len(quote) < QUOTE_LIMIT - _CUT_MARGIN:
        return False
    normalized = quote_way(quote)
    words = normalized.split(" ")
    for count in range(len(words) - 1, 0, -1):
        head = " ".join(words[:count])
        if head in normalized_source:
            return len(normalized) - len(head) <= _CUT_MAX_TAIL
    return False


def _matches(quote: str, source: str, quote_way: Form, source_way: Form) -> bool:
    without_citation = CUT_CITATION_RE.sub("", quote)
    normalized_quote = quote_way(without_citation)
    if not normalized_quote:
        return False
    normalized_source = source_way(source)
    return (
        normalized_quote in normalized_source
        or _field_matches(without_citation, source, quote_way, source_way)
        or _cut_prefix_matches(quote, normalized_source, quote_way)
    )


def quote_matches(quote: str, source: str) -> bool:
    return any(_matches(quote, source, q, s) for q, s in _WAYS)
