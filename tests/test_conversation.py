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


VERIFIED = answer_payload("Dış paça 76,5 cm.")


def test_first_question_does_not_call_the_rewriter() -> None:
    rewriter = follows()

    outcome = ask_with(deps_with(rewriter, FakeClient(VERIFIED)), "İç paça kaç?", context=None)

    assert rewriter.calls == []
    assert outcome.question == "İç paça kaç?"


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


def test_context_for_a_document_no_longer_visible_is_ignored() -> None:
    retriever = FakeRetriever()
    stale = ConversationContext(question=PREVIOUS.question, doc_ids=("gizli",))

    ask_with(deps_with(follows(), FakeClient(VERIFIED), retriever), "Peki dış paça?", stale)

    assert retriever.calls[0]["doc_ids"] == ("a", "b", "c")


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


def test_unverified_answer_does_not_replace_the_context() -> None:
    payload = answer_payload("Dış paça 99 cm.", "Dış paça 99")

    outcome = ask_with(deps_with(follows(), FakeClient(payload)), "Peki dış paça kaç?")

    assert isinstance(outcome.result, Answered)
    assert outcome.result.status is not VerificationStatus.VERIFIED
    assert outcome.context == PREVIOUS


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
        question="Mavi pantolon dış paça kaç?", doc_ids=("a",)
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
