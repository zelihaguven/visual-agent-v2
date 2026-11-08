import pytest

from evals.gold import Badge, GoldQuestion, GoldSource, Outcome, QuestionKind
from evals.scoring import (
    AnswerItem,
    AnswerRecord,
    compare_runs,
    extract_tokens,
    score_question,
    summarize,
)

SOURCE = GoldSource(doc_id="spec-1", page=2)
LOOKUP = GoldQuestion(
    question_id="q1",
    text="PNT-4417 M beden iç paça kaç?",
    kind=QuestionKind.TABLE_LOOKUP,
    domain="dikim",
    outcome=Outcome.ANSWERED,
    expected_values=("76,5",),
    evidence="PNT-4417 M İç paça 76,5 cm ±0,5",
    sources=(SOURCE,),
)
NOT_FOUND = LOOKUP.model_copy(
    update={
        "question_id": "q2",
        "kind": QuestionKind.NOT_IN_DOCUMENT,
        "outcome": Outcome.NOT_FOUND,
        "expected_values": (),
        "sources": (),
    }
)
CLARIFY = NOT_FOUND.model_copy(
    update={"question_id": "q3", "kind": QuestionKind.CLARIFY, "outcome": Outcome.CLARIFY}
)


def answered(text: str, source: GoldSource = SOURCE, badge: Badge = Badge.VERIFIED) -> AnswerRecord:
    return AnswerRecord(
        question_id="q1",
        outcome=Outcome.ANSWERED,
        badge=badge,
        items=(AnswerItem(text=text, sources=(source,)),),
    )


def test_correct_answer_passes() -> None:
    score = score_question(LOOKUP, answered("İç paça 76,5 cm, tolerans ±0,5."))

    assert score.passed
    assert not score.verified_wrong


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("İç paça 78 cm.", id="yanlis-sayi"),
        pytest.param("İç paça 76,5 cm, S bedende 74 cm.", id="dogrunun-yaninda-yanlis-sayi"),
        pytest.param("PNT-4471 için iç paça 76,5 cm.", id="benzer-model-kodu"),
    ],
)
def test_wrong_values_with_a_badge_count_as_verified_wrong(text: str) -> None:
    score = score_question(LOOKUP, answered(text))

    assert not score.passed
    assert score.verified_wrong


def test_extra_wrong_number_is_reported_even_when_expected_value_is_present() -> None:
    score = score_question(LOOKUP, answered("İç paça 76,5 cm, S bedende 74 cm."))

    assert score.values_ok
    assert score.foreign_tokens == ("74",)


def test_wrong_page_fails_source_check() -> None:
    wrong_page = GoldSource(doc_id="spec-1", page=3)

    score = score_question(LOOKUP, answered("İç paça 76,5 cm.", source=wrong_page))

    assert not score.source_ok
    assert score.verified_wrong


def test_answer_from_another_document_fails_even_if_value_matches() -> None:
    old_revision = GoldSource(doc_id="spec-1-rev-a", page=2)

    assert not score_question(LOOKUP, answered("İç paça 76,5 cm.", source=old_revision)).source_ok


def test_wrong_value_without_a_badge_fails_but_is_not_verified_wrong() -> None:
    score = score_question(LOOKUP, answered("İç paça 78 cm.", badge=Badge.FAILED))

    assert not score.passed
    assert not score.verified_wrong


def test_refusing_an_answerable_question_is_a_false_reject() -> None:
    record = AnswerRecord(question_id="q1", outcome=Outcome.NOT_FOUND, badge=Badge.NONE)

    score = score_question(LOOKUP, record)

    assert score.false_reject
    assert not score.verified_wrong


def test_answering_a_question_not_in_the_documents_is_verified_wrong() -> None:
    assert score_question(NOT_FOUND, answered("Kordon boyu 40 cm.")).verified_wrong


def test_correct_not_found_passes() -> None:
    record = AnswerRecord(question_id="q2", outcome=Outcome.NOT_FOUND, badge=Badge.NONE)

    assert score_question(NOT_FOUND, record).passed


def test_answering_when_clarification_is_required_is_verified_wrong() -> None:
    assert score_question(CLARIFY, answered("İç paça 76,5 cm.")).verified_wrong


def test_identifier_with_wrong_name_is_foreign() -> None:
    question = LOOKUP.model_copy(
        update={
            "expected_values": ("SIPARIS_TARIHI",),
            "evidence": "SIPARIS_BASLIK SIPARIS_TARIHI DATE",
        }
    )

    score = score_question(question, answered("Kolon adı SIP_TARIH."))

    assert not score.values_ok
    assert score.foreign_tokens == ("SIP_TARIH",)


@pytest.mark.parametrize(
    ("left", "right"),
    [("76,5", "76.5"), ("76,50", "76.5"), ("1.200", "1200"), ("0,125", "0.125")],
)
def test_number_formats_are_compared_by_value(left: str, right: str) -> None:
    assert extract_tokens(left) == extract_tokens(right)


def test_digits_inside_a_code_are_not_read_as_a_number() -> None:
    assert extract_tokens("PNT-4417 kodu") == frozenset({"PNT-4417"})


def test_summary_counts_outcomes_by_kind() -> None:
    scores = [
        score_question(LOOKUP, answered("İç paça 76,5 cm.")),
        score_question(LOOKUP, answered("İç paça 78 cm.")),
    ]

    summary = summarize([LOOKUP, LOOKUP], scores)

    assert summary.total == 2
    assert summary.passed == 1
    assert summary.verified_wrong == 1
    assert summary.by_kind[QuestionKind.TABLE_LOOKUP.value] == (1, 2)


def test_compare_runs_lists_questions_that_changed() -> None:
    good = score_question(LOOKUP, answered("İç paça 76,5 cm."))
    bad = score_question(LOOKUP, answered("İç paça 78 cm."))

    assert compare_runs([good], [bad]).regressed == ("q1",)
    assert compare_runs([bad], [good]).improved == ("q1",)
    assert compare_runs([good], [good]).regressed == ()
