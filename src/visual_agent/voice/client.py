"""OpenRouter konuşma uçları. Ses yalnız bellekte tutulur, ZDR her çağrıda zorunludur."""

import base64
import io
import wave
from dataclasses import dataclass, field
from typing import Literal, Protocol

import httpx

_ZERO_RETENTION = {"zdr": True, "data_collection": "deny"}
_TRANSCRIBE_TIMEOUT_SECONDS = 30.0
_SPEECH_TIMEOUT_SECONDS = 20.0
_PCM_SAMPLE_RATE = 24_000
_PCM_SAMPLE_WIDTH = 2


@dataclass(frozen=True)
class Speech:
    audio: bytes
    mime: str


class Voice(Protocol):
    async def transcribe(self, audio: bytes, audio_format: str) -> str: ...

    async def synthesize(self, text: str) -> Speech: ...


@dataclass
class CachingVoice:
    """Yalnız sabit cümlelerin sesi saklanır; belge cevapları tutulmaz."""

    inner: Voice
    fixed_texts: tuple[str, ...]
    _ready: dict[str, Speech] = field(default_factory=dict)

    async def transcribe(self, audio: bytes, audio_format: str) -> str:
        return await self.inner.transcribe(audio, audio_format)

    async def synthesize(self, text: str) -> Speech:
        if text in self._ready:
            return self._ready[text]
        speech = await self.inner.synthesize(text)
        if text in self.fixed_texts:
            self._ready[text] = speech
        return speech


def _wav_from_pcm(pcm: bytes) -> bytes:
    """Ham PCM tarayıcıda çalınamaz; WAV başlığı eklenir."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(_PCM_SAMPLE_WIDTH)
        output.setframerate(_PCM_SAMPLE_RATE)
        output.writeframes(pcm)
    return buffer.getvalue()


@dataclass(frozen=True)
class OpenRouterVoice:
    http: httpx.AsyncClient
    base_url: str
    api_key: str
    stt_model: str
    stt_language: str
    tts_model: str
    tts_voice: str
    tts_format: Literal["mp3", "pcm"]

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def transcribe(self, audio: bytes, audio_format: str) -> str:
        response = await self.http.post(
            f"{self.base_url}/audio/transcriptions",
            headers=self._headers,
            timeout=_TRANSCRIBE_TIMEOUT_SECONDS,
            json={
                "model": self.stt_model,
                "language": self.stt_language,
                "input_audio": {
                    "data": base64.b64encode(audio).decode("ascii"),
                    "format": audio_format,
                },
                "provider": _ZERO_RETENTION,
            },
        )
        response.raise_for_status()
        text: str = response.json()["text"]
        return text.strip()

    async def synthesize(self, text: str) -> Speech:
        response = await self.http.post(
            f"{self.base_url}/audio/speech",
            headers=self._headers,
            timeout=_SPEECH_TIMEOUT_SECONDS,
            json={
                "model": self.tts_model,
                "input": text,
                "voice": self.tts_voice,
                "response_format": self.tts_format,
                "provider": _ZERO_RETENTION,
            },
        )
        response.raise_for_status()
        if self.tts_format == "pcm":
            return Speech(_wav_from_pcm(response.content), "audio/wav")
        return Speech(response.content, "audio/mpeg")
