"""HTTP API giriş noktası."""

import asyncio
import json
import logging
import shutil
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Literal, Protocol

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Response, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from starlette.types import Scope

from apps.api.documents import RemoveVectors, delete_document
from apps.api.preview import render_highlighted_page
from apps.api.question_log import InputMode, QuestionRecord, record_for
from apps.api.voice import SpokenAnswer, voice_router
from visual_agent.ask.deps import AskRequest
from visual_agent.ask.language import detect_language
from visual_agent.ask.streaming import Event
from visual_agent.catalog.repository import DocumentStatus, StoredDocument
from visual_agent.domain.conversation import MAX_QUESTION_CHARS, ConversationContext
from visual_agent.domain.document import Chunk
from visual_agent.domain.result import (
    Answered,
    AskOutcome,
    AskResult,
    Clarify,
    Inventory,
    NotFound,
    SmallTalk,
)
from visual_agent.ingest.formats import UnsupportedFormat, detect_format
from visual_agent.settings import Settings
from visual_agent.voice.client import Voice

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
_UPLOAD_CHUNK_BYTES = 1024 * 1024
_MAX_TITLE_CHARS = 200
_GENERIC_ERROR = "Cevap hazırlanırken bir sorun oluştu. Lütfen yeniden deneyin."
_END_OF_STREAM: Event = {"type": "__end__"}
_HEALTH_TIMEOUT_SECONDS = 1.0

HealthCheck = Callable[[], Awaitable[object]]


class Repository(Protocol):
    async def create_document(self, document: StoredDocument) -> None: ...

    async def list_documents(self) -> list[StoredDocument]: ...

    async def get_document(self, doc_id: str) -> StoredDocument | None: ...

    async def get_chunk(self, chunk_id: str) -> Chunk | None: ...

    async def sheet_chunks(self, doc_id: str, sheet: str) -> Sequence[Chunk]: ...

    async def reprocess(self, doc_id: str) -> StoredDocument | None: ...

    async def mark_deleting(self, doc_id: str) -> StoredDocument | None: ...

    async def deleting_documents(self) -> list[StoredDocument]: ...

    async def purge(self, doc_id: str) -> None: ...


async def _no_vectors(doc_id: str) -> None:
    """Vektör deposu bağlanmamış (testler)."""


class QuestionRecorder(Protocol):
    async def record(self, record: QuestionRecord) -> None: ...


@dataclass(frozen=True)
class ApiServices:
    repository: Repository
    ask: Callable[[AskRequest], Awaitable[AskOutcome]]
    storage_directory: Path
    voice: Voice | None = None
    health_checks: Mapping[str, HealthCheck] = field(default_factory=dict)
    remove_vectors: RemoveVectors = _no_vectors
    question_log: QuestionRecorder | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    auth_enabled: bool
    dependencies: dict[str, bool] | None = None


class AskBody(BaseModel):
    question: str = Field(max_length=MAX_QUESTION_CHARS)
    doc_ids: tuple[str, ...] | None = None
    context: ConversationContext | None = None
    speak: bool = False
    input_mode: InputMode = "text"

    @field_validator("question")
    @classmethod
    def require_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("soru boş olamaz")
        return stripped


class DocumentResponse(BaseModel):
    doc_id: str
    title: str
    filename: str
    status: DocumentStatus
    error: str | None
    report: dict[str, object] | None


def _document_response(document: StoredDocument) -> DocumentResponse:
    return DocumentResponse(
        doc_id=document.doc_id,
        title=document.title,
        filename=document.filename,
        status=document.status,
        error=document.error,
        report=document.report,
    )


def _result_payload(result: AskResult) -> dict[str, object]:
    kinds: list[tuple[type[BaseModel], str]] = [
        (Answered, "answered"),
        (Clarify, "clarify"),
        (NotFound, "not_found"),
        (Inventory, "inventory"),
        (SmallTalk, "small_talk"),
    ]
    kind = next((name for model, name in kinds if isinstance(result, model)), "failed")
    return {"kind": kind, **result.model_dump(mode="json")}


def _sse(event: Event) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


class _AskClock:
    """Süre kullanıcının gözünden ölçülür: istek gelişinden ilk doğrulanmış cümleye."""

    def __init__(self, sink: Callable[[Event], None]) -> None:
        self._sink = sink
        self._started = time.perf_counter()
        self.first_verified: float | None = None

    def __call__(self, event: Event) -> None:
        if event.get("type") == "item_verified" and self.first_verified is None:
            self.first_verified = self.elapsed()
        self._sink(event)

    def elapsed(self) -> float:
        return time.perf_counter() - self._started


_PENDING_RECORDS: set[asyncio.Task[None]] = set()


def _record_finished(task: asyncio.Task[None]) -> None:
    _PENDING_RECORDS.discard(task)
    if not task.cancelled() and task.exception() is not None:
        logger.warning("Soru kaydı yazılamadı: %s", type(task.exception()).__name__)


def _record_question(
    request: AskBody, services: ApiServices, outcome: AskOutcome | None, clock: _AskClock
) -> None:
    """Kayıt arka planda yazılır: yavaşlasa ya da başarısız olsa da cevap beklemez."""
    if services.question_log is None:
        return
    record = record_for(
        request.question,
        "voice" if request.speak else request.input_mode,
        str(_result_payload(outcome.result)["kind"]) if outcome is not None else "error",
        outcome,
        clock.elapsed(),
        clock.first_verified,
        follow_up=request.context is not None,
    )
    task = asyncio.create_task(services.question_log.record(record))
    _PENDING_RECORDS.add(task)
    task.add_done_callback(_record_finished)


async def _answer_events(request: AskBody, services: ApiServices) -> AsyncIterator[str]:
    """Soru hattının olaylarını üretildikleri anda istemciye taşır."""
    queue: asyncio.Queue[Event] = asyncio.Queue()
    spoken = (
        SpokenAnswer(services.voice, queue.put_nowait, detect_language(request.question))
        if request.speak and services.voice is not None
        else None
    )
    clock = _AskClock(spoken.on_event if spoken is not None else queue.put_nowait)

    async def run() -> None:
        outcome: AskOutcome | None = None
        try:
            outcome = await services.ask(
                AskRequest(
                    question=request.question,
                    doc_ids=request.doc_ids,
                    context=request.context,
                    on_event=clock,
                )
            )
            _record_question(request, services, outcome, clock)
            queue.put_nowait(
                {
                    "type": "done",
                    "result": _result_payload(outcome.result),
                    "timings": outcome.timings,
                    "question": outcome.question,
                    "scope_inherited": outcome.scope_inherited,
                    "context": outcome.context.model_dump(mode="json")
                    if outcome.context is not None
                    else None,
                }
            )
            if spoken is not None:
                spoken.announce(outcome.result)
                await spoken.finish()
        except Exception:
            logger.exception("Soru cevaplanamadı")
            if outcome is None:
                _record_question(request, services, None, clock)
            queue.put_nowait({"type": "error", "message": _GENERIC_ERROR})
        finally:
            queue.put_nowait(_END_OF_STREAM)

    task = asyncio.create_task(run())
    try:
        while (event := await queue.get()) is not _END_OF_STREAM:
            yield _sse(event)
    finally:
        task.cancel()
        if spoken is not None:
            spoken.cancel()


async def _save_upload(file: UploadFile, target: Path) -> None:
    written = 0
    with target.open("wb") as stream:
        while data := await file.read(_UPLOAD_CHUNK_BYTES):
            written += len(data)
            if written > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Dosya 100 MB sınırını aşıyor.")
            stream.write(data)


def _safe_suffix(filename: str) -> str:
    return Path(filename.replace("\\", "/")).suffix.lower()


async def _store_upload(file: UploadFile, title: str, services: ApiServices) -> StoredDocument:
    filename = Path((file.filename or "belge").replace("\\", "/")).name
    doc_id = uuid.uuid4().hex
    directory = services.storage_directory / doc_id
    directory.mkdir(parents=True)
    target = directory / f"original{_safe_suffix(filename)}"
    try:
        await _save_upload(file, target)
        detect_format(target)
    except UnsupportedFormat as error:
        shutil.rmtree(directory, ignore_errors=True)
        reason = str(error).replace(target.name, filename)
        raise HTTPException(status_code=415, detail=reason) from error
    except HTTPException:
        shutil.rmtree(directory, ignore_errors=True)
        raise
    document = StoredDocument(
        doc_id=doc_id,
        title=(title.strip() or Path(filename).stem)[:_MAX_TITLE_CHARS],
        filename=filename,
        status=DocumentStatus.QUEUED,
        stored_path=str(target),
    )
    await services.repository.create_document(document)
    return document


async def _dependency_answers(name: str, check: HealthCheck) -> bool:
    try:
        await asyncio.wait_for(check(), _HEALTH_TIMEOUT_SECONDS)
    except Exception as error:
        logger.warning("Bağımlılık cevap vermiyor: %s (%s)", name, type(error).__name__)
        return False
    return True


async def _dependency_states(checks: Mapping[str, HealthCheck]) -> dict[str, bool]:
    states = await asyncio.gather(
        *(_dependency_answers(name, check) for name, check in checks.items())
    )
    return dict(zip(checks, states, strict=True))


def _health_router(app: FastAPI) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse, response_model_exclude_none=True)
    async def health(response: Response) -> HealthResponse:
        services: ApiServices | None = app.state.services
        checks = services.health_checks if services is not None else {}
        states = await _dependency_states(checks) if checks else None
        healthy = states is None or all(states.values())
        if not healthy:
            response.status_code = 503
        return HealthResponse(
            status="ok" if healthy else "unavailable",
            auth_enabled=app.state.settings.auth_enabled,
            dependencies=states,
        )

    return router


def _require_services(app: FastAPI) -> Callable[[], ApiServices]:
    def dependency() -> ApiServices:
        services: ApiServices | None = app.state.services
        if services is None:
            raise HTTPException(status_code=503, detail="Servis henüz hazır değil.")
        return services

    return dependency


async def _chunk_source(chunk: Chunk, services: ApiServices) -> dict[str, object]:
    location = chunk.location
    if location.sheet is not None:
        rows = await services.repository.sheet_chunks(chunk.doc_id, location.sheet)
        return {
            "kind": "sheet",
            "sheet": location.sheet,
            "title": chunk.title,
            "highlight_row": location.row,
            "rows": [{"row": item.location.row, "text": item.text} for item in rows],
        }
    if location.page is not None:
        return {
            "kind": "page",
            "page": location.page,
            "title": chunk.title,
            "image_url": f"/api/chunks/{chunk.chunk_id}/preview.png",
        }
    return {"kind": "text", "text": chunk.text, "title": chunk.title}


def _library_router(app: FastAPI) -> APIRouter:
    """Belge listesi, yükleme, silme ve yeniden işleme."""
    router = APIRouter(prefix="/api")
    ServicesDep = Annotated[ApiServices, Depends(_require_services(app))]

    @router.get("/documents", response_model=list[DocumentResponse])
    async def documents(services: ServicesDep) -> list[DocumentResponse]:
        return [_document_response(d) for d in await services.repository.list_documents()]

    @router.post("/documents", response_model=DocumentResponse, status_code=201)
    async def upload(
        file: UploadFile, services: ServicesDep, title: Annotated[str, Form()] = ""
    ) -> DocumentResponse:
        return _document_response(await _store_upload(file, title, services))

    @router.delete("/documents/{doc_id}", status_code=204)
    async def delete(doc_id: str, services: ServicesDep) -> Response:
        deleted = await delete_document(
            doc_id, services.repository, services.remove_vectors, services.storage_directory
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Belge bulunamadı.")
        return Response(status_code=204)

    @router.post("/documents/{doc_id}/reprocess", response_model=DocumentResponse)
    async def reprocess(doc_id: str, services: ServicesDep) -> DocumentResponse:
        document = await services.repository.reprocess(doc_id)
        if document is not None:
            return _document_response(document)
        if await services.repository.get_document(doc_id) is None:
            raise HTTPException(status_code=404, detail="Belge bulunamadı.")
        raise HTTPException(status_code=409, detail="Belge zaten sırada ya da işleniyor.")

    return router


def _document_router(app: FastAPI) -> APIRouter:
    router = APIRouter(prefix="/api")
    ServicesDep = Annotated[ApiServices, Depends(_require_services(app))]

    @router.post("/ask")
    async def ask(body: AskBody, services: ServicesDep) -> StreamingResponse:
        return StreamingResponse(
            _answer_events(body, services),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @router.get("/chunks/{chunk_id}/source")
    async def source(chunk_id: str, services: ServicesDep) -> dict[str, object]:
        chunk = await services.repository.get_chunk(chunk_id)
        if chunk is None:
            raise HTTPException(status_code=404, detail="Kaynak bulunamadı.")
        return await _chunk_source(chunk, services)

    @router.get("/chunks/{chunk_id}/preview.png")
    async def preview(chunk_id: str, services: ServicesDep) -> Response:
        chunk = await services.repository.get_chunk(chunk_id)
        document = await services.repository.get_document(chunk.doc_id) if chunk else None
        if (
            chunk is None
            or document is None
            or document.display_pdf is None
            or chunk.location.page is None
        ):
            raise HTTPException(status_code=404, detail="Sayfa bulunamadı.")
        image = await asyncio.to_thread(
            render_highlighted_page,
            Path(document.display_pdf),
            chunk.location.page,
            chunk.location.boxes,
        )
        return Response(content=image, media_type="image/png")

    return router


class WebFiles(StaticFiles):
    """Derlenmiş arayüz: adları içerik özetli dosyalar uzun, sayfanın kendisi hiç saklanmaz."""

    async def get_response(self, path: str, scope: Scope) -> Response:
        response = await super().get_response(path, scope)
        immutable = Path(path).parts[:1] == ("assets",) and response.status_code == 200
        response.headers["Cache-Control"] = (
            "public, max-age=31536000, immutable" if immutable else "no-cache"
        )
        return response


def _mount_web(app: FastAPI, directory: str | None) -> None:
    """Sunucuda arayüzü nginx sunar; yerelde aynı porttan API verir."""
    if directory is None or not (Path(directory) / "index.html").is_file():
        return
    app.mount("/", WebFiles(directory=directory, html=True), name="web")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    if app.state.services is not None:
        yield
        return
    from apps.api.services import open_services

    async with open_services(settings) as services:
        app.state.services = services
        yield


def create_app(settings: Settings | None = None, services: ApiServices | None = None) -> FastAPI:
    resolved = settings if settings is not None else Settings()
    app = FastAPI(title="Visual Agent", lifespan=_lifespan)
    app.state.settings = resolved
    app.state.services = services
    app.include_router(_health_router(app))
    app.include_router(_document_router(app))
    app.include_router(_library_router(app))
    app.include_router(
        voice_router(lambda: app.state.services.voice if app.state.services else None)
    )
    _mount_web(app, resolved.web_directory)
    return app
