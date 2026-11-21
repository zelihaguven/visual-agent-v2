"""Niteleyici denetimi: cümledeki ad ve varyant, değerin kendi satırıyla eşleşmeli.

Kural A: kaynakların tablo satırlarındaki çok sözcüklü bir ad ("Chart Size Range", "Black //
Blue Haze") cümlede geçiyorsa cümlenin alıntı yaptığı kaynağın metninde de geçmeli; başka
kaynağın adı bir değere yapıştırılamaz. Yalnız parçanın metni sayılır; bölüm yolu sayılmaz
(yanlış iç içe olabilir). Düz yazı satırları ad kaynağı değildir.

Kural B: alıntılanan değer bir varyant sütununun altındaysa (beden, renk yolu) o sütunun adı
cümlede ya da kullanıcının kendi sorusunda geçmeli; değer bütün varyantlarda aynıysa gerekmez.
Varyant sütunu: aynı satırda aynı gruptan en az iki etiket ve aynı türde değer. Grup: kaynakta
büyük harfle yazılmış kısa kod ("S", "XL", "4XLT"), son sözcüğü böyle kod olan ortak başlı ad
("Beden S", "Beden M"), rakamlı ad ("100: White // Venom Red", "Seviye 2"), salt sayısal etiket
("38", "40"; yıl sütunları "2024", "2025" da böyledir). Kaynaklardan birinin başlık satırında
birden çok geçen numaralı ad da, satırda tek kalsa varyanttır. Yapısı anlaşılmayan satır
(başlıksız) bu kuralın dışında kalır.

Kural C (hücre eşleşmesi): alıntı birden çok rakamlı hücre taşıyorsa ve cümle bunlardan birinin
adını anıp kendi değerini söylemeden başka hücrenin değerini söylüyorsa cümle gizlenir
("38: 72,0 | 40: 74,0" alıntısıyla "40 beden 72,0"). Varyant ya da öznitelik ayrımı yapılmaz;
adı anılmayan cümleyi bu kural etkilemez. Rakamsız değer ("Ebat: İç paça", "Beden: S") addır.

Kurallar cümleyi yeniden yazmaz: geçemeyen cümle gizlenir.
"""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache

from visual_agent.domain.answer import ModelItem, PromptSource
from visual_agent.verification.quote import labeled_cells
from visual_agent.verification.text import (
    canonical_number,
    normalize,
    numbers_in,
    turkish_lower,
)

_CELL_SEPARATOR = "|"
_NUMBER_SEPARATOR = ":"
_MIN_NAME_WORDS = 2
_CODE_RE = re.compile(r"[A-ZÇĞİÖŞÜ0-9]{1,4}")
_NUMERIC_VALUE_RE = re.compile(r"[\d\s.,:/+\-−]+")
_SLASHES_RE = re.compile(r"\s*(?:/\s*)+")
_SAME_VALUE = "sayı"
_NUMERIC_LABEL = "sayısal etiket"


def _norm(text: str) -> str:
    """Türkçe büyük-küçük harf ve ı/i farkı yok; "/ /", "//", " / " aynı."""
    return _SLASHES_RE.sub("/", normalize(turkish_lower(text, merge_dotless_i=True)))


@lru_cache(maxsize=4096)
def _pattern(name: str) -> re.Pattern[str]:
    """Sözcük sınırıyla: "m" "m.code" ya da "smt-4xlt" içinde eşleşmez; cümle sonu noktası olur."""
    return re.compile(rf"(?<![\w./-]){re.escape(name)}(?![\w/-]|\.\w)")


def _mentions(text: str, name: str) -> bool:
    return bool(name) and _pattern(name).search(text) is not None


def _says(text: str, name: str, numeric: bool) -> bool:
    """Salt sayısal etiket ("38") metinde ayrı bir sayı olarak geçmeli: "38,5" ya da "138" onu
    söylemez, "38,0" söyler (aynı sayı). Diğer adlar sözcük sınırıyla aranır."""
    if numeric:
        return canonical_number(name) in numbers_in(text)
    return _mentions(text, name)


def _read_as_label(value: str, group: Sequence["_Column"], sentence: str) -> bool:
    """Sayısal kardeşlerde bir hücrenin değeri başka bir kardeşin etiketine eşit olabilir
    ("36: 38 | 38: 40 | 40: 42"): cümledeki "40", 40 bedenin kendi değeri (42) de cümledeyse
    değer değil etikettir ("40 beden bel 42")."""
    number = canonical_number(value)
    return any(
        column.value != value
        and canonical_number(column.label) == number
        and _occurs(column.value, sentence)
        for column in group
    )


def _without(text: str, name: str) -> str:
    return _pattern(name).sub(lambda m: " " * len(m.group(0)), text) if name else text


def _shape(text: str) -> str:
    return re.sub(r"\d+", "9", re.sub(r"[^\W\d_]+", "a", text))


def _value_kind(value: str) -> str:
    return _SAME_VALUE if _NUMERIC_VALUE_RE.fullmatch(value) else _shape(value)


def _has_digit(text: str) -> bool:
    return any(c.isdigit() for c in text)


def _has_letter(text: str) -> bool:
    return any(c.isalpha() for c in text)


def _is_code(word: str) -> bool:
    return bool(_CODE_RE.fullmatch(word)) and _has_letter(word)


def _number_parts(label: str) -> set[str]:
    """Numaralı ad: "100: white/venom red" → "100", "white/venom red"."""
    number, separator, name = label.partition(_NUMBER_SEPARATOR)
    if separator and number.strip().isdigit():
        return {number.strip(), name.strip()} - {""}
    return set()


@dataclass(frozen=True)
class _Column:
    label: str
    value: str
    key: str | None
    parts: frozenset[str]


def _column(raw_label: str, raw_value: str) -> _Column:
    """Sütunun varyant grubu ve cümlede adı sayılan parçaları; etiket kaynaktaki yazımıyla."""
    label, value = _norm(raw_label), _norm(raw_value)
    words = raw_label.split()
    parts = {label} | _number_parts(label)
    key: str | None = None
    numbered = _has_digit(label) and _has_letter(label)
    if numbered or (len(words) == 1 and _is_code(words[0])):
        key = _shape(label)
    elif len(words) > 1 and _is_code(words[-1]):
        key = _norm(" ".join(words[:-1]))
        parts.add(_norm(words[-1]))
    elif label.isdigit():
        # Sayısal beden ya da yıl sütunu ("38", "2024"): kardeşiyle aynı türde değer taşıyorsa
        # değerin hangi sütundan geldiği söylenmeli (karar 0019, Kural C'nin 1. sınırı).
        key = _NUMERIC_LABEL
    return _Column(label, value, key, frozenset(parts))


def _columns(line: str) -> list[_Column]:
    return [_column(label, value) for label, value in labeled_cells(line, last=True) if value]


def _is_table_line(line: str, source: PromptSource) -> bool:
    return source.is_table_row or _CELL_SEPARATOR in line


@dataclass(frozen=True)
class Qualifiers:
    """Cevap başına bir kez hesaplanır: kaynakların adları (en uzun önce, derlenmiş), başlık
    satırlarındaki numaralı adlar, kullanıcının bu turdaki sorusu ve önceki turdan yalnız
    kullanıcıdan geldiği denetlenmiş sözcükler."""

    names: tuple[tuple[str, re.Pattern[str]], ...]
    numbered_headers: frozenset[str]
    asked: str
    previous: str = ""


def build_qualifiers(
    sources: Mapping[int, PromptSource], asked: str, previous: str = ""
) -> Qualifiers:
    names: set[str] = set()
    headers: set[str] = set()
    for source in sources.values():
        for line in source.text.splitlines():
            if not _is_table_line(line, source):
                continue
            cells = [_norm(cell) for cell in line.split(_CELL_SEPARATOR) if cell.strip()]
            columns = _columns(line)
            # Etiketli hücrede ölçünün adı değer tarafında olabilir ("Ebat: Dış paça"); rakamsız
            # değer ad sayılır. Rakamlı değer ad değildir, sayısı sayı kuralıyla denetlenir.
            texts = {*cells, *(c.label for c in columns)}
            texts |= {c.value for c in columns if not _has_digit(c.value)}
            texts |= {part for text in set(texts) for part in _number_parts(text)}
            names |= {t for t in texts if len(t.split()) >= _MIN_NAME_WORDS and _has_letter(t)}
            numbered = [cell for cell in cells if _has_digit(cell) and _has_letter(cell)]
            shapes = [_shape(cell) for cell in numbered]
            headers |= {
                cell for cell, s in zip(numbered, shapes, strict=True) if shapes.count(s) > 1
            }
    ordered = sorted(names, key=len, reverse=True)
    return Qualifiers(
        names=tuple((name, _pattern(name)) for name in ordered),
        numbered_headers=frozenset(headers),
        asked=_norm(asked),
        previous=_norm(previous),
    )


def _foreign_names(sentence: str, own: str, qualifiers: Qualifiers) -> list[str]:
    """Cümlede en uzun eşleşen adlar; kısa ad uzun adın içindeyse ayrıca sayılmaz."""
    text, foreign = sentence, []
    for name, pattern in qualifiers.names:
        match = pattern.search(text)
        if match is None:
            continue
        text = text[: match.start()] + " " * (match.end() - match.start()) + text[match.end() :]
        if pattern.search(own) is None:
            foreign.append(name)
    return foreign


def _occurs(value: str, sentence: str) -> bool:
    numbers = numbers_in(value)
    if numbers and _value_kind(value) == _SAME_VALUE:
        return numbers <= numbers_in(sentence)
    return _mentions(sentence, value)


def _variant_groups(line: str, headers: frozenset[str]) -> list[list[_Column]]:
    """Satırdaki varyant grupları: aynı gruptan etiket ve aynı türde değer taşıyan kardeşler;
    satırda tek kalan ama başlık satırında numaralı ad olan sütun da varyanttır."""
    columns = _columns(line)
    groups: dict[tuple[str, str], list[_Column]] = {}
    for column in columns:
        if column.key is not None:
            groups.setdefault((column.key, _value_kind(column.value)), []).append(column)
    found = [group for group in groups.values() if len({c.label for c in group}) > 1]
    grouped = {column for group in found for column in group}
    return found + [[c] for c in columns if c.label in headers and c not in grouped]


def _missing_variants(
    sentence: str, quotes: Sequence[str], cited: Sequence[PromptSource], q: Qualifiers
) -> list[str]:
    missing: set[str] = set()
    for source in cited:
        for line in source.text.splitlines():
            normalized = _norm(line)
            if not any(quote and quote in normalized for quote in quotes):
                continue
            for group in _variant_groups(line, q.numbered_headers):
                if len(group) > 1 and len({c.value for c in group}) == 1:
                    continue  # bütün varyantlarda aynı değer
                # Bu turun sorusu gruptan bir ad söylüyorsa ("peki M?") önceki turun o gruptaki
                # adı ("L") geçersizdir; söylemiyorsa ("peki kalça?") önceki tur geçerlidir.
                # Başlıktan gelen tek sütunlu grupta kardeşler başlık satırındadır.
                shapes = {_shape(c.label) for c in group}
                siblings = {h for h in q.numbered_headers if _shape(h) in shapes}
                names = {p for c in group for p in c.parts}
                names |= {p for h in siblings for p in {h} | _number_parts(h)}
                numeric = group[0].key == _NUMERIC_LABEL
                renamed = any(_says(q.asked, name, numeric) for name in names)
                asked = (q.asked,) if renamed else (q.asked, q.previous)
                for value in {c.value for c in group if _occurs(c.value, sentence)}:
                    if numeric and _read_as_label(value, group, sentence):
                        continue
                    # Değerin kendisi ad sayılmaz: "Black 001"deki 001 renk yolunu söylemez.
                    rest = _without(sentence, value)
                    owners = [c for c in group if c.value == value]
                    named = any(
                        _says(text, part, numeric)
                        for column in owners
                        for part in column.parts
                        for text in (rest, *asked)
                    )
                    if not named:
                        missing.update(c.label for c in owners)
    return sorted(missing)


def _misplaced_values(sentence: str, quotes: Sequence[str]) -> list[str]:
    """Kural C: cümle bir değer hücresinin adını anıp o hücrenin değerini söylemiyor, alıntının
    başka hücresinin değerini söylüyorsa o değerler (çok hücreli alıntılarda).

    Yalnız değeri rakamlı hücre "adı anılan" sayılır: "Beden: S | Etiket kodu: ETK-6154"
    satırında "S beden" bir anahtardır, değer hücresi değil. Adı anılan hücrenin kendi değeri de
    cümledeyse başka hücrenin değeri yan bilgidir ("M beden 40,0, tolerans 1,0")."""
    misplaced: list[str] = []
    for quote in quotes:
        cells = [c for c in _columns(quote) if _has_digit(c.value)]
        if len(cells) < 2:
            continue
        stated = [c for c in cells if _occurs(c.value, sentence)]
        rest = sentence
        for cell in stated:
            rest = _without(rest, cell.value)
        named = [c for c in cells if any(_mentions(rest, part) for part in c.parts)]
        if named and not any(c in stated for c in named):
            misplaced += [c.value for c in stated]
    return sorted(set(misplaced))


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
    misplaced = _misplaced_values(sentence, [quote.text for quote in item.quotes])
    if misplaced:
        problems.append(f"cümlede adı geçen hücrenin değeri değil: {misplaced}")
    return problems
