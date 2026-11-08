"""Cevapları altun veriye karşı katı biçimde puanlar."""

import re
from collections.abc import Sequence
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from evals.gold import Badge, GoldQuestion, GoldSource, Outcome

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


class RunSummary(ScoringModel):
    total: int
    passed: int
    verified_wrong: int
    false_rejects: int
    by_kind: dict[str, tuple[int, int]]


class RunComparison(ScoringModel):
    regressed: tuple[str, ...]
    improved: tuple[str, ...]


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


def score_question(question: GoldQuestion, record: AnswerRecord) -> QuestionScore:
    answer_tokens = extract_tokens(" ".join(item.text for item in record.items))
    expected = frozenset().union(*(extract_tokens(value) for value in question.expected_values))
    foreign = tuple(sorted(answer_tokens - extract_tokens(question.evidence)))
    outcome_ok = record.outcome is question.outcome
    values_ok = expected <= answer_tokens
    source_ok = _sources_ok(question, record)
    passed = outcome_ok and values_ok and source_ok and not foreign
    return QuestionScore(
        question_id=question.question_id,
        outcome_ok=outcome_ok,
        values_ok=values_ok,
        source_ok=source_ok,
        foreign_tokens=foreign,
        passed=passed,
        verified_wrong=record.badge in _BADGED and not passed,
        false_reject=question.outcome is Outcome.ANSWERED and record.outcome in _REJECTED,
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
    )


def compare_runs(
    baseline: Sequence[QuestionScore], candidate: Sequence[QuestionScore]
) -> RunComparison:
    """İki koşuyu soru soru karşılaştırır."""
    pairs = [
        (before.question_id, before.passed, after.passed)
        for before, after in zip(baseline, candidate, strict=True)
    ]
    return RunComparison(
        regressed=tuple(qid for qid, before, after in pairs if before and not after),
        improved=tuple(qid for qid, before, after in pairs if after and not before),
    )
