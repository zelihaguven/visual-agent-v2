"""Ses yalnız doğrulanan cümleden üretilir ve hiçbir yere yazılmaz."""

import asyncio
import base64
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from apps.api.main import ApiServices, create_app
from apps.api.voice import GREETING, MAX_AUDIO_BYTES
from tests.test_api_documents import FakeRepository, _events
from visual_agent.ask.deps import AskRequest
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.result import Answered, AskOutcome, AskResult, Clarify, Failed, NotFound
from visual_agent.settings import Settings
from visual_agent.voice.client import OpenRouterVoice, Speech


@dataclass
class FakeVoice:
    transcript: str = "peki dış paça"
    fail_on: str | None = None
    delays: dict[str, float] = field(default_factory=dict)
    spoken: list[str] = field(default_factory=list)
    received: list[tuple[bytes, str]] = field(default_factory=list)

    async def transcribe(self, audio: bytes, audio_format: str) -> str:
        self.received.append((audio, audio_format))
        if self.fail_on == "transcribe":
            raise RuntimeError("gizli ayrıntı")
        return self.transcript

    async def synthesize(self, text: str) -> Speech:
        self.spoken.append(text)
        await asyncio.sleep(self.delays.get(text, 0))
        if self.fail_on == text:
            raise RuntimeError("servis")
        return Speech(text.encode(), "audio/mpeg")


def verified(index: int, text: str, has_code: bool = False) -> dict[str, object]:
    return {
        "type": "item_verified",
        "index": index,
        "text": text,
        "source_numbers": [1],
        "from_figure": False,
        "has_code": has_code,
    }


UNVERIFIED = {"type": "item_unverified", "index": 1, "message": "yok", "source_numbers": []}
ANSWERED = Answered(status=VerificationStatus.VERIFIED, items=())


def make_client(
    tmp_path: Path, voice: FakeVoice | None, events: list[dict[str, object]], result: AskResult
) -> TestClient:
    async def ask(request: AskRequest) -> AskOutcome:
        assert request.on_event is not None
        for event in events:
            request.on_event(event)
        return AskOutcome(result=result, timings={})

    services = ApiServices(
        repository=FakeRepository(), ask=ask, storage_directory=tmp_path, voice=voice
    )
    return TestClient(create_app(Settings(_env_file=None), services))


def ask_events(client: TestClient, speak: bool = True) -> list[dict[str, object]]:
    body = {"question": "PNT-1162 bel kaç?", "speak": speak}
    return _events(client.post("/api/ask", json=body).text)


def audio_of(events: list[dict[str, object]]) -> list[str]:
    return [
        base64.b64decode(str(event["audio"])).decode()
        for event in events
        if event["type"] == "item_audio"
    ]


def test_only_verified_sentences_are_spoken(tmp_path: Path) -> None:
    voice = FakeVoice()
    events = [verified(0, "Bel 42,5 cm."), UNVERIFIED]

    result = ask_events(make_client(tmp_path, voice, events, ANSWERED))

    assert voice.spoken == ["Bel kırk iki virgül beş santimetre."]
    assert audio_of(result) == ["Bel kırk iki virgül beş santimetre."]


def test_no_audio_unless_requested(tmp_path: Path) -> None:
    voice = FakeVoice()

    result = ask_events(make_client(tmp_path, voice, [verified(0, "Bel 5.")], ANSWERED), False)

    assert voice.spoken == []
    assert audio_of(result) == []


def test_audio_is_delivered_in_order_even_if_later_sentence_is_ready_first(tmp_path: Path) -> None:
    voice = FakeVoice(delays={"Birinci.": 0.05})
    events = [verified(0, "Birinci."), verified(1, "İkinci.")]

    result = ask_events(make_client(tmp_path, voice, events, ANSWERED))

    assert audio_of(result) == ["Birinci.", "İkinci."]


def test_command_is_not_read_aloud(tmp_path: Path) -> None:
    voice = FakeVoice()
    events = [verified(0, "ALTER TABLE T_A RENAME;", has_code=True)]

    ask_events(make_client(tmp_path, voice, events, ANSWERED))

    assert voice.spoken == ["Komut ekranda gösteriliyor."]


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (
            NotFound(),
            "Bu bilgi belgelerde bulunamadı. Bir model ya da konu söylerseniz yardımcı olabilirim.",
        ),
        (
            Clarify(question="Model 123 mü, 456 mı?"),
            "Netleştirmem gereken bir nokta var, ekrana bakın.",
        ),
        (Failed(reason="x"), "Cevap doğrulanamadı, ekrana bakın."),
        (
            Answered(status=VerificationStatus.PARTIAL, items=()),
            "Bazı değerler doğrulanamadı, ekrana bakın.",
        ),
    ],
)
def test_unverified_outcomes_read_a_fixed_notice(
    tmp_path: Path, result: AskResult, expected: str
) -> None:
    voice = FakeVoice()

    ask_events(make_client(tmp_path, voice, [], result))

    assert voice.spoken == [expected]


def test_speech_failure_keeps_the_text_answer(tmp_path: Path) -> None:
    voice = FakeVoice(fail_on="Birinci.")
    events = [verified(0, "Birinci."), verified(1, "İkinci.")]

    result = ask_events(make_client(tmp_path, voice, events, ANSWERED))

    assert result[-1]["type"] == "item_audio" or result[-2]["type"] == "item_audio"
    assert [e["type"] for e in result].count("audio_unavailable") == 1
    assert [e["type"] for e in result].count("done") == 1
    assert audio_of(result) == ["İkinci."]


def _upload(client: TestClient, data: bytes, content_type: str) -> Any:
    return client.post("/api/transcribe", files={"file": ("kayit", data, content_type)})


def test_transcribe_returns_text_and_stores_nothing(tmp_path: Path) -> None:
    voice = FakeVoice()
    client = make_client(tmp_path, voice, [], ANSWERED)

    response = _upload(client, b"ses", "audio/webm;codecs=opus")

    assert response.status_code == 200
    assert response.json() == {"text": "peki dış paça"}
    assert voice.received == [(b"ses", "webm")]
    assert list(tmp_path.iterdir()) == []


def test_transcribe_rejects_other_file_types(tmp_path: Path) -> None:
    voice = FakeVoice()

    response = _upload(make_client(tmp_path, voice, [], ANSWERED), b"x", "application/pdf")

    assert response.status_code == 415
    assert voice.received == []


def test_transcribe_rejects_a_recording_over_the_limit(tmp_path: Path) -> None:
    voice = FakeVoice()
    client = make_client(tmp_path, voice, [], ANSWERED)

    response = _upload(client, b"x" * (MAX_AUDIO_BYTES + 1), "audio/webm")

    assert response.status_code == 413
    assert voice.received == []


def test_transcribe_failure_hides_details(tmp_path: Path) -> None:
    client = make_client(tmp_path, FakeVoice(fail_on="transcribe"), [], ANSWERED)

    response = _upload(client, b"ses", "audio/webm")

    assert response.status_code == 502
    assert "gizli" not in response.text


def test_transcribe_without_voice_service_is_unavailable(tmp_path: Path) -> None:
    response = _upload(make_client(tmp_path, None, [], ANSWERED), b"ses", "audio/webm")

    assert response.status_code == 503


def test_clarifying_question_is_read_when_it_holds_no_value(tmp_path: Path) -> None:
    voice = FakeVoice()

    ask_events(make_client(tmp_path, voice, [], Clarify(question="Hangi beden için?")))

    assert voice.spoken == ["Hangi beden için?"]


def test_speak_reads_each_answer_item_in_order(tmp_path: Path) -> None:
    voice = FakeVoice(delays={"Birinci.": 0.02})
    client = make_client(tmp_path, voice, [], ANSWERED)
    items = [{"text": "Birinci."}, {"text": "Bel 5 cm."}, {"text": "ALTER T_A;", "has_code": True}]

    response = client.post("/api/speak", json={"items": items})

    assert response.status_code == 200
    spoken = [base64.b64decode(a["audio"]).decode() for a in response.json()["audios"]]
    assert spoken == ["Birinci.", "Bel beş santimetre.", "Komut ekranda gösteriliyor."]


@pytest.mark.parametrize(
    "items",
    [[], [{"text": ""}], [{"text": "x" * 2001}], [{"text": "a"}] * 21],
    ids=["bos", "bos-metin", "uzun-metin", "cok-oge"],
)
def test_speak_limits_what_can_be_requested(tmp_path: Path, items: list[dict[str, str]]) -> None:
    voice = FakeVoice()
    client = make_client(tmp_path, voice, [], ANSWERED)

    assert client.post("/api/speak", json={"items": items}).status_code == 422
    assert voice.spoken == []


def test_speak_failure_hides_details(tmp_path: Path) -> None:
    client = make_client(tmp_path, FakeVoice(fail_on="Birinci."), [], ANSWERED)

    response = client.post("/api/speak", json={"items": [{"text": "Birinci."}]})

    assert response.status_code == 502
    assert "servis" not in response.text


def test_speak_without_voice_service_is_unavailable(tmp_path: Path) -> None:
    client = make_client(tmp_path, None, [], ANSWERED)

    assert client.post("/api/speak", json={"items": [{"text": "a"}]}).status_code == 503


def test_ready_phrases_are_generated_once(tmp_path: Path) -> None:
    voice = FakeVoice()
    client = make_client(tmp_path, voice, [], ANSWERED)

    first = client.get("/api/voice/phrases")
    second = client.get("/api/voice/phrases")

    assert first.status_code == 200
    assert second.json() == first.json()
    assert len(voice.spoken) == 1 + len(first.json()["waiting"])
    assert base64.b64decode(first.json()["greeting"]["audio"]).decode().startswith("Merhaba")


def test_failed_phrases_are_tried_again(tmp_path: Path) -> None:
    voice = FakeVoice(fail_on=GREETING)
    client = make_client(tmp_path, voice, [], ANSWERED)

    assert client.get("/api/voice/phrases").status_code == 502
    voice.fail_on = None
    assert client.get("/api/voice/phrases").status_code == 200


def test_phrases_without_voice_service_are_unavailable(tmp_path: Path) -> None:
    client = make_client(tmp_path, None, [], ANSWERED)

    assert client.get("/api/voice/phrases").status_code == 503


Handler = Callable[[httpx.Request], httpx.Response]


def _voice(http: httpx.AsyncClient, tts_format: str = "mp3") -> OpenRouterVoice:
    return OpenRouterVoice(
        http=http,
        base_url="https://router.test",
        api_key="k",
        stt_model="stt",
        stt_language="tr",
        tts_model="tts",
        tts_voice="v",
        tts_format=tts_format,  # type: ignore[arg-type]
    )


def _run_voice(
    handler: Handler, call: Callable[[OpenRouterVoice], Awaitable[Any]], fmt: str = "mp3"
) -> Any:
    async def run() -> Any:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            return await call(_voice(http, fmt))

    return asyncio.run(run())


def test_client_transcribes_with_zero_retention() -> None:
    sent: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"text": " merhaba "})

    text: str = _run_voice(handler, lambda voice: voice.transcribe(b"ses", "webm"))

    assert text == "merhaba"
    assert sent[0]["provider"] == {"zdr": True, "data_collection": "deny"}
    assert sent[0]["language"] == "tr"
    assert sent[0]["input_audio"] == {"data": base64.b64encode(b"ses").decode(), "format": "webm"}


def test_client_speech_uses_zero_retention_and_mp3() -> None:
    sent: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(json.loads(request.content))
        return httpx.Response(200, content=b"mp3")

    speech: Speech = _run_voice(handler, lambda voice: voice.synthesize("metin"))

    assert speech == Speech(b"mp3", "audio/mpeg")
    assert sent[0]["provider"] == {"zdr": True, "data_collection": "deny"}
    assert sent[0]["voice"] == "v"


def test_client_wraps_pcm_so_browsers_can_play_it() -> None:
    speech: Speech = _run_voice(
        lambda _: httpx.Response(200, content=b"\x00\x00" * 10),
        lambda voice: voice.synthesize("metin"),
        "pcm",
    )

    assert speech.mime == "audio/wav"
    assert speech.audio.startswith(b"RIFF")
