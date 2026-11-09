"""Yazıya çevirme ucu ve doğrulanan cümlelerin sesli teslimi."""

import asyncio
import base64
import logging
from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel

from visual_agent.ask.streaming import Event
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.result import Answered, AskResult, Clarify, NotFound
from visual_agent.voice.client import Speech, Voice
from visual_agent.voice.reading import spoken_text

logger = logging.getLogger(__name__)

MAX_AUDIO_BYTES = 5 * 1024 * 1024
_AUDIO_FORMATS = {
    "audio/webm": "webm",
    "audio/ogg": "ogg",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a",
    "audio/aac": "aac",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
}
_NOTICE_INDEX = -1
_NOTICES = {
    "tr": {
        "clarify": "Netleştirmem gereken bir nokta var, ekrana bakın.",
        "not_found": "Bu bilgi belgelerde bulunamadı.",
        "failed": "Cevap doğrulanamadı, ekrana bakın.",
        "partial": "Bazı değerler doğrulanamadı, ekrana bakın.",
    },
    "en": {
        "clarify": "I need to clarify something, please check the screen.",
        "not_found": "This information was not found in the documents.",
        "failed": "The answer could not be verified, please check the screen.",
        "partial": "Some values could not be verified, please check the screen.",
    },
}


class TranscriptResponse(BaseModel):
    text: str


def _notice_key(result: AskResult) -> str | None:
    if isinstance(result, Answered):
        return None if result.status is VerificationStatus.VERIFIED else "partial"
    if isinstance(result, Clarify):
        return "clarify"
    return "not_found" if isinstance(result, NotFound) else "failed"


class SpokenAnswer:
    """Yalnız doğrulanan cümleler seslendirilir; sesler sırayla teslim edilir."""

    def __init__(self, voice: Voice, emit: Callable[[Event], None], language: str) -> None:
        self._voice = voice
        self._emit = emit
        self._language = language
        self._tasks: list[asyncio.Task[object]] = []
        self._last: asyncio.Task[None] | None = None
        self._reported_failure = False

    def on_event(self, event: Event) -> None:
        self._emit(event)
        if event["type"] == "item_verified":
            text = spoken_text(str(event["text"]), self._language, has_code=bool(event["has_code"]))
            self._speak(int(str(event["index"])), text)

    def announce(self, result: AskResult) -> None:
        """Doğrulanmamış sonuçlarda model metni değil, sabit bir bildirim okunur."""
        key = _notice_key(result)
        if key is not None:
            notices = _NOTICES.get(self._language, _NOTICES["tr"])
            self._speak(_NOTICE_INDEX, notices[key])

    def _speak(self, index: int, text: str) -> None:
        speech = asyncio.create_task(self._voice.synthesize(text))
        self._last = asyncio.create_task(self._deliver(index, speech, self._last))
        self._tasks += [speech, self._last]

    async def _deliver(
        self, index: int, speech: asyncio.Task[Speech], previous: asyncio.Task[None] | None
    ) -> None:
        if previous is not None:
            await previous
        try:
            result = await speech
        except Exception:
            logger.warning("Cümle seslendirilemedi", exc_info=True)
            if not self._reported_failure:
                self._reported_failure = True
                self._emit({"type": "audio_unavailable"})
            return
        audio = base64.b64encode(result.audio).decode("ascii")
        self._emit({"type": "item_audio", "index": index, "audio": audio, "mime": result.mime})

    async def finish(self) -> None:
        if self._last is not None:
            await self._last

    def cancel(self) -> None:
        for task in self._tasks:
            task.cancel()


def _audio_format(content_type: str | None) -> str:
    audio_format = _AUDIO_FORMATS.get((content_type or "").split(";")[0].strip().lower())
    if audio_format is None:
        raise HTTPException(status_code=415, detail="Bu ses biçimi desteklenmiyor.")
    return audio_format


def voice_router(dependency: Callable[[], Voice | None]) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.post("/transcribe", response_model=TranscriptResponse)
    async def transcribe(
        file: UploadFile, voice: Annotated[Voice | None, Depends(dependency)]
    ) -> TranscriptResponse:
        if voice is None:
            raise HTTPException(status_code=503, detail="Ses servisi yapılandırılmamış.")
        audio_format = _audio_format(file.content_type)
        audio = await file.read(MAX_AUDIO_BYTES + 1)
        if len(audio) > MAX_AUDIO_BYTES:
            raise HTTPException(status_code=413, detail="Kayıt çok uzun.")
        try:
            return TranscriptResponse(text=await voice.transcribe(audio, audio_format))
        except Exception as error:
            logger.warning("Ses yazıya çevrilemedi", exc_info=True)
            raise HTTPException(status_code=502, detail="Ses yazıya çevrilemedi.") from error

    return router
