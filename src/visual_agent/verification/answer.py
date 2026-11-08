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
from visual_agent.verification.quote import quote_matches
from visual_agent.verification.text import (
    FOREIGN_SCRIPT_RE,
    TOLERANCE_RE,
    canonical_number,
    identifiers_in,
    normalize,
    numbers_in,
    word_numbers,
)

Sources = Mapping[int, PromptSource]
_MIN_WORDS_FOR_REPEAT = 4


def _quote_problems(item: ModelItem, sources: Sources) -> list[str]:
    problems = []
    for quote in item.quotes:
        source = sources.get(quote.source_no)
        if source is None or not quote_matches(quote.text, source.text):
            problems.append(f"alıntı [{quote.source_no}] kaynakta birebir değil")
    return problems


def _code_source(item: ModelItem, sources: Sources) -> PromptSource | None:
    source = None if item.code_source_no is None else sources.get(item.code_source_no)
    return source if source is not None and source.is_code else None


def _ocr_problems(item: ModelItem, sources: Sources) -> list[str]:
    uncertain = []
    for quote in item.quotes:
        source = sources.get(quote.source_no)
        tokens = source.ocr_uncertain if source is not None else ()
        normalized = normalize(quote.text)
        uncertain += [token for token in tokens if normalize(token) in normalized]
    return [f"OCR değeri belirsiz: {uncertain}"] if uncertain else []


def _tolerance_problems(text: str, evidence: str) -> list[str]:
    problems = []
    flat = re.sub(r"\s+", "", text).replace(",", ".").lower()
    for match in TOLERANCE_RE.finditer(evidence):
        value, tolerance = canonical_number(match.group(1)), canonical_number(match.group(2))
        if value in numbers_in(text) and f"±{tolerance}" not in flat:
            problems.append(f"tolerans düşmüş: {match.group(0)}")
    return problems


def _token_problems(item: ModelItem, evidence: str, sources: Sources) -> list[str]:
    problems = []
    stray_numbers = numbers_in(item.text) - numbers_in(evidence) - word_numbers(evidence)
    if stray_numbers:
        problems.append(f"cümlede kendi alıntısında olmayan sayı: {sorted(stray_numbers)}")
    cited = [sources[q.source_no].context for q in item.quotes if q.source_no in sources]
    allowed = identifiers_in(" ".join([evidence, *cited]))
    stray_identifiers = identifiers_in(item.text) - allowed
    if stray_identifiers:
        problems.append(f"cümlede kaynakta olmayan teknik ad: {sorted(stray_identifiers)}")
    return problems


def _is_from_figure(item: ModelItem, sources: Sources) -> bool:
    for quote in item.quotes:
        source = sources.get(quote.source_no)
        if source and source.generated and normalize(quote.text) in normalize(source.generated):
            return True
    return False


def verify_item(item: ModelItem, sources: Sources) -> ItemCheck:
    """Her sayı ve teknik ad, cümlenin kendi dayanağında bulunmalıdır."""
    problems = _quote_problems(item, sources)
    code_source = _code_source(item, sources)
    if item.code_source_no is not None and code_source is None:
        problems.append(f"kod kaynağı [{item.code_source_no}] geçersiz")
    evidence = " ".join(
        [*(quote.text for quote in item.quotes), code_source.text if code_source else ""]
    )
    problems += _ocr_problems(item, sources)
    problems += _token_problems(item, evidence, sources)
    problems += _tolerance_problems(item.text, evidence)
    if FOREIGN_SCRIPT_RE.search(item.text):
        problems.append("cümlede başka alfabeden karakter")
    numbers = tuple(quote.source_no for quote in item.quotes)
    return ItemCheck(
        ok=not problems and bool(item.text.strip()),
        from_figure=_is_from_figure(item, sources),
        problems=tuple(problems),
        source_numbers=numbers
        + ((item.code_source_no,) if item.code_source_no is not None else ()),
    )


def _has_repeated_sentence(answer: ModelAnswer) -> bool:
    long_texts = [
        text
        for text in (normalize(item.text) for item in answer.items)
        if len(text.split()) >= _MIN_WORDS_FOR_REPEAT
    ]
    return len(long_texts) != len(set(long_texts))


def _verify_clarification(answer: ModelAnswer, sources: Sources) -> AnswerVerification:
    options = answer.clarify.options if answer.clarify else ()
    valid = tuple(dict.fromkeys(o.source_no for o in options if o.source_no in sources))
    if len(valid) < MIN_CLARIFY_OPTIONS:
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


def verify_answer(answer: ModelAnswer, sources: Sources) -> AnswerVerification:
    if answer.kind is AnswerKind.NOT_FOUND:
        return AnswerVerification(status=VerificationStatus.NOT_FOUND)
    if answer.kind is AnswerKind.CLARIFY:
        return _verify_clarification(answer, sources)
    checks = tuple(verify_item(item, sources) for item in answer.items)
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
