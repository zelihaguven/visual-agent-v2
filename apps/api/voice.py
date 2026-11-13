"""Yazıya çevirme ucu ve doğrulanan cümlelerin sesli teslimi."""

import asyncio
import base64
import logging
from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel, Field

from visual_agent.ask.intent import SMALL_TALK_REPLIES
from visual_agent.ask.language import detect_language
from visual_agent.ask.streaming import INCOMPLETE_MESSAGE, Event
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.result import (
    Answered,
    AskResult,
    Clarify,
    Inventory,
    NotFound,
    SmallTalk,
)
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
_MAX_SPOKEN_ITEMS = 20
_MAX_SPOKEN_CHARS = 2000
_NOTICE_INDEX = -1
GREETING = "Merhaba, hoş geldiniz. Sorunuzu sorabilirsiniz."
_WAITING = ("Bir saniye, bakıyorum.", "Hemen kontrol ediyorum.")
_NOTICES = {
    "tr": {
        "clarify": "Netleştirmem gereken bir nokta var, ekrana bakın.",
        "not_found": (
            "Bu bilgi belgelerde bulunamadı. Soruyu başka sözcüklerle sorarsanız yeniden bakarım."
        ),
        "failed": "Cevap doğrulanamadı, ekrana bakın.",
        "partial": "Bazı değerler doğrulanamadı, ekrana bakın.",
        "from_ocr": "Bu cevap görsel ya da taramadan okundu, kaynağı ekrandan kontrol edin.",
        "incomplete": "Cevap tamamlanamadı, ekrana bakın.",
        "source_line": "Kaynaktaki satır ekranda gösteriliyor.",
    },
    "en": {
        "clarify": "I need to clarify something, please check the screen.",
        "not_found": "Not found in the documents. Ask in other words and I will look again.",
        "failed": "The answer could not be verified, please check the screen.",
        "partial": "Some values could not be verified, please check the screen.",
        "from_ocr": (
            "This answer was read from an image or scan, please check the source on screen."
        ),
        "incomplete": "The answer could not be completed, please check the screen.",
        "source_line": "The source line is shown on the screen.",
    },
}


def fixed_notice_texts() -> tuple[str, ...]:
    return tuple(text for notices in _NOTICES.values() for text in notices.values())


def fixed_reply_texts() -> tuple[str, ...]:
    return tuple(text for replies in SMALL_TALK_REPLIES.values() for text in replies.values())


class TranscriptResponse(BaseModel):
    text: str


class PhraseAudio(BaseModel):
    audio: str
    mime: str


class PhrasesResponse(BaseModel):
    greeting: PhraseAudio
    waiting: list[PhraseAudio]


class SpeakItem(BaseModel):
    text: str = Field(min_length=1, max_length=_MAX_SPOKEN_CHARS)
    has_code: bool = False


class SpeakBody(BaseModel):
    items: list[SpeakItem] = Field(min_length=1, max_length=_MAX_SPOKEN_ITEMS)


class SpeakResponse(BaseModel):
    audios: list[PhraseAudio]


def _phrase(speech: Speech) -> PhraseAudio:
    return PhraseAudio(audio=base64.b64encode(speech.audio).decode("ascii"), mime=speech.mime)


class PhraseCache:
    """Sabit cümleler bir kez üretilir; değer içermedikleri için bellekte kalabilir."""

    def __init__(self) -> None:
        self._ready: PhrasesResponse | None = None
        self._lock = asyncio.Lock()

    async def get(self, voice: Voice) -> PhrasesResponse:
        async with self._lock:
            if self._ready is None:
                greeting, *waiting = await asyncio.gather(
                    *(voice.synthesize(text) for text in (GREETING, *_WAITING))
                )
                await asyncio.gather(
                    asyncio.gather(*(voice.synthesize(text) for text in fixed_reply_texts())),
                    asyncio.gather(
                        *(voice.synthesize(text) for text in fixed_notice_texts()),
                        return_exceptions=True,
                    ),
                )
                self._ready = PhrasesResponse(
                    greeting=_phrase(greeting), waiting=[_phrase(item) for item in waiting]
                )
            return self._ready


def _inventory_summary(result: Inventory, language: str) -> str:
    """Liste sesle okunmaz; sayı söylenir. Liste varsa hangisi olduğu, yoksa konu sorulur."""
    documents, codes = result.document_count, result.code_count
    listed = bool(result.documents)
    if language == "en":
        held = f"{documents} documents and {codes} codes" if codes else f"{documents} documents"
        ask = (
            "the list is on screen. Which one do you mean?"
            if listed
            else "tell me a topic or document name and I will look there."
        )
        return f"I have {held}, {ask}"
    held = f"{documents} belgede {codes} kod var" if codes else f"{documents} belge var"
    ask = (
        "liste ekranda. Hangisini soruyorsunuz?"
        if listed
        else "bir konu ya da belge adı söylerseniz ona göre ararım."
    )
    return f"{held}, {ask}"


def _answered_notice_key(result: Answered) -> str | None:
    if result.status is VerificationStatus.VERIFIED:
        return None
    if result.status is VerificationStatus.PARTIAL:
        if INCOMPLETE_MESSAGE in result.problems:
            return "incomplete"
        if any(item.from_ocr for item in result.items):
            return "from_ocr"
    hidden = [item for item in result.items if not item.verified]
    if hidden and all(item.source_quote for item in hidden):
        return None  # gizlenen her cümlenin yerine kaynak satırı gösterildi ve söylendi
    return "partial"


def _notice_key(result: AskResult) -> str | None:
    if isinstance(result, Answered):
        return _answered_notice_key(result)
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
        elif event["type"] == "item_unverified" and event.get("quote"):
            # Alıntı birden çok bedenin değerini taşıyabilir; okunmaz, ekranda olduğu söylenir.
            notices = _NOTICES.get(self._language, _NOTICES["tr"])
            self._speak(int(str(event["index"])), notices["source_line"])

    def announce(self, result: AskResult) -> None:
        """Değer içermeyen netleştirme sorusu okunur; diğer durumlarda sabit bildirim."""
        if isinstance(result, Clarify) and not any(c.isdigit() for c in result.question):
            self._speak(_NOTICE_INDEX, spoken_text(result.question, self._language))
            return
        if isinstance(result, SmallTalk):
            self._speak(_NOTICE_INDEX, result.text)
            return
        if isinstance(result, Inventory):
            summary = _inventory_summary(result, self._language)
            self._speak(_NOTICE_INDEX, spoken_text(summary, self._language))
            return
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


def _available(voice: Voice | None) -> Voice:
    if voice is None:
        raise HTTPException(status_code=503, detail="Ses servisi yapılandırılmamış.")
    return voice


def voice_router(dependency: Callable[[], Voice | None]) -> APIRouter:
    router = APIRouter(prefix="/api")
    phrases = PhraseCache()

    @router.get("/voice/phrases", response_model=PhrasesResponse)
    async def ready_phrases(voice: Annotated[Voice | None, Depends(dependency)]) -> PhrasesResponse:
        service = _available(voice)
        try:
            return await phrases.get(service)
        except Exception as error:
            logger.warning("Hazır cümleler üretilemedi", exc_info=True)
            raise HTTPException(status_code=502, detail="Sesler hazırlanamadı.") from error

    @router.post("/speak", response_model=SpeakResponse)
    async def speak(
        body: SpeakBody, voice: Annotated[Voice | None, Depends(dependency)]
    ) -> SpeakResponse:
        service = _available(voice)
        language = detect_language(" ".join(item.text for item in body.items))
        try:
            speeches = await asyncio.gather(
                *(
                    service.synthesize(spoken_text(item.text, language, has_code=item.has_code))
                    for item in body.items
                )
            )
        except Exception as error:
            logger.warning("Cevap seslendirilemedi", exc_info=True)
            raise HTTPException(status_code=502, detail="Cevap seslendirilemedi.") from error
        return SpeakResponse(audios=[_phrase(speech) for speech in speeches])

    @router.post("/transcribe", response_model=TranscriptResponse)
    async def transcribe(
        file: UploadFile, voice: Annotated[Voice | None, Depends(dependency)]
    ) -> TranscriptResponse:
        service = _available(voice)
        audio_format = _audio_format(file.content_type)
        audio = await file.read(MAX_AUDIO_BYTES + 1)
        if len(audio) > MAX_AUDIO_BYTES:
            raise HTTPException(status_code=413, detail="Kayıt çok uzun.")
        try:
            return TranscriptResponse(text=await service.transcribe(audio, audio_format))
        except Exception as error:
            logger.warning("Ses yazıya çevrilemedi", exc_info=True)
            raise HTTPException(status_code=502, detail="Ses yazıya çevrilemedi.") from error

    return router
