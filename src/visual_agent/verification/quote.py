"""Alıntının kaynakla birebir eşleşmesi; yalnız biçim farkı yok sayılır.

İki yol denenir, ikisinde de alıntıya ve parçaya aynı biçim uygulanır:
1. Birebir yol: yalnız tırnak türü ve boşluk tek biçime iner (quote_form).
2. Sade yol: markdown vurgusu, satır içi kod işareti ve kaçış standart ayrıştırıcıyla kalkar
   (markdown_plain_form). Kaynak biçimi (markdown, PDF, Word) denetimde bilinmez.
İkisi de tutmazsa alıntı reddedilir.
"""

from collections.abc import Callable

from visual_agent.verification.text import (
    CUT_CITATION_RE,
    MINUS_SIGNS,
    identifiers_in,
    markdown_plain_form,
    quote_form,
    word_numbers,
)

QUOTE_LIMIT = 150
_CUT_MARGIN = 15
_CUT_MAX_TAIL = 20
_CELL_SEPARATOR = " | "
_LABEL_SEPARATOR = ": "
_MAX_LABEL_LENGTH = 80

Form = Callable[[str], str]
_FORMS: tuple[Form, ...] = (quote_form, markdown_plain_form)


def _is_sign(text: str, position: int) -> bool:
    """Rakamdan hemen önceki çizgi, önünde rakam yoksa sayının parçasıdır.

    Biçim, çizginin çevresindeki boşluğu siler ("sıcaklık -5" -> "sıcaklık-5"); bu yüzden
    önündeki harfe bakılmaz. Aralıktaki çizgi ("10-14") işaret sayılmaz.
    """
    return (
        text[position] in MINUS_SIGNS
        and position + 1 < len(text)
        and text[position + 1].isdigit()
        and (position == 0 or not text[position - 1].isdigit())
    )


def _in_number(text: str, position: int) -> bool:
    """Konumdaki karakter bir sayının parçası mı: rakam ya da iki rakam arasındaki ayırıcı."""
    if not 0 <= position < len(text):
        return False
    character = text[position]
    if character.isdigit() or _is_sign(text, position):
        return True
    return (
        character in ".,"
        and 0 < position < len(text) - 1
        and text[position - 1].isdigit()
        and text[position + 1].isdigit()
    )


def _cuts_number(text: str, boundary: int) -> bool:
    return _in_number(text, boundary - 1) and _in_number(text, boundary)


def contains_whole(haystack: str, needle: str) -> bool:
    """Metinde geçer, ama bir sayının ortasından başlamaz ya da bitmez ("4", "74" içinde yok)."""
    start = haystack.find(needle)
    while start >= 0:
        end = start + len(needle)
        if not _cuts_number(haystack, start) and not _cuts_number(haystack, end):
            return True
        start = haystack.find(needle, start + 1)
    return False


def _labeled_cells(line: str) -> list[tuple[str, str]]:
    cells = []
    for part in (piece.strip() for piece in line.split(_CELL_SEPARATOR)):
        label, separator, value = part.partition(_LABEL_SEPARATOR)
        if separator and len(label) <= _MAX_LABEL_LENGTH:
            cells.append((label.strip(), value.strip()))
    return cells


def _field_matches(quote: str, source: str, form: Form) -> bool:
    label, separator, value = quote.strip().partition(_LABEL_SEPARATOR)
    value = value.strip()
    if not separator or not value or "|" in value or "|" in label:
        return False
    wanted_label, wanted_value = form(label), form(value)
    return any(
        form(cell_label) == wanted_label and contains_whole(form(cell_value), wanted_value)
        for line in source.splitlines()
        for cell_label, cell_value in _labeled_cells(line)
    )


def _carries_values(tail: str, written_tail: str) -> bool:
    """Denetlenmeyen kuyrukta sayı, yazıyla sayı ya da teknik ad olamaz; olursa kanıt sayılırdı.

    Yazıyla sayı alıntının yazıldığı hâlinden okunur: küçük harfe indirmek "İki" ve "ALTI"
    sözcüklerini tanınmaz kılar.
    """
    return (
        any(character.isdigit() for character in tail)
        or bool(identifiers_in(tail))
        or bool(word_numbers(written_tail))
    )


def _written_tail(quote: str, normalized_words: list[str], head_count: int) -> str:
    """Alıntının yazıldığı hâlinden kuyruğu kapsayan son sözcükler.

    Biçim sözcük sayısını değiştirebilir (vurgu işareti, çizgi çevresi); fark kadar fazla
    sözcük alınır, kuyruk dışarıda kalmaz.
    """
    written_words = quote.split()
    tail_count = len(normalized_words) - head_count
    extra = max(0, len(written_words) - len(normalized_words))
    return " ".join(written_words[-(tail_count + extra) :])


def _cut_prefix_matches(quote: str, normalized_source: str, form: Form) -> bool:
    """Uzunluk sınırına dayanıp sonu bozulan alıntının başı kaynakla örtüşüyorsa kabul eder."""
    if len(quote) < QUOTE_LIMIT - _CUT_MARGIN:
        return False
    normalized = form(quote)
    words = normalized.split(" ")
    for count in range(len(words) - 1, 0, -1):
        head = " ".join(words[:count])
        if contains_whole(normalized_source, head):
            tail = normalized[len(head) :]
            written_tail = _written_tail(quote, words, count)
            return len(tail) <= _CUT_MAX_TAIL and not _carries_values(tail, written_tail)
    return False


def _matches(quote: str, source: str, form: Form) -> bool:
    without_citation = CUT_CITATION_RE.sub("", quote)
    normalized_quote = form(without_citation)
    if not normalized_quote:
        return False
    normalized_source = form(source)
    return (
        contains_whole(normalized_source, normalized_quote)
        or _field_matches(without_citation, source, form)
        or _cut_prefix_matches(quote, normalized_source, form)
    )


def quote_matches(quote: str, source: str) -> bool:
    return any(_matches(quote, source, form) for form in _FORMS)
