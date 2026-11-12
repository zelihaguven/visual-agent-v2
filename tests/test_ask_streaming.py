import json

import pytest

from visual_agent.ask.streaming import UNVERIFIED_MESSAGE, StreamAssembler, mask_values
from visual_agent.domain.answer import PromptSource

SOURCES = {
    1: PromptSource(number=1, text="Beden M: 76,5 | Tolerans: 0,5"),
    2: PromptSource(number=2, text="Beden L: 78,5"),
}


def item(text: str, quote: str = "Beden M: 76,5", source_no: int = 1) -> dict[str, object]:
    return {"alintilar": [{"kaynak_no": source_no, "metin": quote}], "metin": text}


def content(*items: dict[str, object]) -> str:
    body = {"tur": "cevap", "cevap": list(items), "celiski_var": False}
    return json.dumps(body, ensure_ascii=False)


def assemble() -> tuple[StreamAssembler, list[dict[str, object]]]:
    events: list[dict[str, object]] = []
    return StreamAssembler(SOURCES, "tr", events.append), events


def feed_all(assembler: StreamAssembler, raw: str, step: int = 7) -> None:
    for end in range(step, len(raw) + step, step):
        assembler.feed(raw[:end], 0.1)


def of_type(events: list[dict[str, object]], name: str) -> list[dict[str, object]]:
    return [event for event in events if event["type"] == name]


@pytest.mark.parametrize(
    "text",
    [
        "İç paça 76,5 cm olmalı",
        "aralık 10-14 arası",
        "E050 hatası",
        "PNT-4417 modeli",
        "SIPARIS_TARIHI kolonu",
        "`dbo.Musteri` tablosu",
        "tam on iki adet",
    ],
)
def test_values_and_identifiers_are_hidden(text: str) -> None:
    masked = mask_values(text, "tr")

    for secret in ("76,5", "10-14", "E050", "PNT-4417", "SIPARIS_TARIHI", "dbo.Musteri", " on "):
        assert secret not in masked


def test_plain_words_stay_visible() -> None:
    assert mask_values("Ölçü tablosuna bakın", "tr") == "Ölçü tablosuna bakın"


def test_unit_is_hidden_with_its_number() -> None:
    assert "cm" not in mask_values("76,5 cm olmalı", "tr")


def test_no_streamed_event_ever_contains_an_unverified_value() -> None:
    assembler, events = assemble()

    feed_all(assembler, content(item("İç paça değeri 99 cm olarak verilmiştir.")))

    assert not any("99" in str(event) for event in events)


def test_verified_item_is_revealed_with_its_sources() -> None:
    assembler, events = assemble()

    feed_all(assembler, content(item("İç paça 76,5.")))

    verified = of_type(events, "item_verified")
    assert verified[0]["index"] == 0
    assert verified[0]["text"] == "İç paça 76,5."
    assert verified[0]["source_numbers"] == [1]


def test_failed_item_shows_message_and_does_not_block_the_next() -> None:
    assembler, events = assemble()

    feed_all(assembler, content(item("Değer 99."), item("Değer 76,5.")))

    assert of_type(events, "item_unverified")[0]["message"] == UNVERIFIED_MESSAGE
    assert of_type(events, "item_verified")[0]["index"] == 1


def test_half_written_word_is_not_sent() -> None:
    assembler, events = assemble()
    partial = '{"tur":"cevap","cevap":[{"alintilar":[],"metin":"Ölçü tablo'

    assembler.feed(partial, 0.1)

    assert of_type(events, "item_stream")[0]["text"] == "Ölçü"


def test_quote_text_is_never_streamed() -> None:
    assembler, events = assemble()

    feed_all(assembler, content(item("Sonuç budur.", quote="gizli kaynak cümlesi")))

    assert not any("gizli" in str(event) for event in of_type(events, "item_stream"))


def test_malformed_item_is_reported_as_unverified() -> None:
    assembler, events = assemble()

    assembler.feed('{"tur":"cevap","cevap":[{"metin":"Alıntısız cümle."}]}', 0.1)

    assert of_type(events, "item_unverified")


def test_retry_is_allowed_only_before_a_verified_item() -> None:
    assembler, _ = assemble()
    assert assembler.may_retry()

    assembler.feed(content(item("İç paça 76,5.")), 0.1)

    assert not assembler.may_retry()


def test_reset_clears_streamed_text() -> None:
    assembler, events = assemble()
    assembler.feed('{"tur":"cevap","cevap":[{"alintilar":[],"metin":"Ölçü tablosu ', 0.1)

    assembler.reset()
    assembler.feed('{"tur":"cevap","cevap":[{"alintilar":[],"metin":"Ölçü tablosu ', 0.2)

    assert of_type(events, "reset")
    assert len(of_type(events, "item_stream")) == 2


def test_verified_items_are_available_after_an_interruption() -> None:
    assembler, events = assemble()
    raw = content(item("İç paça 76,5."))

    assembler.feed(raw[: raw.rindex("]")], 0.1)
    assembler.interrupted()

    assert len(assembler.verified) == 1
    assert of_type(events, "incomplete")


def test_first_verified_time_is_recorded() -> None:
    assembler, _ = assemble()

    assembler.feed(content(item("İç paça 76,5.")), 1.25)

    assert assembler.first_verified_seconds == 1.25


def test_sentence_hidden_only_for_its_unit_streams_its_quote() -> None:
    assembler, events = assemble()

    feed_all(assembler, content(item("M beden 76,5 cm.")))

    hidden = of_type(events, "item_unverified")
    assert [event["quote"] for event in hidden] == ["Beden M: 76,5"]
    assert of_type(events, "item_verified") == []
