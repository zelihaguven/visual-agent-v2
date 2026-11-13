"""Netleştirme adayları aynı cevabı veriyorsa sormadan cevaplanır; emin olunamazsa sorulur."""

import json
from collections.abc import Sequence
from dataclasses import dataclass, field

from tests.test_ask_pipeline import FakeRetriever, ask, chunk, make_deps
from visual_agent.domain.document import Chunk, ChunkKind, DocumentMeta
from visual_agent.domain.result import Answered, Clarify
from visual_agent.generation.openrouter import ServiceUnavailable, StreamCallbacks, StreamResult

SHARED = "Right click on the order and select Change delivery date."
CLARIFY = {
    "tur": "netlestirme",
    "netlestirme": {"soru": "Hangisi?", "secenekler": [{"kaynak_no": 1}, {"kaynak_no": 2}]},
    "cevap": [],
}


def _answer(quote: str, text: str = "Siparişe sağ tıklayıp Change delivery date seçilir.") -> dict:  # type: ignore[type-arg]
    return {
        "tur": "cevap",
        "cevap": [{"alintilar": [{"kaynak_no": 1, "metin": quote}], "metin": text}],
        "celiski_var": False,
    }


@dataclass
class SequenceClient:
    """Her çağrıda sıradaki cevabı döndürür; hata nesnesi gelirse onu fırlatır."""

    replies: list[object]
    calls: list[Sequence[dict[str, str]]] = field(default_factory=list)

    async def stream(
        self, messages: Sequence[dict[str, str]], callbacks: StreamCallbacks | None = None
    ) -> StreamResult:
        self.calls.append(messages)
        reply = self.replies[min(len(self.calls), len(self.replies)) - 1]
        if isinstance(reply, Exception):
            raise reply
        return StreamResult(
            content=json.dumps(reply),
            provider="p",
            finish="stop",
            cost_usd=0.001,
            attempts=(),
        )


def _text(chunk_id: str, doc_id: str, text: str) -> Chunk:
    return chunk(chunk_id, doc_id, text, ChunkKind.TEXT)


def _ask(client: SequenceClient, hits: list[Chunk]):  # type: ignore[no-untyped-def]
    deps = make_deps(client, FakeRetriever(hits=hits))  # type: ignore[arg-type]
    for doc_id in "de":
        deps.catalog.add(DocumentMeta(doc_id=doc_id, title=f"Belge {doc_id}"))
    return ask(deps, "Teslim tarihini nasıl değiştiririm?")


TWO_SAME = [
    _text("a:1", "a", f"Planning board. {SHARED}"),
    _text("b:1", "b", f"Low level board. {SHARED}"),
]


def test_same_answer_in_every_candidate_is_given_with_all_sources() -> None:
    client = SequenceClient([CLARIFY, _answer(SHARED)])

    outcome = _ask(client, TWO_SAME)

    assert isinstance(outcome.result, Answered)
    assert outcome.result.status.value == "verified"
    assert [c.doc_id for c in outcome.result.items[0].citations] == ["a", "b"]
    assert outcome.cost_usd == 0.002


def test_second_request_sees_only_the_first_candidate() -> None:
    client = SequenceClient([CLARIFY, _answer(SHARED)])

    _ask(client, TWO_SAME)

    second = client.calls[1][1]["content"]
    assert "Planning board." in second
    assert "Low level board." not in second


def test_different_values_keep_the_clarification() -> None:
    hits = [
        _text("a:1", "a", "Bel ölçüsü toplam: 72 cm"),
        _text("b:1", "b", "Bel ölçüsü toplam: 74 cm"),
    ]
    client = SequenceClient([CLARIFY, _answer("Bel ölçüsü toplam: 72 cm", "Bel 72 cm.")])

    result = _ask(client, hits).result

    assert isinstance(result, Clarify)
    assert [option.doc_id for option in result.options] == ["a", "b"]


def test_short_shared_quote_is_not_enough() -> None:
    hits = [_text("a:1", "a", "Bel: 72 | Kalça: 90"), _text("b:1", "b", "Bel: 72 | Kalça: 94")]
    client = SequenceClient([CLARIFY, _answer("Bel: 72", "Bel 72.")])

    assert isinstance(_ask(client, hits).result, Clarify)


def test_unverified_or_unclear_second_answer_keeps_the_clarification() -> None:
    for reply in (
        CLARIFY,
        {"tur": "bulunamadi", "cevap": [], "celiski_var": False},
        _answer("Bu cümle kaynakta yok ama uzun."),
        ServiceUnavailable("yok", ()),
    ):
        client = SequenceClient([CLARIFY, reply])

        assert isinstance(_ask(client, TWO_SAME).result, Clarify), reply


def test_clarification_within_one_document_asks_the_model_once() -> None:
    hits = [_text("a:1", "a", f"S beden. {SHARED}"), _text("a:2", "a", f"M beden. {SHARED}")]
    client = SequenceClient([CLARIFY, _answer(SHARED)])

    assert isinstance(_ask(client, hits).result, Clarify)
    assert len(client.calls) == 1


def _many(texts: Sequence[str]) -> list[Chunk]:
    return [_text(f"{doc}:1", doc, text) for doc, text in zip("abcde", texts, strict=True)]


def _clarify_all(count: int) -> dict:  # type: ignore[type-arg]
    options = [{"kaynak_no": number} for number in range(1, count + 1)]
    return {"tur": "netlestirme", "netlestirme": {"soru": "Hangisi?", "secenekler": options}}


def test_more_than_four_candidates_are_not_listed() -> None:
    hits = _many([f"Model {n}: bel {70 + n} cm ve kalça değeri" for n in range(5)])
    client = SequenceClient([_clarify_all(5), _answer("Model 0: bel 70 cm", "Bel 70 cm.")])

    result = _ask(client, hits).result

    assert isinstance(result, Clarify)
    assert result.options == ()


def test_four_candidates_are_still_listed() -> None:
    hits = _many([f"Model {n}: bel {70 + n} cm" for n in range(4)] + ["Başka metin"])
    client = SequenceClient([_clarify_all(4), CLARIFY])

    result = _ask(client, hits).result

    assert isinstance(result, Clarify)
    assert [option.doc_id for option in result.options] == ["a", "b", "c", "d"]
