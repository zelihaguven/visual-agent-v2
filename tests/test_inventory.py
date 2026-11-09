"""Envanter soruları: sayılar modele sorulmadan sistem kayıtlarından gelir."""

import asyncio
import json
from dataclasses import dataclass, field, replace
from pathlib import Path

import httpx
import pytest

from tests.test_ask_pipeline import CHUNKS, FakeClient, FakeRetriever, ask, chunk, make_deps
from tests.test_voice_api import ANSWERED, FakeVoice, ask_events
from tests.test_voice_api import make_client as voice_client
from visual_agent.ask.deps import AskDeps, AskRequest
from visual_agent.ask.orchestrator import answer_question
from visual_agent.catalog.identifiers import build_identifier_index
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.document import DocumentMeta
from visual_agent.domain.result import (
    Answered,
    Inventory,
    InventoryDocument,
    NotFound,
    SmallTalk,
)
from visual_agent.generation.intent import Intent, make_intent_classifier
from visual_agent.generation.json_model import JsonModel

NOT_FOUND = {"tur": "bulunamadi", "cevap": [], "celiski_var": False}
ANSWER = {
    "tur": "cevap",
    "cevap": [{"alintilar": [{"kaynak_no": 1, "metin": "Beden M: 76,5"}], "metin": "76,5 cm."}],
    "celiski_var": False,
}


@dataclass
class FakeClassifier:
    intent: Intent = "inventory"
    error: Exception | None = None
    delay: float = 0.0
    calls: list[str] = field(default_factory=list)

    async def __call__(self, question: str) -> Intent:
        self.calls.append(question)
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error is not None:
            raise self.error
        return self.intent


def deps_with(classifier: FakeClassifier, payload: object = NOT_FOUND) -> AskDeps:
    return replace(
        make_deps(FakeClient(payload)),
        intent_classifier=classifier,
        intent_limit_seconds=0.05,
    )


def test_inventory_question_lists_documents_and_codes_from_the_records() -> None:
    outcome = ask(deps_with(FakeClassifier()), "Elinde kaç belge ve kaç ürün kodu var?")

    assert isinstance(outcome.result, Inventory)
    assert outcome.result.document_count == 3
    assert outcome.result.code_count == 2
    documents = {item.title: item.codes for item in outcome.result.documents}
    assert documents == {
        "PNT-4417 ölçü föyü": ("PNT-4417",),
        "Kılavuz": ("E050",),
        "SQL kılavuzu": (),
    }


def test_inventory_only_counts_documents_the_user_can_see() -> None:
    deps = deps_with(FakeClassifier())
    deps.catalog.add(DocumentMeta(doc_id="gizli", title="Gizli", access=("muhasebe",)))

    outcome = asyncio.run(answer_question(AskRequest("Neler var?", access=("dikim",)), deps))

    assert isinstance(outcome.result, Inventory)
    assert outcome.result.document_count == 3


def test_inventory_answer_does_not_use_search_or_the_model() -> None:
    deps = deps_with(FakeClassifier())

    ask(deps, "Elinde kaç belge var?")

    assert deps.answer_client.calls == []  # type: ignore[attr-defined]
    assert deps.retriever.calls == []  # type: ignore[attr-defined]


def test_question_with_a_code_skips_the_classifier() -> None:
    classifier = FakeClassifier()

    outcome = ask(deps_with(classifier, ANSWER), "PNT-4417 iç paça kaç?")

    assert isinstance(outcome.result, Answered)
    assert classifier.calls == []


def test_ordinary_question_is_answered_normally() -> None:
    classifier = FakeClassifier(intent="question")

    outcome = ask(deps_with(classifier, ANSWER), "İç paça kaç?")

    assert isinstance(outcome.result, Answered)
    assert classifier.calls == ["İç paça kaç?"]


def test_chosen_document_skips_the_classifier() -> None:
    classifier = FakeClassifier()

    outcome = ask(deps_with(classifier, ANSWER), "İç paça kaç?", doc_ids=("a",))

    assert isinstance(outcome.result, Answered)
    assert classifier.calls == []


def test_missing_code_keeps_its_reason_without_asking_the_classifier() -> None:
    classifier = FakeClassifier()

    outcome = ask(deps_with(classifier), "ZZZ-9999 bel kaç?")

    assert isinstance(outcome.result, NotFound)
    assert "ZZZ-9999" in outcome.result.reason
    assert classifier.calls == []


@pytest.mark.parametrize(
    "classifier",
    [FakeClassifier(error=RuntimeError("servis")), FakeClassifier(delay=1.0)],
    ids=["hata", "zaman-asimi"],
)
def test_classifier_problems_do_not_block_the_answer(classifier: FakeClassifier) -> None:
    outcome = ask(deps_with(classifier, ANSWER), "İç paça kaç?")

    assert isinstance(outcome.result, Answered)


def test_long_code_lists_are_cut_but_the_count_stays_true() -> None:
    chunks = [chunk(f"a:{i}", "a", f"Kod KOD-{i:04d}") for i in range(600)]
    deps = replace(deps_with(FakeClassifier()), identifiers=build_identifier_index(chunks))

    outcome = ask(deps, "Hangi kodlar var?")

    assert isinstance(outcome.result, Inventory)
    assert outcome.result.code_count == 600
    assert len(outcome.result.documents[0].codes) == 200


def test_no_classifier_means_plain_not_found() -> None:
    outcome = ask(make_deps(FakeClient(NOT_FOUND), FakeRetriever(hits=[CHUNKS[0]])), "Neler var?")

    assert isinstance(outcome.result, NotFound)


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (
            Inventory(
                documents=(InventoryDocument(doc_id="a", title="A", codes=("X1",), code_count=12),),
                document_count=4,
                code_count=12,
            ),
            "dört belgede on iki kod var, liste ekranda. Hangisini soruyorsunuz?",
        ),
        (
            Inventory(documents=(), document_count=4, code_count=0),
            "dört belge var, liste ekranda. Hangisini soruyorsunuz?",
        ),
    ],
)
def test_inventory_is_summarised_aloud_never_read_as_a_list(
    tmp_path: Path, result: Inventory, expected: str
) -> None:
    voice = FakeVoice()

    ask_events(voice_client(tmp_path, voice, [], result))

    assert voice.spoken == [expected]


def test_inventory_reaches_the_client_as_its_own_kind(tmp_path: Path) -> None:
    result = Inventory(documents=(), document_count=1, code_count=0)

    events = ask_events(voice_client(tmp_path, None, [], result), False)

    done = events[-1]["result"]
    assert isinstance(done, dict)
    assert done["kind"] == "inventory"
    assert ANSWERED.status.value == "verified"


def _classify(content: str, sent: list[dict[str, object]]) -> Intent:
    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    async def run() -> Intent:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            classifier = make_intent_classifier(
                JsonModel(http, "https://r.test", "k", "m", ("p",), ())
            )
            return await classifier("Kaç belge var?")

    return asyncio.run(run())


def test_classifier_sends_only_the_question_with_zero_retention() -> None:
    sent: list[dict[str, object]] = []

    assert _classify('{"intent": "inventory"}', sent) == "inventory"
    provider = sent[0]["provider"]
    assert isinstance(provider, dict)
    assert provider["zdr"] is True
    assert "Kaç belge var?" in str(sent[0]["messages"])


def test_classifier_treats_an_unclear_reply_as_a_question() -> None:
    assert _classify('{"intent": "belki"}', []) == "question"
    assert _classify("metin", []) == "question"


@pytest.mark.parametrize(
    ("intent", "question", "expected"),
    [
        ("greeting", "Merhaba", "Merhaba, nasıl yardımcı olabilirim?"),
        ("how_are_you", "Nasılsın?", "İyiyim, teşekkürler. Nasıl yardımcı olabilirim?"),
        ("thanks", "Teşekkürler", "Rica ederim. Başka bir sorunuz var mı?"),
        ("goodbye", "Görüşürüz", "Görüşmek üzere, iyi çalışmalar."),
    ],
)
def test_small_talk_gets_a_fixed_reply_without_search_or_model(
    intent: Intent, question: str, expected: str
) -> None:
    deps = deps_with(FakeClassifier(intent=intent))

    outcome = ask(deps, question)

    assert outcome.result == SmallTalk(text=expected)
    assert deps.answer_client.calls == []  # type: ignore[attr-defined]
    assert deps.retriever.calls == []  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("Merhaba.", "Merhaba, nasıl yardımcı olabilirim?"),
        ("selam!", "Merhaba, nasıl yardımcı olabilirim?"),
        ("Merhaba, nasılsın?", "İyiyim, teşekkürler. Nasıl yardımcı olabilirim?"),
        ("Teşekkür ederim", "Rica ederim. Başka bir sorunuz var mı?"),
        ("Hoşça kal", "Görüşmek üzere, iyi çalışmalar."),
    ],
)
def test_common_small_talk_is_recognised_without_asking_a_model(
    question: str, expected: str
) -> None:
    classifier = FakeClassifier(error=RuntimeError("servis"))

    outcome = ask(deps_with(classifier), question)

    assert outcome.result == SmallTalk(text=expected)
    assert classifier.calls == []


def test_a_greeting_inside_a_longer_question_is_not_small_talk() -> None:
    classifier = FakeClassifier(intent="question")

    outcome = ask(deps_with(classifier, ANSWER), "Merhaba, iç paça kaç?")

    assert isinstance(outcome.result, Answered)
    assert classifier.calls == ["Merhaba, iç paça kaç?"]


def test_small_talk_keeps_the_conversation_context() -> None:
    context = ConversationContext(question="Bel kaç?", doc_ids=("a",))
    deps = deps_with(FakeClassifier(intent="greeting"))
    request = AskRequest("Merhaba", context=context)

    outcome = asyncio.run(answer_question(request, deps))

    assert outcome.context == context


def _events_of(deps: AskDeps, question: str) -> list[str]:
    events: list[dict[str, object]] = []
    asyncio.run(answer_question(AskRequest(question, on_event=events.append), deps))
    return [str(event["type"]) for event in events]


@pytest.mark.parametrize(
    ("intent", "question", "searches"),
    [
        ("greeting", "Merhaba", False),
        ("inventory", "Kaç belge var?", False),
        ("question", "İç paça kaç?", True),
    ],
)
def test_searching_is_announced_only_when_a_search_will_run(
    intent: Intent, question: str, searches: bool
) -> None:
    types = _events_of(deps_with(FakeClassifier(intent=intent), ANSWER), question)

    assert ("searching" in types) is searches


def test_question_with_a_code_is_announced_as_searching() -> None:
    types = _events_of(deps_with(FakeClassifier(), ANSWER), "PNT-4417 iç paça kaç?")

    assert "searching" in types
    assert types.index("searching") < types.index("sources")


def test_small_talk_is_spoken_as_written(tmp_path: Path) -> None:
    voice = FakeVoice()

    ask_events(
        voice_client(tmp_path, voice, [], SmallTalk(text="Merhaba, nasıl yardımcı olabilirim?"))
    )

    assert voice.spoken == ["Merhaba, nasıl yardımcı olabilirim?"]


def test_small_talk_reaches_the_client_as_its_own_kind(tmp_path: Path) -> None:
    events = ask_events(voice_client(tmp_path, None, [], SmallTalk(text="Merhaba")), False)

    assert events[-1]["result"] == {"kind": "small_talk", "text": "Merhaba"}
