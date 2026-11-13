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
from visual_agent.verification.quote import labeled_cells, quote_matches
from visual_agent.verification.text import (
    FOREIGN_SCRIPT_RE,
    TOLERANCE_RE,
    canonical_number,
    compact_identifier,
    contains_token,
    header_units,
    identifiers_in,
    measures_in,
    normalize,
    numbers_in,
    prefixed_codes_in,
    turkish_tens,
    word_numbers,
)

Sources = Mapping[int, PromptSource]
_MIN_WORDS_FOR_REPEAT = 4
# "bir" ve "one" çoğu zaman sayı değil, belirsiz tanımlıktır; cümlede sayı sayılmaz.
_ARTICLE_NUMBERS = {"1"}


def _quote_problems(item: ModelItem, sources: Sources) -> list[str]:
    problems = []
    for quote in item.quotes:
        source = sources.get(quote.source_no)
        if source is None or not quote_matches(quote.text, source.text, source.language):
            problems.append(f"alıntı [{quote.source_no}] kaynakta birebir değil")
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
    uncertain = []
    for quote in item.quotes:
        source = sources.get(quote.source_no)
        tokens = source.ocr_uncertain if source is not None else ()
        normalized = normalize(quote.text)
        uncertain += [token for token in tokens if contains_token(normalized, normalize(token))]
    return [f"OCR değeri belirsiz: {uncertain}"] if uncertain else []


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


def _unit_problems(
    item: ModelItem, evidence: Evidence, sources: Sources, language: str
) -> list[str]:
    """Cümlede sayının birimi alıntıda o sayıyla ya da sayının sütun başlığında yazılı olmalı."""
    allowed = {m for text, lang in evidence for m in measures_in(text, lang)}
    allowed |= _header_measures(item, sources)
    values = numbers_in(item.text)  # kodun içindeki rakam ("PNT-1126 S") değer değildir
    missing = sorted(
        f"{number} {unit}"
        for number, unit in measures_in(item.text, language)
        if number in values and (number, unit) not in allowed
    )
    return [f"cümlede kaynakta yazmayan birim: {missing}"] if missing else []


def _stray_tens(text: str, language: str, backed: set[str], evidence: Evidence) -> set[str]:
    """Cümledeki Türkçe "on" rakamla ya da aynı sözcüğün önündeki "on" ile karşılanır
    ("on dakika" <-> "on dakika"); "click on", "ON konumu" kanıt olamaz."""
    phrases = {phrase for part, lang in evidence for phrase in turkish_tens(part, lang)}
    return {
        value
        for value, following in turkish_tens(text, language)
        if value not in backed and not (following and (value, following) in phrases)
    }


def _token_problems(
    item: ModelItem, evidence: Evidence, sources: Sources, language: str
) -> list[str]:
    problems = []
    joined = " ".join(text for text, _ in evidence)
    backed = numbers_in(joined) | word_numbers(joined)
    stray_numbers = (
        (numbers_in(item.text) - backed)
        | (word_numbers(item.text) - _ARTICLE_NUMBERS - backed)
        | _stray_tens(item.text, language, backed, evidence)
    )
    if stray_numbers:
        problems.append(f"cümlede kendi alıntısında olmayan sayı: {sorted(stray_numbers)}")
    cited = [sources[q.source_no].context for q in item.quotes if q.source_no in sources]
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


def verify_item(item: ModelItem, sources: Sources, language: str) -> ItemCheck:
    """Her sayı ve teknik ad, cümlenin kendi dayanağında bulunmalıdır; language cevabın dili."""
    problems = _quote_problems(item, sources)
    code_source = _code_source(item, sources)
    if item.code_source_no is not None and code_source is None:
        problems.append(f"kod kaynağı [{item.code_source_no}] geçersiz")
    evidence = _evidence(item, sources, code_source)
    problems += _ocr_problems(item, sources)
    problems += _token_problems(item, evidence, sources, language)
    problems += _tolerance_problems(item.text, " ".join(text for text, _ in evidence))
    others = len(problems)
    problems += _unit_problems(item, evidence, sources, language)
    if FOREIGN_SCRIPT_RE.search(item.text):
        problems.append("cümlede başka alfabeden karakter")
    numbers = tuple(quote.source_no for quote in item.quotes)
    return ItemCheck(
        ok=not problems and bool(item.text.strip()),
        from_figure=_rests_on_ocr(item, sources),
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


def _has_repeated_sentence(answer: ModelAnswer) -> bool:
    long_texts = [
        text
        for text in (normalize(item.text) for item in answer.items)
        if len(text.split()) >= _MIN_WORDS_FOR_REPEAT
    ]
    return len(long_texts) != len(set(long_texts))


_SAFE_CLARIFY_QUESTION = {"tr": "Hangisi için soruyorsunuz?", "en": "Which one do you mean?"}


def _values_in(text: str, language: str) -> set[str]:
    codes = {compact_identifier(value) for value in identifiers_in(text)} | prefixed_codes_in(text)
    words = word_numbers(text) | {value for value, _ in turkish_tens(text, language)}
    numbers = numbers_in(text) | (words - _ARTICLE_NUMBERS)
    return codes | numbers


def safe_clarify_question(question: str, user_question: str, language: str) -> str:
    """Netleştirme sorusu kaynağa karşı denetlenmez; kullanıcının söylemediği sayı ya da kod
    taşıyorsa ya da boşsa yerine sabit soru gelir."""
    if question.strip() and _values_in(question, language) <= _values_in(user_question, language):
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


def _final_status(checks: tuple[ItemCheck, ...], repeated: bool) -> VerificationStatus:
    if not checks or repeated or not all(check.ok for check in checks):
        return VerificationStatus.FAILED
    if any(check.from_figure for check in checks):
        return VerificationStatus.PARTIAL
    return VerificationStatus.VERIFIED


def verify_answer(answer: ModelAnswer, sources: Sources, language: str) -> AnswerVerification:
    if answer.kind is AnswerKind.NOT_FOUND:
        return AnswerVerification(status=VerificationStatus.NOT_FOUND)
    if answer.kind is AnswerKind.CLARIFY:
        return _verify_clarification(answer, sources)
    checks = tuple(verify_item(item, sources, language) for item in answer.items)
    repeated = _has_repeated_sentence(answer)
    problems = [problem for check in checks for problem in check.problems]
    if repeated:
        problems.append("aynı cümle tekrar ediyor")
    if not checks:
        problems.append("cevap listesi boş")
    return AnswerVerification(
        status=_final_status(checks, repeated),
        items=checks,
        problems=tuple(dict.fromkeys(problems)),
    )
