"""HTTP API giriş noktası."""

import asyncio
import json
import logging
import shutil
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal, Protocol

from fastapi import APIRouter, Depends, FastAPI, Form, HTTPException, Response, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from apps.api.preview import render_highlighted_page
from visual_agent.ask.deps import AskRequest
from visual_agent.ask.streaming import Event
from visual_agent.catalog.repository import DocumentStatus, StoredDocument
from visual_agent.domain.conversation import MAX_QUESTION_CHARS, ConversationContext
from visual_agent.domain.document import Chunk
from visual_agent.domain.result import (
    Answered,
    AskOutcome,
    AskResult,
    Clarify,
    NotFound,
)
from visual_agent.ingest.formats import UnsupportedFormat, detect_format
from visual_agent.settings import Settings

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
_UPLOAD_CHUNK_BYTES = 1024 * 1024
_MAX_TITLE_CHARS = 200
_GENERIC_ERROR = "Cevap hazırlanırken bir sorun oluştu. Lütfen yeniden deneyin."
_END_OF_STREAM: Event = {"type": "__end__"}


class Repository(Protocol):
    async def create_document(self, document: StoredDocument) -> None: ...

    async def list_documents(self) -> list[StoredDocument]: ...

    async def get_document(self, doc_id: str) -> StoredDocument | None: ...

    async def get_chunk(self, chunk_id: str) -> Chunk | None: ...

    async def sheet_chunks(self, doc_id: str, sheet: str) -> Sequence[Chunk]: ...


@dataclass(frozen=True)
class ApiServices:
    repository: Repository
    ask: Callable[[AskRequest], Awaitable[AskOutcome]]
    storage_directory: Path


class HealthResponse(BaseModel):
    status: Literal["ok"]
    auth_enabled: bool


class AskBody(BaseModel):
    question: str = Field(max_length=MAX_QUESTION_CHARS)
    doc_ids: tuple[str, ...] | None = None
    context: ConversationContext | None = None

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
    ]
    kind = next((name for model, name in kinds if isinstance(result, model)), "failed")
    return {"kind": kind, **result.model_dump(mode="json")}


def _sse(event: Event) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def _answer_events(request: AskBody, services: ApiServices) -> AsyncIterator[str]:
    """Soru hattının olaylarını üretildikleri anda istemciye taşır."""
    queue: asyncio.Queue[Event] = asyncio.Queue()

    async def run() -> None:
        try:
            outcome = await services.ask(
                AskRequest(
                    question=request.question,
                    doc_ids=request.doc_ids,
                    context=request.context,
                    on_event=queue.put_nowait,
                )
            )
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
        except Exception:
            logger.exception("Soru cevaplanamadı")
            queue.put_nowait({"type": "error", "message": _GENERIC_ERROR})
        finally:
            queue.put_nowait(_END_OF_STREAM)

    task = asyncio.create_task(run())
    try:
        while (event := await queue.get()) is not _END_OF_STREAM:
            yield _sse(event)
    finally:
        task.cancel()


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


def _health_router(settings: Settings) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", auth_enabled=settings.auth_enabled)

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

    @router.get("/documents", response_model=list[DocumentResponse])
    async def documents(services: ServicesDep) -> list[DocumentResponse]:
        return [_document_response(d) for d in await services.repository.list_documents()]

    @router.post("/documents", response_model=DocumentResponse, status_code=201)
    async def upload(
        file: UploadFile, services: ServicesDep, title: Annotated[str, Form()] = ""
    ) -> DocumentResponse:
        return _document_response(await _store_upload(file, title, services))

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


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    if app.state.services is not None or settings.database_url is None:
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
    app.include_router(_health_router(resolved))
    app.include_router(_document_router(app))
    return app
