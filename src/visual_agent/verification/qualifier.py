"""Niteleyici denetimi: cümledeki ad ve varyant, değerin kendi satırıyla eşleşmeli.

Kural A: kaynakların tablo satırlarındaki çok sözcüklü bir ad ("Chart Size Range", "Black //
Blue Haze") cümlede geçiyorsa cümlenin alıntı yaptığı kaynağın metninde de geçmeli; başka
kaynağın adı bir değere yapıştırılamaz. Yalnız parçanın metni sayılır; bölüm yolu sayılmaz
(yanlış iç içe olabilir). Düz yazı satırları ad kaynağı değildir.

Kural B: alıntılanan değer bir varyant sütununun altındaysa (beden, renk yolu) o sütunun adı
cümlede ya da kullanıcının kendi sorusunda geçmeli; değer bütün varyantlarda aynıysa gerekmez.
Varyant sütunu: aynı satırda aynı gruptan en az iki etiket ve aynı türde değer. Grup: kaynakta
büyük harfle yazılmış kısa kod ("S", "XL", "4XLT"), son sözcüğü böyle kod olan ortak başlı ad
("Beden S", "Beden M"), rakamlı ad ("100: White // Venom Red", "Seviye 2"), değeri de sayı olan
salt sayısal etiket ("38: 72,0", "40: 74,0"; yıl sütunları "2024: 120" da böyledir).
Kaynaklardan birinin başlık satırında birden çok geçen numaralı ad da, satırda tek kalsa
varyanttır. Yapısı anlaşılmayan satır (başlıksız) bu kuralın dışında kalır.

Kural C (hücre eşleşmesi): alıntı birden çok rakamlı hücre taşıyorsa ve cümle bunlardan birinin
adını anıp kendi değerini söylemeden başka hücrenin değerini söylüyorsa cümle gizlenir
("38: 72,0 | 40: 74,0" alıntısıyla "40 beden 72,0"). Varyant ya da öznitelik ayrımı yapılmaz;
adı anılmayan cümleyi bu kural etkilemez. Rakamsız değer ("Ebat: İç paça", "Beden: S") addır.

Kural D (tek varyantlı satır): tablo satırında tam bir rakamlı adlı hücre varsa ("100: White //
Racer Red: White 100") satır o varyanta özgüdür. Cümle bu satıra dayanıyorsa varyant hücresi de
alıntılanmalı; satırın KENDİ varyant adı ("White // Racer Red") cümlede ya da kullanıcının
sorusunda geçiyorsa gerekmez. Birden çok varyant hücreli satır bu kuralın dışında.

Kural E (önekli etiket): aynı belgenin kaynaklarında hem "L" hem "P L" etiketli hücre varsa
("Size Range" ve "Chart Size Range") ve değerleri farklıysa, cümle "P L" hücresinin değerini
söylüyorsa cümlede ya da kullanıcının bu turdaki sorusunda P ("Chart") ya da tam etiket geçmeli;
yoksa önekli etiketin değeri öneksiz etiket diye sunulmuştur ve cümle gizlenir. Yalnız tablo
hücresi etiketleri ("Etiket: değer" ya da form satırında etiket | değer); hücre değeri sayılmaz.

Kurallar cümleyi yeniden yazmaz: geçemeyen cümle gizlenir.
"""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache

from visual_agent.domain.answer import ModelItem, PromptSource
from visual_agent.verification.quote import labeled_cells, quote_pieces
from visual_agent.verification.text import (
    canonical_number,
    identifiers_in,
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
    elif label.isdigit() and _value_kind(value) == _SAME_VALUE:
        # Sayısal beden ya da yıl sütunu ("38: 72,0", "2024: 120"): değerin hangi sütundan
        # geldiği söylenmeli (karar 0019, Kural C'nin 1. sınırı). Değeri sayı olmayan hücre
        # ("001: Black // White") numaralı addır; onu başlık satırı kuralı görür.
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


_VARIANT_LABEL_RE = re.compile(r"\d+\s*:\s*(?P<name>.*[^\W\d_].*)")


def _single_variant(source: PromptSource) -> str | None:
    """Kural D: tablo satırındaki tek rakamlı adlı hücrenin etiketi ("100: White // Racer Red")."""
    if not source.is_table_row:
        return None
    labels = [
        label
        for label, _ in labeled_cells(source.text, last=True)
        if _VARIANT_LABEL_RE.fullmatch(label)
    ]
    return labels[0] if len(labels) == 1 else None


def _names_own(text: str, name: str, qualifiers: Qualifiers) -> bool:
    """Ad metinde kendi başına geçiyor: onu içeren daha uzun bir kaynak adının ("Off White")
    parçası olarak geçmesi sayılmaz."""
    for longer, pattern in qualifiers.names:
        if len(longer) > len(name) and _mentions(longer, name):
            text = pattern.sub(lambda m: " " * len(m.group(0)), text)
    return _mentions(text, name)


def _unquoted_variants(
    item: ModelItem, sources: Mapping[int, PromptSource], qualifiers: Qualifiers
) -> list[str]:
    """Muafiyet yalnız bu cümle ve bu turun sorusuyla: önceki turun adı ("White") bu turda başka
    varyant sorulunca ("peki City Khaki?") geçersiz olurdu; önceki tur hiç sayılmaz."""
    sentence, asked = _norm(item.text), qualifiers.asked
    missing = []
    for number in dict.fromkeys(q.source_no for q in item.quotes):
        label = _single_variant(sources[number]) if number in sources else None
        match = _VARIANT_LABEL_RE.fullmatch(label) if label else None
        if label is None or match is None:
            continue
        quoted = " ".join(
            _norm(piece)
            for q in item.quotes
            if q.source_no == number
            for piece in quote_pieces(q.text)
        )
        name = _norm(match["name"])
        if (
            _norm(label) in quoted
            or _names_own(sentence, name, qualifiers)
            or _names_own(asked, name, qualifiers)
        ):
            continue
        missing.append(label)
    return missing


_MAX_LABEL_WORDS = 6


def _label_pairs(line: str) -> list[tuple[str, str]]:
    """Tablo satırının (etiket, değer) çiftleri: "Etiket: değer" hücreleri, yoksa form satırı
    ("Sub Category | Sportstyle | Size Range | XS-4XL"): sıradaki hücre etiket, ardından değer.
    Etiket rakamsız ve kısadır."""
    pairs = labeled_cells(line) or [
        (cells[index], cells[index + 1])
        for cells in [[cell.strip() for cell in line.split(_CELL_SEPARATOR)]]
        for index in range(0, len(cells) - 1, 2)
    ]
    return [
        (_norm(label), value)
        for label, value in pairs
        if _has_letter(label)
        and not _has_digit(label)
        and len(label.split()) <= _MAX_LABEL_WORDS
        and value.strip()
    ]


def _value_said(value: str, sentence: str) -> bool:
    """Cümle hücrenin değerini söylüyor: değerin tamamı, içindeki bir kod ("XS-5XL") ya da
    bütün sayıları."""
    numbers = numbers_in(value)
    return (
        _mentions(sentence, _norm(value))
        or any(_mentions(sentence, _norm(code)) for code in identifiers_in(value))
        or (bool(numbers) and numbers <= numbers_in(sentence))
    )


def _prefixed_label_values(
    item: ModelItem, sources: Mapping[int, PromptSource], qualifiers: Qualifiers
) -> list[str]:
    """Kural E: cümlenin söylediği değer önekli bir etiketin ("Chart Size Range") hücresinden
    geliyor, aynı belgede öneksiz etiket ("Size Range") başka değerle duruyor ve cümle de soru
    da öneki anmıyor."""
    sentence, asked = _norm(item.text), qualifiers.asked
    found: list[str] = []
    for quote in item.quotes:
        source = sources.get(quote.source_no)
        if source is None or not source.is_table_row:
            continue
        same_document = [s for s in sources.values() if s.title == source.title and s.is_table_row]
        plain = {
            label: _norm(value)
            for other in same_document
            for line in other.text.splitlines()
            for label, value in _label_pairs(line)
        }
        quoted = _norm(quote.text)
        for line in source.text.splitlines():
            for label, value in _label_pairs(line):
                words = label.split()
                shorter = [" ".join(words[k:]) for k in range(1, len(words))]
                base = next((s for s in shorter if s in plain and plain[s] != _norm(value)), None)
                if base is None or label not in quoted or not _value_said(value, sentence):
                    continue
                prefix = " ".join(words[: len(words) - len(base.split())])
                if not any(
                    _mentions(text, name) for text in (sentence, asked) for name in (prefix, label)
                ):
                    found.append(label)
    return sorted(set(found))


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
    # Ayrık alıntı ("…") parçalarına açılır: Kural B parçaları satırda arar, Kural C hücreleri
    # parçalardan yeniden kurar (parçalar tablo satırında hücre başından başlar).
    pieces = [quote_pieces(quote.text) or [quote.text] for quote in item.quotes]
    quotes = [_norm(piece) for parts in pieces for piece in parts]
    missing = _missing_variants(sentence, quotes, cited, qualifiers)
    if missing:
        problems.append(f"cümlede değerin varyantı yok: {missing}")
    misplaced = _misplaced_values(sentence, [" | ".join(parts) for parts in pieces])
    if misplaced:
        problems.append(f"cümlede adı geçen hücrenin değeri değil: {misplaced}")
    unquoted = _unquoted_variants(item, sources, qualifiers)
    if unquoted:
        problems.append(f"satır tek bir varyanta ait, varyant hücresi alıntıda değil: {unquoted}")
    prefixed = _prefixed_label_values(item, sources, qualifiers)
    if prefixed:
        problems.append(f"önekli etiketin değeri öneksiz etiket diye sunulmuş: {prefixed}")
    return problems
