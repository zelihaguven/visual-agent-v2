import pytest

from evals.gold import Badge, GoldQuestion, GoldSet, GoldSource, Outcome, QuestionKind
from evals.rescore import rescore
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


REV_A, REV_B = GoldSource(doc_id="rev-a"), GoldSource(doc_id="rev-b")
REVISIONS = CLARIFY.model_copy(
    update={"text": "SRT-9874 M beden iç paça kaç?", "differing_values": ("74,0", "75,0")}
)
DOCUMENTS = {
    "rev-a": "SRT-9874 Rev A | M | İç paça 74,0",
    "rev-b": "SRT-9874 Rev B | M | İç paça 75,0",
}


def listed(
    *items: tuple[str, tuple[GoldSource, ...]], badge: Badge = Badge.VERIFIED
) -> AnswerRecord:
    return AnswerRecord(
        question_id="q3",
        outcome=Outcome.ANSWERED,
        badge=badge,
        items=tuple(AnswerItem(text=text, sources=sources) for text, sources in items),
    )


def test_listing_every_differing_value_with_its_source_is_a_skipped_clarification() -> None:
    record = listed(
        ("SRT-9874 Rev B belgesine göre M beden iç paça 75,0'dır.", (REV_B,)),
        ("SRT-9874 Rev A belgesine göre M beden iç paça 74,0'dır.", (REV_A,)),
    )

    score = score_question(REVISIONS, record, DOCUMENTS)

    assert score.skipped_clarification
    assert not score.verified_wrong
    assert not score.passed


def test_giving_only_some_differing_values_is_a_guess_and_verified_wrong() -> None:
    record = listed(("SRT-9874 M beden iç paça 75,0.", (REV_B,)))

    score = score_question(REVISIONS, record, DOCUMENTS)

    assert score.verified_wrong
    assert not score.skipped_clarification


def test_value_attributed_to_a_document_without_it_is_verified_wrong() -> None:
    record = listed(
        ("Rev A: iç paça 75,0.", (REV_A,)),
        ("Rev B: iç paça 74,0.", (REV_B,)),
    )

    assert score_question(REVISIONS, record, DOCUMENTS).verified_wrong


def test_uncited_values_are_verified_wrong() -> None:
    record = listed(("İç paça 74,0 ya da 75,0.", ()))

    assert score_question(REVISIONS, record, DOCUMENTS).verified_wrong


def test_an_extra_value_besides_the_differing_ones_is_verified_wrong() -> None:
    record = listed(
        ("Rev A: 74,0.", (REV_A,)),
        ("Rev B: 75,0, tolerans 0,5.", (REV_B,)),
    )

    assert score_question(REVISIONS, record, DOCUMENTS).verified_wrong


def test_without_document_texts_sources_cannot_be_confirmed() -> None:
    record = listed(("Rev A: 74,0.", (REV_A,)), ("Rev B: 75,0.", (REV_B,)))

    assert score_question(REVISIONS, record).verified_wrong


def test_clarify_question_without_differing_values_stays_verified_wrong() -> None:
    record = listed(("İç paça 76,5 cm.", (SOURCE,)))

    assert score_question(CLARIFY, record, {"spec-1": "İç paça 76,5"}).verified_wrong


def test_unbadged_listing_is_neither_skipped_nor_verified_wrong() -> None:
    record = listed(("Rev A: 74,0.", (REV_A,)), ("Rev B: 75,0.", (REV_B,)), badge=Badge.FAILED)

    score = score_question(REVISIONS, record, DOCUMENTS)

    assert not score.skipped_clarification and not score.verified_wrong


def test_summary_counts_skipped_clarifications_separately() -> None:
    skipped = listed(("Rev A: 74,0.", (REV_A,)), ("Rev B: 75,0.", (REV_B,)))
    guessed = listed(("Rev B: 75,0.", (REV_B,)))
    scores = [
        score_question(REVISIONS, skipped, DOCUMENTS),
        score_question(REVISIONS, guessed, DOCUMENTS),
    ]

    summary = summarize([REVISIONS, REVISIONS], scores)

    assert (summary.skipped_clarifications, summary.verified_wrong) == (1, 1)


def test_saved_answers_are_rescored_without_the_model() -> None:
    gold = GoldSet(seed=11, documents=(), questions=(LOOKUP, REVISIONS), document_texts=DOCUMENTS)
    skipped = listed(("Rev A: 74,0.", (REV_A,)), ("Rev B: 75,0.", (REV_B,)))
    rows = [
        {"question": "q3", "record": skipped.model_dump(mode="json"), "score": {"eski": True}},
        {"question": "q1", "record": answered("İç paça 76,5 cm.").model_dump(mode="json")},
    ]

    updated, summary = rescore(gold, rows)

    assert [row["question"] for row in updated] == ["q1", "q3"]
    assert updated[1]["score"]["skipped_clarification"] is True
    assert (summary.passed, summary.verified_wrong, summary.skipped_clarifications) == (1, 0, 1)


def test_rescoring_refuses_a_run_with_missing_answers() -> None:
    gold = GoldSet(seed=11, documents=(), questions=(LOOKUP,), document_texts={})

    with pytest.raises(ValueError, match="q1"):
        rescore(gold, [])


WORD_VALUE = LOOKUP.model_copy(
    update={"expected_values": ("iki",), "evidence": "Deneme süresi iki aydır."}
)


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("Deneme süresi üç aydır.", id="baska-sozcuk"),
        pytest.param("Deneme süresi belgede yazıyor.", id="degersiz-cevap"),
        pytest.param("Deneme süresi ikinci ayda biter.", id="sozcugun-parcasi"),
    ],
)
def test_a_value_written_in_words_must_appear_in_the_answer(text: str) -> None:
    score = score_question(WORD_VALUE, answered(text))

    assert not score.values_ok
    assert score.verified_wrong


@pytest.mark.parametrize("text", ["Deneme süresi iki aydır.", "İki ay deneme süresi var."])
def test_a_value_written_in_words_passes_when_stated(text: str) -> None:
    assert score_question(WORD_VALUE, answered(text)).passed
