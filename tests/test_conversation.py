"""Takip soruları: bağlam yalnız sorudan gelir, önceki cevap kaynak sayılmaz."""

import asyncio
import json
from collections.abc import Sequence
from dataclasses import dataclass, field

import httpx
import pytest
from pydantic import ValidationError

from tests.test_ask_pipeline import (
    CHUNKS,
    FakeClient,
    FakeRetriever,
    answer_payload,
    chunk,
    make_deps,
)
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.orchestrator import answer_question
from visual_agent.ask.steps import CONTEXT_GONE_QUESTION
from visual_agent.conversation.grounding import is_grounded
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.result import Answered, AskOutcome, Clarify, NotFound
from visual_agent.generation.json_model import JsonModel
from visual_agent.generation.rewrite import Rewrite, make_rewriter

PREVIOUS = ConversationContext(
    question="Mavi pantolon M beden iç paça kaç?", doc_ids=("a",), titles=("PNT-4417 ölçü föyü",)
)
RESOLVED = "Mavi pantolon M beden dış paça kaç?"


@dataclass
class FakeRewriter:
    result: Rewrite | None = None
    error: Exception | None = None
    delay: float = 0.0
    calls: list[tuple[str, str]] = field(default_factory=list)

    async def __call__(self, previous: str, message: str) -> Rewrite:
        self.calls.append((previous, message))
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


def follows(question: str = RESOLVED) -> FakeRewriter:
    return FakeRewriter(Rewrite(follows=True, question=question))


def deps_with(
    rewriter: FakeRewriter, client: FakeClient, retriever: FakeRetriever | None = None
) -> AskDeps:
    deps = make_deps(client, retriever)
    return AskDeps(
        catalog=deps.catalog,
        identifiers=deps.identifiers,
        retriever=deps.retriever,
        answer_client=deps.answer_client,
        system_prompt=deps.system_prompt,
        rewriter=rewriter,
        rewrite_limit_seconds=0.05,
    )


def ask_with(
    deps: AskDeps,
    question: str,
    context: ConversationContext | None = PREVIOUS,
    events: list[dict[str, object]] | None = None,
) -> AskOutcome:
    sink = events.append if events is not None else None
    return asyncio.run(
        answer_question(AskRequest(question=question, context=context, on_event=sink), deps)
    )


VERIFIED = answer_payload("Dış paça 76,5.")


def test_first_question_does_not_call_the_rewriter() -> None:
    rewriter = follows()

    outcome = ask_with(deps_with(rewriter, FakeClient(VERIFIED)), "İç paça kaç?", context=None)

    assert rewriter.calls == []
    assert outcome.question == "İç paça kaç?"


def test_announcing_a_question_does_not_wait_for_the_rewriter() -> None:
    rewriter = follows()

    outcome = ask_with(deps_with(rewriter, FakeClient(VERIFIED)), "Merhaba, bir şey soracağım.")

    assert rewriter.calls == []
    assert outcome.context == PREVIOUS


def test_follow_up_searches_and_answers_the_completed_question() -> None:
    client = FakeClient(VERIFIED)
    retriever = FakeRetriever()

    outcome = ask_with(deps_with(follows(), client, retriever), "Peki dış paça kaç?")

    assert retriever.calls[0]["query"] == RESOLVED
    assert RESOLVED in client.calls[0][1]["content"]
    assert "Peki dış paça" not in client.calls[0][1]["content"]
    assert outcome.question == RESOLVED


def test_follow_up_stays_in_the_documents_of_the_last_answer() -> None:
    retriever = FakeRetriever()

    outcome = ask_with(deps_with(follows(), FakeClient(VERIFIED), retriever), "Peki dış paça kaç?")

    assert retriever.calls[0]["doc_ids"] == ("a",)
    assert outcome.scope_inherited


def test_new_code_in_the_message_lifts_the_inherited_scope() -> None:
    retriever = FakeRetriever(hits=[CHUNKS[1]])
    rewriter = follows("E050 M beden iç paça kaç?")
    payload = answer_payload("E050 motor arızasıdır.", "Hata E050 motor arızasıdır.")

    outcome = ask_with(deps_with(rewriter, FakeClient(payload), retriever), "Peki E050 için?")

    assert retriever.calls[0]["doc_ids"] == ("a", "b", "c")
    assert not outcome.scope_inherited


def test_spoken_new_code_lifts_the_inherited_scope() -> None:
    retriever = FakeRetriever(hits=[CHUNKS[1]])
    rewriter = follows("e050 M beden iç paça kaç?")
    payload = answer_payload("E050 motor arızasıdır.", "Hata E050 motor arızasıdır.")

    outcome = ask_with(deps_with(rewriter, FakeClient(payload), retriever), "Peki e050 için?")

    assert retriever.calls[0]["doc_ids"] == ("a", "b", "c")
    assert not outcome.scope_inherited


def test_same_code_in_another_spelling_keeps_the_scope() -> None:
    retriever = FakeRetriever(hits=[CHUNKS[1]])
    previous = ConversationContext(question="E050 nedir?", doc_ids=("b",), titles=("Kılavuz",))
    rewriter = follows("e050 çözümü nedir?")
    payload = answer_payload("E050 motor arızasıdır.", "Hata E050 motor arızasıdır.")

    outcome = ask_with(
        deps_with(rewriter, FakeClient(payload), retriever), "Peki e050 çözümü?", previous
    )

    assert retriever.calls[0]["doc_ids"] == ("b",)
    assert outcome.scope_inherited


def test_previous_answer_never_reaches_the_rewriter_or_the_sources() -> None:
    rewriter = follows()
    client = FakeClient(VERIFIED)

    ask_with(deps_with(rewriter, client), "Peki dış paça kaç?")

    assert rewriter.calls == [(PREVIOUS.question, "Peki dış paça kaç?")]
    assert "<onceki" not in client.calls[0][1]["content"]


def test_unrelated_question_drops_the_context() -> None:
    retriever = FakeRetriever()
    rewriter = FakeRewriter(Rewrite(follows=False, question=""))

    outcome = ask_with(
        deps_with(rewriter, FakeClient(VERIFIED), retriever), "İzin kaç gün?", PREVIOUS
    )

    assert retriever.calls[0]["query"] == "İzin kaç gün?"
    assert retriever.calls[0]["doc_ids"] == ("a", "b", "c")
    assert not outcome.scope_inherited


@pytest.mark.parametrize(
    "rewriter",
    [
        FakeRewriter(error=RuntimeError("servis")),
        FakeRewriter(Rewrite(follows=True, question=RESOLVED), delay=1.0),
        follows("PNT-9999 M beden dış paça kaç?"),
        follows("Mavi pantolon XL beden dış paça kaç?"),
        follows("Mavi pantolon M beden dış paça 104 mü?"),
    ],
    ids=["hata", "zaman-asimi", "uydurma-kod", "uydurma-beden", "uydurma-sayi"],
)
def test_unusable_rewrite_asks_again_without_searching(rewriter: FakeRewriter) -> None:
    client = FakeClient(VERIFIED)
    retriever = FakeRetriever()

    outcome = ask_with(deps_with(rewriter, client, retriever), "Peki dış paça kaç?")

    assert isinstance(outcome.result, Clarify)
    assert retriever.calls == []
    assert client.calls == []
    assert outcome.context == PREVIOUS


def test_rewrite_event_is_sent_before_the_sources() -> None:
    events: list[dict[str, object]] = []

    ask_with(deps_with(follows(), FakeClient(VERIFIED)), "Peki dış paça kaç?", events=events)

    types = [event["type"] for event in events]
    assert {"type": "resolved", "question": RESOLVED} in events
    assert types.index("resolved") < types.index("sources")


def test_no_event_when_there_is_nothing_to_complete() -> None:
    events: list[dict[str, object]] = []

    ask_with(deps_with(follows(), FakeClient(VERIFIED)), "İç paça kaç?", None, events)

    assert "resolved" not in [event["type"] for event in events]


def test_verified_answer_becomes_the_next_context() -> None:
    outcome = ask_with(deps_with(follows(), FakeClient(VERIFIED)), "Peki dış paça kaç?")

    assert isinstance(outcome.result, Answered)
    assert outcome.context == ConversationContext(
        question=RESOLVED, doc_ids=("a",), titles=("PNT-4417 ölçü föyü",)
    )


def test_partially_verified_answer_becomes_the_next_context() -> None:
    retriever = FakeRetriever(hits=[CHUNKS[0].model_copy(update={"from_ocr": True})])

    outcome = ask_with(deps_with(follows(), FakeClient(VERIFIED), retriever), "Peki dış paça kaç?")

    assert isinstance(outcome.result, Answered)
    assert outcome.result.status is VerificationStatus.PARTIAL
    assert outcome.context == ConversationContext(
        question=RESOLVED, doc_ids=("a",), titles=("PNT-4417 ölçü föyü",)
    )


def test_hidden_answer_keeps_the_question_but_not_its_documents() -> None:
    payload = answer_payload("Dış paça 99.", "Dış paça 99")

    outcome = ask_with(deps_with(follows(), FakeClient(payload)), "Peki dış paça kaç?")

    assert isinstance(outcome.result, Answered)
    assert outcome.result.status is VerificationStatus.FAILED
    assert outcome.context == PREVIOUS.model_copy(update={"question": RESOLVED})


def test_follow_up_after_a_hidden_answer_is_completed_from_the_hidden_turn() -> None:
    """dikim-sohbet-2: "S beden bel?" -> "L beden?" (cevap gizlendi) -> "Etiketi ne?"."""
    first = ConversationContext(question="PNT-4417 S beden bel kaç?", doc_ids=("a",))
    hidden = answer_payload("L beden bel 42,0 cm.", "M: 76,5")  # kaynakta birim yok
    second = ask_with(
        deps_with(follows("PNT-4417 L beden bel kaç?"), FakeClient(hidden)), "L beden?", first
    )
    assert isinstance(second.result, Answered)
    assert second.result.status is VerificationStatus.FAILED

    rewriter = follows("PNT-4417 L beden etiketi ne?")
    ask_with(deps_with(rewriter, FakeClient(VERIFIED)), "Etiketi ne?", second.context)

    assert rewriter.calls == [("PNT-4417 L beden bel kaç?", "Etiketi ne?")]


def test_hidden_turn_with_a_new_code_does_not_keep_the_old_documents() -> None:
    """Önceki konu "a"; yeni kodlu soru bütün belgelerde arandı, cevabı gizlendi."""
    hidden = answer_payload("Dış paça 99.", "Dış paça 99")
    outcome = ask_with(deps_with(follows("E050 hatası nedir?"), FakeClient(hidden)), "E050 nedir?")

    assert isinstance(outcome.result, Answered)
    assert outcome.result.status is VerificationStatus.FAILED
    assert outcome.context == ConversationContext(question="E050 hatası nedir?")


def test_follow_up_after_a_hidden_turn_with_a_new_code_searches_where_it_was_asked() -> None:
    """PNT-1126 (a) -> PNT-1162 (yeni kod, cevap gizlendi) -> "peki l beden?"."""
    hidden = answer_payload("Dış paça 99.", "Dış paça 99")
    second = ask_with(deps_with(follows("E050 hatası nedir?"), FakeClient(hidden)), "E050 nedir?")
    rewriter = follows("E050 hatası ne zaman görülür?")

    third = ask_with(deps_with(rewriter, FakeClient(VERIFIED)), "peki ne zaman?", second.context)

    assert rewriter.calls == [("E050 hatası nedir?", "peki ne zaman?")]
    assert not third.scope_inherited
    assert not (isinstance(third.result, NotFound) and "geçmiyor" in third.result.reason)


def test_code_outside_the_inherited_document_only_says_this_document() -> None:
    context = ConversationContext(question="E050 hatası nedir?", doc_ids=("a",), titles=("Föy",))
    rewriter = follows("E050 hatası ne zaman görülür?")

    outcome = ask_with(deps_with(rewriter, FakeClient(VERIFIED)), "peki ne zaman?", context)

    assert isinstance(outcome.result, NotFound)
    assert outcome.scope_inherited
    assert outcome.result.reason == ""
    assert outcome.result.suggested_doc_ids == ("b",)


def test_not_found_keeps_the_previous_context() -> None:
    client = FakeClient({"tur": "bulunamadi", "cevap": [], "celiski_var": False})
    rewriter = follows("Mavi pantolon M beden kordon boyu kaç?")

    outcome = ask_with(deps_with(rewriter, client), "Peki kordon boyu kaç?")

    assert isinstance(outcome.result, NotFound)
    assert outcome.context == PREVIOUS
    assert outcome.scope_inherited


def test_clarification_keeps_the_question_it_is_waiting_on() -> None:
    hits = [chunk("a:1", "a", "Beden M: 76,5"), chunk("a:2", "a", "Beden S: 72,5")]
    client = FakeClient(
        {
            "tur": "netlestirme",
            "cevap": [],
            "celiski_var": False,
            "netlestirme": {
                "soru": "Hangi beden?",
                "secenekler": [{"kaynak_no": 1}, {"kaynak_no": 2}],
            },
        }
    )
    rewriter = follows("Mavi pantolon dış paça kaç?")

    outcome = ask_with(deps_with(rewriter, client, FakeRetriever(hits=hits)), "Peki dış paça?")

    assert isinstance(outcome.result, Clarify)
    assert outcome.context == ConversationContext(
        question="Mavi pantolon dış paça kaç?", doc_ids=("a",), titles=("PNT-4417 ölçü föyü",)
    )


@pytest.mark.parametrize(
    ("rewritten", "expected"),
    [
        ("PNT-4417 M beden dış paça kaç?", True),
        ("pnt-4417 m beden dış paça kaç?", True),
        ("PNT-4417 m beden dış paça kaçtı?", True),
        ("PNT-4417'nin M bedeninde dış paça kaç?", True),
        ("PNT-4418 M beden dış paça kaç?", False),
        ("PNT-4417 L beden dış paça kaç?", False),
        ("PNT-4417 M beden dış paça 76,5 mi?", False),
        ("depo_sayim tablosunda dış paça kaç?", False),
        ("", False),
        ("x" * 2001, False),
    ],
)
def test_grounding_rejects_anything_the_user_did_not_say(rewritten: str, expected: bool) -> None:
    assert (
        is_grounded(rewritten, ("Peki dış paça kaç?", "PNT-4417 M beden iç paça kaç?")) is expected
    )


def test_context_limits_are_enforced() -> None:
    with pytest.raises(ValidationError):
        ConversationContext(question="")
    with pytest.raises(ValidationError):
        ConversationContext(question="x" * 2001)
    with pytest.raises(ValidationError):
        ConversationContext(question="soru", doc_ids=tuple(str(i) for i in range(21)))


def _rewriter_response(content: str, sent: list[dict[str, object]]) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def _rewrite_call(content: str, sent: list[dict[str, object]]) -> Rewrite:
    async def run() -> Rewrite:
        async with _rewriter_response(content, sent) as http:
            rewriter = make_rewriter(
                JsonModel(http, "https://openrouter.test", "test", "m", ("p",), ("q",))
            )
            return await rewriter("Önceki?", "Yeni?")

    return asyncio.run(run())


def test_rewriter_sends_only_the_questions_with_zdr() -> None:
    sent: list[dict[str, object]] = []

    result = _rewrite_call('{"follows": true, "question": "Tam soru?"}', sent)

    assert result == Rewrite(follows=True, question="Tam soru?")
    messages: Sequence[dict[str, str]] = sent[0]["messages"]  # type: ignore[assignment]
    assert "<previous>\nÖnceki?\n</previous>" in messages[1]["content"]
    assert "<new>\nYeni?\n</new>" in messages[1]["content"]
    provider: dict[str, object] = sent[0]["provider"]  # type: ignore[assignment]
    assert provider["zdr"] is True
    assert provider["data_collection"] == "deny"
    assert provider["ignore"] == ["q"]


def test_rewriter_rejects_a_reply_without_the_expected_fields() -> None:
    with pytest.raises(ValueError, match="takip"):
        _rewrite_call('{"question": "Tam soru?"}', [])
    with pytest.raises(ValueError, match="takip"):
        _rewrite_call("metin", [])


def test_rewriter_accepts_a_reply_that_marks_a_new_topic() -> None:
    assert _rewrite_call('{"follows": false}', []) == Rewrite(follows=False, question="")


GONE = ConversationContext(question=PREVIOUS.question, doc_ids=("silindi",), titles=("Eski föy",))


def test_follow_up_whose_documents_are_all_gone_asks_which_document() -> None:
    retriever = FakeRetriever()

    outcome = ask_with(
        deps_with(follows(), FakeClient(VERIFIED), retriever), "Peki dış paça?", GONE
    )

    assert isinstance(outcome.result, Clarify)
    assert outcome.result.question == CONTEXT_GONE_QUESTION
    assert retriever.calls == []


def test_code_carried_from_a_deleted_document_asks_which_document() -> None:
    previous = ConversationContext(question="PNT-9999 M beden bel kaç?", doc_ids=("silindi",))
    retriever = FakeRetriever()
    deps = deps_with(follows("PNT-9999 M beden kalça kaç?"), FakeClient(VERIFIED), retriever)

    outcome = ask_with(deps, "Peki kalça?", previous)

    assert isinstance(outcome.result, Clarify)
    assert outcome.result.question == CONTEXT_GONE_QUESTION
    assert retriever.calls == []


def test_new_code_after_the_document_is_gone_is_searched_normally() -> None:
    retriever = FakeRetriever()
    deps = deps_with(follows("PNT-4417 M beden dış paça kaç?"), FakeClient(VERIFIED), retriever)

    outcome = ask_with(deps, "Peki PNT-4417 dış paça?", GONE)

    assert not isinstance(outcome.result, Clarify)
    assert len(retriever.calls) == 1


def test_named_document_after_the_document_is_gone_is_searched_there() -> None:
    retriever = FakeRetriever()
    deps = deps_with(follows("SQL kılavuzu dış paça ne diyor?"), FakeClient(VERIFIED), retriever)

    ask_with(deps, "Peki SQL kılavuzu ne diyor?", GONE)

    assert retriever.calls[0]["doc_ids"] == ("c",)


def test_follow_up_keeps_the_documents_that_are_still_there() -> None:
    retriever = FakeRetriever()
    partly = ConversationContext(question=PREVIOUS.question, doc_ids=("a", "silindi"))

    ask_with(deps_with(follows(), FakeClient(VERIFIED), retriever), "Peki dış paça?", partly)

    assert retriever.calls[0]["doc_ids"] == ("a",)


def test_gone_documents_stay_in_the_context_so_the_next_follow_up_asks_again() -> None:
    retriever = FakeRetriever()
    deps = deps_with(follows(), FakeClient(VERIFIED), retriever)

    first = ask_with(deps, "Peki dış paça?", GONE)
    second = ask_with(deps, "Peki bel?", first.context)

    assert first.context is not None and first.context.doc_ids == ("silindi",)
    assert isinstance(second.result, Clarify)
    assert second.result.question == CONTEXT_GONE_QUESTION
    assert retriever.calls == []
