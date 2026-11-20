"""Niteleyici denetimi: cümledeki ad ve varyant, değerin kendi satırıyla eşleşmeli.

Kural A: kaynaklardan birinin hücre adı ("Chart Size Range", "Black // Blue Haze") cümlede
geçiyorsa cümlenin alıntı yaptığı kaynağın metninde de geçmeli; başka kaynağın adı bir değere
yapıştırılamaz. Yalnız parçanın metni sayılır; bölüm yolu sayılmaz (yanlış iç içe olabilir).

Kural B: alıntılanan değer bir varyant sütununun altındaysa (beden, renk yolu) o sütunun adı
cümlede ya da kullanıcının kendi sorusunda geçmeli; değer bütün varyantlarda aynıysa gerekmez.
Varyant sütunu: aynı satırda aynı biçimde en az iki etiket (kısa kod, numaralı ad ya da yalnız
son sözcüğü kısa kod olarak değişen ad: "Beden S", "Beden M") ve aynı türde değer; ya da
kaynaklardan birinin başlık satırında birden çok geçen numaralı ad ("100: White // Venom Red").
Yapısı anlaşılmayan satır (başlıksız) bu kuralın dışında kalır.

Kurallar cümleyi yeniden yazmaz: geçemeyen cümle gizlenir.
"""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from visual_agent.domain.answer import ModelItem, PromptSource
from visual_agent.verification.text import normalize, numbers_in, turkish_lower

_CELL_SEPARATOR = "|"
_LABEL_SEPARATOR = ":"
_SHORT_CODE_LENGTH = 4
_MIN_NAME_WORDS = 2
_NUMERIC_VALUE_RE = re.compile(r"[\d\s.,/+\-−]+")
_SLASHES_RE = re.compile(r"\s*(?:/\s*)+")
_SAME_VALUE = "sayı"

Cell = tuple[str, str]


def _norm(text: str) -> str:
    """Türkçe büyük-küçük harf ve ı/i farkı yok; "/ /", "//", " / " aynı."""
    return _SLASHES_RE.sub("/", normalize(turkish_lower(text, merge_dotless_i=True)))


def _pattern(name: str) -> re.Pattern[str]:
    """Sözcük sınırıyla: "m" "m.code" ya da "smt-4xlt" içinde eşleşmez; cümle sonu noktası olur."""
    return re.compile(rf"(?<![\w./-]){re.escape(name)}(?![\w/-]|\.\w)")


def _mentions(text: str, name: str) -> bool:
    return bool(name) and _pattern(name).search(text) is not None


def _shape(text: str) -> str:
    return re.sub(r"\d+", "9", re.sub(r"[^\W\d_]+", "a", text))


def _value_kind(value: str) -> str:
    return _SAME_VALUE if _NUMERIC_VALUE_RE.fullmatch(value) else _shape(value)


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.split(_CELL_SEPARATOR) if cell.strip()]


def _labeled(cell: str) -> Cell | None:
    """ "Etiket: değer". Etiketin kendisinde ":" olabilir ("100: White // Venom Red: Venom Red
    690"); değer son ":"ten sonrasıdır."""
    label, separator, value = cell.rpartition(_LABEL_SEPARATOR)
    if not separator or not label.strip() or not value.strip():
        return None
    return _norm(label), _norm(value)


def _name_parts(label: str) -> set[str]:
    """Adın kendisi; numaralı adın numarası ve adı ("100", "white/venom red"); son sözcüğü
    kısa kod olan adın kodu ("beden s" → "s")."""
    parts = {label}
    number, separator, name = label.partition(_LABEL_SEPARATOR)
    if separator and number.strip().isdigit():
        parts |= {number.strip(), name.strip()}
    words = label.split()
    if len(words) > 1 and len(words[-1]) <= _SHORT_CODE_LENGTH and not _has_digit(label):
        parts.add(words[-1])
    return {part for part in parts if part}


def _has_digit(text: str) -> bool:
    return any(c.isdigit() for c in text)


def _numbered(label: str) -> bool:
    return _has_digit(label) and any(c.isalpha() for c in label)


def _variant_key(label: str) -> str | None:
    """Varyant olabilecek etiketin grubu: kısa kodlar ve numaralı adlar biçimleriyle; çok
    sözcüklü adlar ortak başlarıyla ("beden s", "beden m" → "beden")."""
    if _has_digit(label):
        return _shape(label)
    words = label.split()
    if len(words) > 1:
        return " ".join(words[:-1]) if len(words[-1]) <= _SHORT_CODE_LENGTH else None
    return _shape(label) if len(label) <= _SHORT_CODE_LENGTH else None


@dataclass(frozen=True)
class Qualifiers:
    """Cevap başına bir kez hesaplanır: kaynakların adları (en uzun önce, derlenmiş), başlık
    satırlarındaki numaralı adlar ve kullanıcının kendi metni."""

    names: tuple[tuple[str, re.Pattern[str]], ...]
    numbered_headers: frozenset[str]
    asked: str


def build_qualifiers(sources: Mapping[int, PromptSource], asked: str) -> Qualifiers:
    names: set[str] = set()
    headers: set[str] = set()
    for source in sources.values():
        for line in source.text.splitlines():
            cells = [_norm(cell) for cell in _cells(line)]
            pairs = [pair for cell in _cells(line) if (pair := _labeled(cell))]
            # Etiketli hücrede ölçünün adı değer tarafında olabilir ("Ebat: Dış paça"); rakamsız
            # değer ad sayılır. Rakamlı değer ad değildir, sayısı sayı kuralıyla denetlenir.
            words = [value for _, value in pairs if not _has_digit(value)]
            for text in {*cells, *(label for label, _ in pairs), *words}:
                names |= {
                    part
                    for part in _name_parts(text)
                    if len(part.split()) >= _MIN_NAME_WORDS and any(c.isalpha() for c in part)
                }
            numbered = [cell for cell in cells if _numbered(cell)]
            shapes = [_shape(cell) for cell in numbered]
            headers |= {
                cell for cell, s in zip(numbered, shapes, strict=True) if shapes.count(s) > 1
            }
    ordered = sorted(names, key=len, reverse=True)
    return Qualifiers(
        names=tuple((name, _pattern(name)) for name in ordered),
        numbered_headers=frozenset(headers),
        asked=_norm(asked),
    )


def _foreign_names(sentence: str, own: str, qualifiers: Qualifiers) -> list[str]:
    """Cümlede en uzun eşleşen adlar; kısa ad uzun adın içindeyse ayrıca sayılmaz."""
    text, foreign = sentence, []
    for name, pattern in qualifiers.names:
        match = pattern.search(text)
        if match is None:
            continue
        text = text[: match.start()] + " " * (match.end() - match.start()) + text[match.end() :]
        if not _mentions(own, name):
            foreign.append(name)
    return foreign


def _occurs(value: str, sentence: str) -> bool:
    numbers = numbers_in(value)
    if numbers and _value_kind(value) == _SAME_VALUE:
        return numbers <= numbers_in(sentence)
    return _mentions(sentence, value)


def _variant_groups(line: str, headers: frozenset[str]) -> list[list[Cell]]:
    """Satırdaki varyant grupları: aynı gruptan etiket ve aynı türde değer taşıyan kardeşler;
    satırda tek kalan ama başlık satırında numaralı ad olan sütun da varyanttır."""
    cells = [pair for cell in _cells(line) if (pair := _labeled(cell))]
    groups: dict[tuple[str, str], list[Cell]] = {}
    for label, value in cells:
        key = _variant_key(label)
        if key is not None:
            groups.setdefault((key, _value_kind(value)), []).append((label, value))
    found = [group for group in groups.values() if len({label for label, _ in group}) > 1]
    grouped = {cell for group in found for cell in group}
    return found + [[cell] for cell in cells if cell[0] in headers and cell not in grouped]


def _missing_variants(
    sentence: str, quotes: Sequence[str], cited: Sequence[PromptSource], q: Qualifiers
) -> list[str]:
    missing: set[str] = set()
    for source in cited:
        for line in source.text.splitlines():
            if not any(quote and quote in _norm(line) for quote in quotes):
                continue
            for group in _variant_groups(line, q.numbered_headers):
                if len(group) > 1 and len({value for _, value in group}) == 1:
                    continue  # bütün varyantlarda aynı değer
                for value in {value for _, value in group if _occurs(value, sentence)}:
                    labels = [label for label, v in group if v == value]
                    named = any(
                        _mentions(text, part)
                        for label in labels
                        for part in _name_parts(label)
                        for text in (sentence, q.asked)
                    )
                    if not named:
                        missing.update(labels)
    return sorted(missing)


def qualifier_problems(
    item: ModelItem, sources: Mapping[int, PromptSource], qualifiers: Qualifiers
) -> list[str]:
    cited = [sources[q.source_no] for q in item.quotes if q.source_no in sources]
    own = " ".join(_norm(source.text) for source in cited)
    sentence = _norm(item.text)
    problems = []
    foreign = _foreign_names(sentence, own, qualifiers)
    if foreign:
        problems.append(f"cümlede alıntısının kaynağında olmayan ad: {foreign}")
    quotes = [_norm(quote.text) for quote in item.quotes]
    missing = _missing_variants(sentence, quotes, cited, qualifiers)
    if missing:
        problems.append(f"cümlede değerin varyantı yok: {missing}")
    return problems
