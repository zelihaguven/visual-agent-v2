"""Cevapları altun veriye karşı katı biçimde puanlar."""

import re
from collections.abc import Mapping, Sequence
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from evals.gold import Badge, GoldQuestion, GoldSource, Outcome
from visual_agent.domain.document import Chunk

_IDENTIFIER = re.compile(
    r"(?<![\w-])(?:"
    r"[A-Z][A-Z0-9]*(?:[_-][A-Z0-9]+)+"
    r"|[a-z][a-z0-9]*(?:_[a-z0-9]+)+"
    r"|[A-Z]+\d+[A-Z]?"
    r")(?![\w-])"
)
_NUMBER = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)*(?!\w)")
_BADGED = (Badge.VERIFIED, Badge.PARTIAL)
_REJECTED = (Outcome.NOT_FOUND, Outcome.FAILED)


class ScoringModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class AnswerItem(ScoringModel):
    text: str
    sources: tuple[GoldSource, ...] = ()


class AnswerRecord(ScoringModel):
    question_id: str
    outcome: Outcome
    badge: Badge
    items: tuple[AnswerItem, ...] = ()


class QuestionScore(ScoringModel):
    question_id: str
    outcome_ok: bool
    values_ok: bool
    source_ok: bool
    foreign_tokens: tuple[str, ...]
    passed: bool
    verified_wrong: bool
    false_reject: bool
    skipped_clarification: bool = False


class RunSummary(ScoringModel):
    total: int
    passed: int
    verified_wrong: int
    false_rejects: int
    by_kind: dict[str, tuple[int, int]]
    skipped_clarifications: int = 0


def _canonical_number(raw: str) -> str:
    parts = re.split(r"[.,]", raw)
    has_thousands = len(parts) > 2 or (
        len(parts) == 2 and len(parts[1]) == 3 and parts[0] != "0" and len(parts[0]) <= 3
    )
    if has_thousands or len(parts) == 1:
        return str(int("".join(parts)))
    return format(Decimal(f"{parts[0]}.{parts[1]}").normalize(), "f")


def extract_tokens(text: str) -> frozenset[str]:
    """Metindeki sayılar ve teknik adlar. Kod içindeki rakam ayrı sayı sayılmaz."""
    identifiers = {match.group() for match in _IDENTIFIER.finditer(text)}
    remainder = _IDENTIFIER.sub(" ", text)
    numbers = {_canonical_number(match.group()) for match in _NUMBER.finditer(remainder)}
    return frozenset(identifiers | numbers)


def _fold(text: str) -> str:
    """Türkçe büyük-küçük harf farkını yok sayar ("İki" -> "iki", "ALTI" -> "altı")."""
    return text.replace("İ", "i").replace("I", "ı").casefold()


def _value_stated(value: str, answer_text: str, answer_tokens: frozenset[str]) -> bool:
    """Değer cevapta geçer. Sayı ya da teknik ad taşımayan değer ("iki") sözcük olarak aranır."""
    tokens = extract_tokens(value)
    if tokens:
        return tokens <= answer_tokens
    pattern = rf"(?<!\w){re.escape(_fold(value))}(?!\w)"
    return re.search(pattern, _fold(answer_text)) is not None


def _source_matches(cited: GoldSource, gold: GoldSource) -> bool:
    if cited.doc_id != gold.doc_id:
        return False
    return all(
        expected is None or expected == actual
        for expected, actual in (
            (gold.page, cited.page),
            (gold.sheet, cited.sheet),
            (gold.row, cited.row),
        )
    )


def _sources_ok(question: GoldQuestion, record: AnswerRecord) -> bool:
    if not question.sources:
        return True
    cited = [source for item in record.items for source in item.sources]
    return bool(cited) and all(
        any(_source_matches(source, gold) for gold in question.sources) for source in cited
    )


def _value_cited(value: str, record: AnswerRecord, documents: Mapping[str, str]) -> bool:
    """Değer kaynak gösteren bir maddede geçer ve gösterilen belgelerden birinin metninde var."""
    tokens = extract_tokens(value)
    return any(
        tokens <= extract_tokens(item.text)
        and any(
            tokens <= extract_tokens(documents.get(source.doc_id, "")) for source in item.sources
        )
        for item in record.items
        if item.sources
    )


def skipped_clarification(
    question: GoldQuestion, record: AnswerRecord, documents: Mapping[str, str]
) -> bool:
    """Netleştirme yerine farklı değerlerin hepsi kaynağıyla ve başka değer olmadan verildi.

    Değerlerin yalnız bir kısmı verildiyse bu bir tahmindir: doğrulanmış yanlış değer sayılır.
    """
    if question.outcome is not Outcome.CLARIFY or record.outcome is not Outcome.ANSWERED:
        return False
    if not question.differing_values:
        return False
    allowed = extract_tokens(question.text).union(
        *(extract_tokens(value) for value in question.differing_values)
    )
    answer_tokens = extract_tokens(" ".join(item.text for item in record.items))
    return answer_tokens <= allowed and all(
        _value_cited(value, record, documents) for value in question.differing_values
    )


def score_question(
    question: GoldQuestion, record: AnswerRecord, documents: Mapping[str, str] | None = None
) -> QuestionScore:
    answer_text = " ".join(item.text for item in record.items)
    answer_tokens = extract_tokens(answer_text)
    foreign = tuple(sorted(answer_tokens - extract_tokens(question.evidence)))
    outcome_ok = record.outcome is question.outcome
    values_ok = all(
        _value_stated(value, answer_text, answer_tokens) for value in question.expected_values
    )
    source_ok = _sources_ok(question, record)
    passed = outcome_ok and values_ok and source_ok and not foreign
    badged = record.badge in _BADGED
    skipped = badged and skipped_clarification(question, record, documents or {})
    return QuestionScore(
        question_id=question.question_id,
        outcome_ok=outcome_ok,
        values_ok=values_ok,
        source_ok=source_ok,
        foreign_tokens=foreign,
        passed=passed,
        verified_wrong=badged and not passed and not skipped,
        false_reject=question.outcome is Outcome.ANSWERED and record.outcome in _REJECTED,
        skipped_clarification=skipped,
    )


def summarize(questions: Sequence[GoldQuestion], scores: Sequence[QuestionScore]) -> RunSummary:
    by_kind: dict[str, tuple[int, int]] = {}
    for question, score in zip(questions, scores, strict=True):
        passed, total = by_kind.get(question.kind.value, (0, 0))
        by_kind[question.kind.value] = (passed + int(score.passed), total + 1)
    return RunSummary(
        total=len(scores),
        passed=sum(score.passed for score in scores),
        verified_wrong=sum(score.verified_wrong for score in scores),
        false_rejects=sum(score.false_reject for score in scores),
        by_kind=by_kind,
        skipped_clarifications=sum(score.skipped_clarification for score in scores),
    )


def source_matches(chunk: Chunk, source: GoldSource) -> bool:
    if chunk.doc_id != source.doc_id:
        return False
    location = chunk.location
    return (
        (source.page is None or location.page == source.page)
        and (source.sheet is None or location.sheet == source.sheet)
        and (source.row is None or location.row == source.row)
    )


def question_found(question: GoldQuestion, chunks: Sequence[Chunk]) -> bool:
    """Her beklenen değer, doğru konumdaki parçalardan birinde bulunmalıdır."""
    expected = frozenset().union(*(extract_tokens(value) for value in question.expected_values))
    candidates = [c for c in chunks if any(source_matches(c, s) for s in question.sources)]
    available = (
        frozenset().union(*(extract_tokens(chunk.text) for chunk in candidates))
        if candidates
        else frozenset()
    )
    return expected <= available
