"""Kod ve teknik adların tam eşleşme indeksi: taramasız arama."""

import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from visual_agent.domain.document import Chunk
from visual_agent.verification.text import compact_identifier, identifiers_in

_SPOKEN_CODE_RE = re.compile(r"(?<!\w)[^\W\d_]{1,6}[-_\s]?\d+(?!\w)")
_SUFFIX_RE = re.compile(r"['’]\w+")
_WORD_RE = re.compile(r"[^\W_]+")
_MIN_PHRASE_WORDS = 2
_MAX_PHRASE_WORDS = 8
_MIN_PAGES = 2


def _words(text: str) -> list[str]:
    """Küçük harfli sözcükler; kesmeyle bağlanan ek ayrılır ("Pant'ın" -> "pant"). Türkçe I/ı
    i'ye katlanır: büyük harfli başlık ("KIRMIZI") ile soru ("kırmızı") aynı yazılır."""
    lowered = _SUFFIX_RE.sub("", text.replace("İ", "i").lower())
    return _WORD_RE.findall(lowered.replace("ı", "i"))


def _on_most_pages(phrase: str, pages: Sequence[str]) -> bool:
    """Sayfaların yarısından fazlasında geçiyor; sonuç belli olunca sayım durur."""
    needed, found = len(pages) // 2 + 1, 0
    for index, page in enumerate(pages):
        found += f" {phrase} " in page
        if found >= needed:
            return True
        if found + len(pages) - index - 1 < needed:
            return False
    return False


def _phrase_re(phrase: str) -> re.Pattern[str]:
    """Öbeğin metindeki yazılışı: sözcükler arasında boşluk ya da noktalama, sonda kesmeli ek."""
    gap = r"(?:['’]\w+)?[\W_]+"
    body = gap.join(re.escape(word) for word in phrase.split())
    return re.compile(rf"(?<![^\W_]){body}(?:['’]\w+)?(?![^\W_])", re.IGNORECASE)


Posting = tuple[str, str]


@dataclass(frozen=True)
class IdentifierIndex:
    _postings: dict[str, tuple[Posting, ...]]
    _chunks: dict[str, Chunk]
    _aliases: dict[str, tuple[str, ...]]
    _in_text: frozenset[tuple[str, str]]
    """(parça, kod): kod parçanın kendi metninde geçiyor; başlıkta ya da bölüm adında değil."""
    _pages: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Belge başına sayfa metinleri (küçük harfli sözcükler, başta ve sonda boşluk)."""

    def _postings_of(self, identifier: str) -> tuple[Posting, ...]:
        keys = self._aliases.get(compact_identifier(identifier), ())
        return tuple(dict.fromkeys(posting for key in keys for posting in self._postings[key]))

    def lookup(self, identifier: str, doc_ids: Sequence[str] | None = None) -> tuple[str, ...]:
        return tuple(
            chunk_id
            for doc_id, chunk_id in self._postings_of(identifier)
            if doc_ids is None or doc_id in doc_ids
        )

    def chunks_naming(self, identifier: str, doc_ids: Sequence[str]) -> tuple[Chunk, ...]:
        """Kodu kendi metninde taşıyan parçalar; yazım farkı (boşluk, tire, büyük harf) sayılmaz."""
        keys = self._aliases.get(compact_identifier(identifier), ())
        return tuple(
            dict.fromkeys(
                self._chunks[chunk_id]
                for key in keys
                for doc_id, chunk_id in self._postings[key]
                if doc_id in doc_ids and (chunk_id, key) in self._in_text
            )
        )

    def chunk(self, chunk_id: str) -> Chunk | None:
        return self._chunks.get(chunk_id)

    def documents_with(self, identifier: str) -> tuple[str, ...]:
        return tuple(dict.fromkeys(doc_id for doc_id, _ in self._postings_of(identifier)))

    def codes_in_speech(self, text: str) -> set[str]:
        """Yazıya çevirmede tiresi düşmüş ya da küçülmüş kodlar; yalnız belgede olanlar sayılır."""
        candidates = (compact_identifier(m.group(0)) for m in _SPOKEN_CODE_RE.finditer(text))
        return {self._aliases[key][0] for key in candidates if key in self._aliases}

    def without_repeated_phrases(self, text: str, doc_id: str) -> str:
        """Belgenin sayfalarının yarısından fazlasında aynen geçen, en az iki sözcüklü öbekler
        (sayfa üst bilgisi, ürün adı: "Challenger Train Pant") metinden çıkar; en uzun öbek
        önce. Belge içinde ayırt edici değillerdir, koleksiyon IDF'i yüzünden aramayı her
        sayfanın başlık satırına çekerler. Öbek metinde her geçtiği yerden çıkar. Metin boş
        kalırsa olduğu gibi döner.

        Öbek en çok 8 sözcük; bir öbek ancak iki alt öbeği de sıksa denenir (sık olmayan öbeğin
        uzantısı da sık olamaz). Uzun soruda bile sayfa araması sözcük sayısıyla doğrusal kalır."""
        pages = self._pages.get(doc_id, ())
        if len(pages) < _MIN_PAGES:
            return text
        words = _words(text)
        frequent: dict[int, set[int]] = {1: set(range(len(words)))}
        for size in range(_MIN_PHRASE_WORDS, min(len(words), _MAX_PHRASE_WORDS) + 1):
            shorter = frequent[size - 1]
            frequent[size] = {
                start
                for start in range(len(words) - size + 1)
                if start in shorter
                and start + 1 in shorter
                and _on_most_pages(" ".join(words[start : start + size]), pages)
            }
            if not frequent[size]:
                break
        used = [False] * len(words)
        stripped = text
        for size in sorted((s for s in frequent if s >= _MIN_PHRASE_WORDS), reverse=True):
            for start in sorted(frequent[size]):
                if any(used[start : start + size]):
                    continue
                used[start : start + size] = [True] * size
                stripped = _phrase_re(" ".join(words[start : start + size])).sub(" ", stripped)
        stripped = " ".join(stripped.split())
        return stripped if _WORD_RE.search(stripped) else text

    def codes_of(self, doc_id: str) -> tuple[str, ...]:
        """Belgedeki kodlar; sütun ve tablo adları kod sayılmaz."""
        codes = (
            identifier
            for identifier, postings in self._postings.items()
            if any(c.isdigit() for c in identifier) and any(d == doc_id for d, _ in postings)
        )
        return tuple(sorted(code.upper() for code in codes))


def build_identifier_index(chunks: Iterable[Chunk]) -> IdentifierIndex:
    postings: defaultdict[str, list[Posting]] = defaultdict(list)
    by_id: dict[str, Chunk] = {}
    in_text: set[tuple[str, str]] = set()
    pages: defaultdict[str, defaultdict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    for chunk in chunks:
        by_id[chunk.chunk_id] = chunk
        if chunk.location.page is not None:
            pages[chunk.doc_id][chunk.location.page].append(" ".join(_words(chunk.text)))
        written = {compact_identifier(code) for code in identifiers_in(chunk.text)}
        written |= {compact_identifier(m.group(0)) for m in _SPOKEN_CODE_RE.finditer(chunk.text)}
        for identifier in identifiers_in(chunk.embed_text):
            postings[identifier].append((chunk.doc_id, chunk.chunk_id))
            if compact_identifier(identifier) in written:
                in_text.add((chunk.chunk_id, identifier))
    aliases: defaultdict[str, list[str]] = defaultdict(list)
    for identifier in sorted(postings):
        aliases[compact_identifier(identifier)].append(identifier)
    return IdentifierIndex(
        {key: tuple(value) for key, value in postings.items()},
        by_id,
        {key: tuple(value) for key, value in aliases.items()},
        frozenset(in_text),
        {
            doc_id: tuple(f" {' '.join(texts)} " for texts in by_page.values())
            for doc_id, by_page in pages.items()
        },
    )
