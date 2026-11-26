"""Model cevabının kaynaklara karşı öğe öğe denetimi."""

import re
from collections.abc import Mapping

from visual_agent.domain.answer import (
    MIN_CLARIFY_OPTIONS,
    AnswerKind,
    AnswerVerification,
    ItemCheck,
    ModelAnswer,
    ModelItem,
    PromptSource,
    VerificationStatus,
)
from visual_agent.verification.qualifier import Qualifiers, build_qualifiers, qualifier_problems
from visual_agent.verification.quote import (
    contains_whole,
    labeled_cells,
    pieces_match,
    quote_matches,
    quote_pieces,
    starts_cell,
)
from visual_agent.verification.text import (
    FOREIGN_SCRIPT_RE,
    TOLERANCE_RE,
    canonical_number,
    compact_identifier,
    contains_token,
    header_units,
    identifiers_in,
    list_marks,
    measures_in,
    model_numbers,
    normalize,
    numbers_in,
    numbers_with_next_word,
    prefixed_codes_in,
    turkish_lower,
    turkish_tens,
    word_numbers,
)

Sources = Mapping[int, PromptSource]
_NAME_JOINERS = re.compile(r"[-_]")
ABSENCE_CLAIM = "cümle belgede olmayan bir bilgiyi iddia ediyor"
_NEGATED = r"(?:m[ae][mdy]\w*|m[ıiuü]yor\w*)"
"""Türkçe olumsuzluk eki ve ardından gelen ek: -memiş, -medi, -meyen, -miyor. Olumlu
"belirtilmiş", "belirtilmekte", ad olan "belirtilmesi" ve genel yasak bildiren geniş zaman
("izin verilmez", "yapılamaz") bu kalıba girmez."""
_ABSENCE_RE = re.compile(
    rf"\b(?:belirtil|yer\s+al|bulun|geç|tanımlan|açıklan){_NEGATED}"
    r"|\bbulunam[aı]\w*"
    r"|\bmevcut\s+değil\w*"
    r"|\b(?:bilgi|kayıt|veri|değer)\w*\s+yok\w*"
    r"|\bnot\s+(?:specified|mentioned|stated|provided|given|indicated|listed|included|found"
    r"|available|defined|documented)\b"
    r"|\b(?:does|do|did)\s+not\s+(?:specify|mention|state|provide|include|contain|indicate|list)\b"
    r"|\bno\s+(?:information|mention|data|record)\b"
    r"|\bunspecified\b"
)
"""Belgenin bir şeyi içermediğini söyleyen kalıplar (dil düzeyi, Türkçe ve İngilizce)."""
_SOURCE_TALK_RE = re.compile(
    r"\b(?:kaynak(?:lar)?[dt]a|belge(?:ler)?de|dok[uü]man(?:lar)?da)\b"
    r"|\b(?:the|this|these)\s+(?:documents?|sources?)\b"
)
"""Cümlenin belgenin içeriğini değil, belgenin kendisini anlattığını gösteren sözler."""
# "bir" ve "one" çoğu zaman sayı değil, belirsiz tanımlıktır; cümlede sayı sayılmaz.
_ARTICLE_NUMBERS = {"1"}


def _quote_problems(item: ModelItem, sources: Sources) -> list[str]:
    """Alıntı bütün hâliyle birebir eşleşir. Eşleşmezse "…" ile ayrılan parçaları (sondaki "…"
    kesik işaretidir) sırayla ve ayrı ayrı birebir eşleşebilir. Cümle birden çok parçaya
    dayanıyorsa (iki alıntı ya da "…") parçaların hepsi aynı kaynaktan olmalı ve kaynak tablo
    satırıysa her biri bir hücrenin başından başlamalı: başka satırdan ya da etiketinden
    koparılmış değerle cümle kurulamaz (kararlar, "Ayrık alıntı")."""
    problems: list[str] = []
    parts: list[tuple[PromptSource, str]] = []
    for quote in item.quotes:
        source = sources.get(quote.source_no)
        if source is not None and quote_matches(quote.text, source.text, source.language):
            parts.append((source, quote.text))
            continue
        pieces = quote_pieces(quote.text)
        if source is None or not pieces_match(pieces, source.text, source.language):
            problems.append(f"alıntı [{quote.source_no}] kaynakta birebir değil")
            continue
        parts += [(source, piece) for piece in pieces]
    if len(parts) > 1:
        if len({source.number for source, _ in parts}) > 1:
            problems.append("alıntılar farklı kaynaklardan birleştirilmiş")
        elif any(s.is_table_row and not starts_cell(piece, s.text) for s, piece in parts):
            problems.append(f"alıntı [{parts[0][0].number}] parçası hücre başında değil")
    return problems


def _code_source(item: ModelItem, sources: Sources) -> PromptSource | None:
    source = None if item.code_source_no is None else sources.get(item.code_source_no)
    return source if source is not None and source.is_code else None


def code_source_number(item: ModelItem, sources: Sources) -> int | None:
    """Komutun gösterileceği kaynak: açık referans ya da komutun tamamını kapsayan alıntı."""
    if item.code_source_no is not None:
        return item.code_source_no
    for quote in item.quotes:
        source = sources.get(quote.source_no)
        if (
            source is not None
            and source.is_code
            and normalize(quote.text) == normalize(source.text)
        ):
            return quote.source_no
    return None


def _ocr_problems(item: ModelItem, sources: Sources) -> list[str]:
    """Belirsiz okunan değer ne alıntıda ne cümlede geçebilir: satırın bağlamından ya da
    başlıktan gelen kod alıntılanmadan cümleye yazılabiliyor (satır bağlamı ve bölüm adı
    cümlenin teknik adlarına izin verir)."""
    numbers = [quote.source_no for quote in item.quotes]
    if item.code_source_no is not None:
        numbers.append(item.code_source_no)
    tokens = {
        token for number in numbers if number in sources for token in sources[number].ocr_uncertain
    }
    texts = [normalize(text) for text in (item.text, *(quote.text for quote in item.quotes))]
    uncertain = sorted(
        token for token in tokens if any(contains_token(text, normalize(token)) for text in texts)
    )
    return [f"OCR değeri belirsiz: {uncertain}"] if uncertain else []


def _absence_problems(item: ModelItem, language: str) -> list[str]:
    """Cümle belgede bir şeyin olmadığını söylüyorsa doğrulanamaz: alıntı bir şeyin var olduğunu
    gösterebilir, olmadığını gösteremez. Bu iddia yalnız "bulunamadı" olarak verilebilir.
    Kaynaklardan söz eden ve denetlenecek sayı ya da kod taşımayan cümle de aynı sınıftandır
    ("Kaynaklarda sadece kalça için bilgi var"): kaynakların neyi kapsadığını alıntı gösteremez.
    İfade kaynağın kendi sözüyse (aynı tür ifade alıntıda geçiyorsa) cümle geçer."""
    text = turkish_lower(item.text)
    quotes = [turkish_lower(quote.text) for quote in item.quotes]
    patterns = [_ABSENCE_RE] + ([] if _values_in(item.text, language) else [_SOURCE_TALK_RE])
    for pattern in patterns:
        if pattern.search(text) and not any(pattern.search(quote) for quote in quotes):
            return [ABSENCE_CLAIM]
    return []


def _tolerance_problems(text: str, evidence: str) -> list[str]:
    problems = []
    flat = re.sub(r"\s+", "", text).replace(",", ".").lower()
    for match in TOLERANCE_RE.finditer(evidence):
        value, tolerance = canonical_number(match.group(1)), canonical_number(match.group(2))
        if value in numbers_in(text) and f"±{tolerance}" not in flat:
            problems.append(f"tolerans düşmüş: {match.group(0)}")
    return problems


# Dayanak parçaları: (metin, belgenin dili). Yazıyla sayı ve birim, parçanın kendi diliyle okunur.
Evidence = list[tuple[str, str]]


def _evidence(item: ModelItem, sources: Sources, code_source: PromptSource | None) -> Evidence:
    parts = [(q.text, sources[q.source_no].language) for q in item.quotes if q.source_no in sources]
    return parts + ([(code_source.text, code_source.language)] if code_source else [])


def _row_measures(line: str, language: str) -> set[tuple[str, str]]:
    """Hücrenin sütun başlığındaki birim o hücreye, satırın ilk hücresindeki birim ("Tork (Nm)",
    devrik tablo) o satırın bütün değerlerine sayılır; başka sütunun başlığı sayılmaz."""
    row_units = header_units(line.split("|", 1)[0], language) if "|" in line else set()
    return {
        (number, unit)
        for label, value in labeled_cells(line)
        for number in numbers_in(value)
        for unit in header_units(label, language) | row_units
    }


def _header_measures(item: ModelItem, sources: Sources) -> set[tuple[str, str]]:
    """Alıntıda ya da alıntıyı içeren kaynak satırında başlığından birim alan değerler."""
    found: set[tuple[str, str]] = set()
    for quote in item.quotes:
        source, wanted = sources.get(quote.source_no), normalize(quote.text)
        if source is None:
            continue
        lines = [line for line in source.text.splitlines() if wanted in normalize(line)]
        for line in [quote.text, *lines]:
            found |= _row_measures(line, source.language)
    return found


def _unit_problems(item: ModelItem, evidence: Evidence, sources: Sources) -> list[str]:
    """Cümlede sayının birimi alıntıda o sayıyla ya da sayının sütun başlığında yazılı olmalı."""
    allowed = {m for text, lang in evidence for m in measures_in(text, lang)}
    allowed |= _header_measures(item, sources)
    values = numbers_in(item.text)  # kodun içindeki rakam ("PNT-1126 S") değer değildir
    missing = sorted(
        f"{number} {unit}"
        for number, unit in measures_in(item.text, "")  # cümlede birim yazıldığı gibi
        if number in values and (number, unit) not in allowed
    )
    return [f"cümlede kaynakta yazmayan birim: {missing}"] if missing else []


def _stray_tens(text: str, language: str, backed: set[str], evidence: Evidence) -> set[str]:
    """Cümledeki Türkçe "on", dayanakta aynı sözcüğün önündeki "on" ya da 10 ile karşılanır
    ("on dakika" <-> "10 dakika"). "click on", "ON konumu", "10 mm" kanıt olamaz; "on beş"
    "10 adet ... beş" ile karşılanmaz. Ardında sözcük yoksa ("Süre on.") yalnız 10 aranır."""
    phrases = {phrase for part, lang in evidence for phrase in turkish_tens(part, lang)}
    phrases |= {phrase for part, _ in evidence for phrase in numbers_with_next_word(part)}
    return {
        value
        for value, following in turkish_tens(text, language)
        if ((value, following) not in phrases if following else value not in backed)
    }


def _asked_model_numbers(item: ModelItem, sources: Sources, user: str) -> set[str]:
    """Alıntılanan kaynağın belge adındaki model numarası ("6029322"), kullanıcı da söylediyse
    cümlede alıntısız geçebilir: değer değil, hangi belgeden söz edildiğidir.

    Yalnız adın tire ya da alt çizgiyle ayrılmış ilk parçası numaranın kendisiyse sayılır
    ("6029322-SS27-..."). Adın başka yerindeki sayı ("Klima-12000-BTU", "Sipariş-45000",
    "Klima 12000 BTU") bir değer olabilir. Başka belgenin numarası ya da kullanıcının
    söylemediği numara yine reddedilir."""
    titles = (sources[q.source_no].title for q in item.quotes if q.source_no in sources)
    heads = {_first_name_part(title) for title in titles}
    return {head for head in heads if head and model_numbers(head) == {head}} & numbers_in(user)


def _asked_cell_labels(item: ModelItem, sources: Sources, user: str) -> set[str]:
    """Alıntılanan tablo hücresinin başlığındaki sayı (varyant adı: renk yolu "001", sayısal beden
    "38"), kullanıcı da söylediyse cümlede alıntısız geçebilir: değer değil, hangi sütundan söz
    edildiğidir. Tutucu: her alıntı kaynağın tablo satırlarında tek bir hücrenin değerinde bütün
    sayı olarak geçmeli, bütün alıntılar aynı hücreye çıkmalı ve alıntılanan değer cümlede de
    yazılı olmalı (başlık sayısı değerin yerine yazılamaz). Aksi hâlde muafiyet yoktur."""
    sentence = normalize(item.text)
    cells: set[str] = set()
    for quote in item.quotes:
        source, wanted = sources.get(quote.source_no), normalize(quote.text)
        if source is None or not wanted or not contains_whole(sentence, wanted):
            return set()
        labels = [
            label
            for line in source.text.splitlines()
            if source.is_table_row or "|" in line
            for label, value in labeled_cells(line, last=True)
            if contains_whole(normalize(value), wanted)
        ]
        if len(labels) != 1:
            return set()
        cells.add(labels[0])
    return numbers_in(cells.pop()) & numbers_in(user) if len(cells) == 1 else set()


def _first_name_part(title: str) -> str:
    """Adın ilk tire ya da alt çizgisinden önceki parçası; ayraç yoksa boş."""
    joiner = _NAME_JOINERS.search(title)
    return title[: joiner.start()].strip() if joiner else ""


def _token_problems(
    item: ModelItem, evidence: Evidence, sources: Sources, language: str, user: str = ""
) -> list[str]:
    """user: kullanıcının kendi metni (bu turun sorusu ve önceki turun denetlenmiş sözcükleri)."""
    problems = []
    joined = " ".join(text for text, _ in evidence)
    backed = numbers_in(joined) | word_numbers(joined)
    backed |= _asked_model_numbers(item, sources, user) | _asked_cell_labels(item, sources, user)
    # Cümle başındaki "30. Gün" de değerdir; kaynağın liste numarası yalnız aynı numarayı aynı
    # sözcükle karşılar ("2. Bekleyin" adımı "2. Gün"ü karşılamaz).
    source_marks = list_marks(joined)
    listed = {n for n, w in list_marks(item.text) if n not in backed and (n, w) not in source_marks}
    stray_numbers = (
        (numbers_in(item.text) - backed)
        | listed
        | (word_numbers(item.text) - _ARTICLE_NUMBERS - backed)
        | _stray_tens(item.text, language, backed, evidence)
    )
    if stray_numbers:
        problems.append(f"cümlede kendi alıntısında olmayan sayı: {sorted(stray_numbers)}")
    # Alıntılanan tablo satırının kodu cümlede geçebilir: model değeri ("LG: 25") alıntılayıp
    # satırın kodunu (BW005) yazar. Başka satırın ya da kaynağın kodu yine reddedilir.
    cited = [
        f"{source.context} {source.text}" if source.is_table_row else source.context
        for source in (sources[q.source_no] for q in item.quotes if q.source_no in sources)
    ]
    allowed = {compact_identifier(value) for value in identifiers_in(" ".join([joined, *cited]))}
    stray_identifiers = {
        value for value in identifiers_in(item.text) if compact_identifier(value) not in allowed
    }
    if stray_identifiers:
        problems.append(f"cümlede kaynakta olmayan teknik ad: {sorted(stray_identifiers)}")
    stray_codes = prefixed_codes_in(item.text) - prefixed_codes_in(" ".join([joined, *cited]))
    if stray_codes:
        problems.append(f"cümlede kaynakta olmayan kod: {sorted(stray_codes)}")
    return problems


def _rests_on_ocr(item: ModelItem, sources: Sources) -> bool:
    """OCR ile okunan kaynaklar birebir teyit edilemez; cevap kısmi doğrulanmış sayılır."""
    numbers = [quote.source_no for quote in item.quotes]
    if item.code_source_no is not None:
        numbers.append(item.code_source_no)
    return any(number in sources and sources[number].from_ocr for number in numbers)


def verify_item(
    item: ModelItem, sources: Sources, language: str, qualifiers: Qualifiers | None = None
) -> ItemCheck:
    """Her sayı ve teknik ad, cümlenin kendi dayanağında bulunmalıdır; language cevabın dili.

    qualifiers cevap başına bir kez hesaplanır (kullanıcının sorusuyla); verilmezse soru
    bilinmiyor sayılır ve varyant adı yalnız cümlede aranır."""
    if qualifiers is None:
        qualifiers = build_qualifiers(sources, asked="")
    problems = _quote_problems(item, sources)
    code_source = _code_source(item, sources)
    if item.code_source_no is not None and code_source is None:
        problems.append(f"kod kaynağı [{item.code_source_no}] geçersiz")
    evidence = _evidence(item, sources, code_source)
    problems += _ocr_problems(item, sources)
    user = f"{qualifiers.asked} {qualifiers.previous}"
    problems += _token_problems(item, evidence, sources, language, user)
    problems += _tolerance_problems(item.text, " ".join(text for text, _ in evidence))
    problems += _absence_problems(item, language)
    problems += qualifier_problems(item, sources, qualifiers)
    others = len(problems)
    problems += _unit_problems(item, evidence, sources)
    if FOREIGN_SCRIPT_RE.search(item.text):
        problems.append("cümlede başka alfabeden karakter")
    numbers = tuple(quote.source_no for quote in item.quotes)
    return ItemCheck(
        ok=not problems and bool(item.text.strip()),
        from_ocr=_rests_on_ocr(item, sources),
        problems=tuple(problems),
        source_numbers=numbers
        + ((item.code_source_no,) if item.code_source_no is not None else ()),
        quote=_unit_only_quote(item, problems, others),
    )


def _unit_only_quote(item: ModelItem, problems: list[str], others: int) -> str | None:
    """Tek sorun kaynakta yazmayan birimse cümle yerine gösterilecek doğrulanmış alıntı.

    Başka sorunu olan ya da alıntısı olmayan cümle için None: cümle eskisi gibi gizlenir.
    """
    unit_only = others == 0 and len(problems) == 1 and bool(item.quotes)
    return " … ".join(quote.text for quote in item.quotes) if unit_only else None


_SAFE_CLARIFY_QUESTION = {"tr": "Hangisi için soruyorsunuz?", "en": "Which one do you mean?"}


def _values_in(text: str, language: str) -> set[str]:
    codes = {compact_identifier(value) for value in identifiers_in(text)} | prefixed_codes_in(text)
    words = word_numbers(text) | {value for value, _ in turkish_tens(text, language)}
    numbers = numbers_in(text) | (words - _ARTICLE_NUMBERS)
    return codes | numbers


def safe_clarify_question(question: str, user_question: str, language: str) -> str:
    """Netleştirme sorusu kaynağa karşı denetlenmez; kullanıcının söylemediği sayı ya da kod
    taşıyorsa ya da boşsa yerine sabit soru gelir."""
    said = _values_in(user_question, language) | {n for n, _ in list_marks(user_question)}
    values = _values_in(question, language) | {n for n, _ in list_marks(question)}
    if question.strip() and values <= said:
        return question
    return _SAFE_CLARIFY_QUESTION.get(language, _SAFE_CLARIFY_QUESTION["tr"])


def _verify_clarification(answer: ModelAnswer, sources: Sources) -> AnswerVerification:
    options = answer.clarify.options if answer.clarify else ()
    valid = tuple(dict.fromkeys(o.source_no for o in options if o.source_no in sources))
    if len(valid) < MIN_CLARIFY_OPTIONS or any(o.source_no not in sources for o in options):
        return AnswerVerification(
            status=VerificationStatus.FAILED, problems=("netleştirme seçenekleri geçersiz",)
        )
    return AnswerVerification(status=VerificationStatus.CLARIFY, clarify_options=valid)


def _final_status(checks: tuple[ItemCheck, ...]) -> VerificationStatus:
    if not checks or not all(check.ok for check in checks):
        return VerificationStatus.FAILED
    if any(check.from_ocr for check in checks):
        return VerificationStatus.PARTIAL
    return VerificationStatus.VERIFIED


def verify_answer(
    answer: ModelAnswer, sources: Sources, language: str, asked: str = "", previous: str = ""
) -> AnswerVerification:
    """asked: kullanıcının bu turdaki sorusu; previous: önceki turun doğrulanmış sözcükleri."""
    if answer.kind is AnswerKind.NOT_FOUND:
        return AnswerVerification(status=VerificationStatus.NOT_FOUND)
    if answer.kind is AnswerKind.CLARIFY:
        return _verify_clarification(answer, sources)
    qualifiers = build_qualifiers(sources, asked, previous)
    checks = tuple(verify_item(item, sources, language, qualifiers) for item in answer.items)
    problems = [problem for check in checks for problem in check.problems]
    if not checks:
        problems.append("cevap listesi boş")
    return AnswerVerification(
        status=_final_status(checks),
        items=checks,
        problems=tuple(dict.fromkeys(problems)),
    )
