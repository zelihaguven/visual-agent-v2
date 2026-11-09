import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from apps.api.main import ApiServices, create_app
from apps.api.preview import render_highlighted_page
from visual_agent.ask.deps import AskRequest
from visual_agent.catalog.repository import DocumentStatus, StoredDocument
from visual_agent.domain.document import Box, Chunk, ChunkKind, SourceLocation
from visual_agent.domain.result import AskOutcome, NotFound
from visual_agent.settings import Settings


def stored(doc_id: str = "d1", status: DocumentStatus = DocumentStatus.READY) -> StoredDocument:
    return StoredDocument(
        doc_id=doc_id, title="Belge", filename="a.pdf", status=status, stored_path="/x/a.pdf"
    )


CHUNK = Chunk(
    chunk_id="d1:0",
    doc_id="d1",
    kind=ChunkKind.TABLE_ROW,
    text="Beden: M",
    title="Belge",
    location=SourceLocation(sheet="Ölçüler", row=4),
)


@dataclass
class FakeRepository:
    documents: list[StoredDocument] = field(default_factory=lambda: [stored()])
    created: list[StoredDocument] = field(default_factory=list)
    chunks: dict[str, Chunk] = field(default_factory=lambda: {CHUNK.chunk_id: CHUNK})

    async def create_document(self, document: StoredDocument) -> None:
        self.created.append(document)

    async def list_documents(self) -> list[StoredDocument]:
        return self.documents

    async def get_document(self, doc_id: str) -> StoredDocument | None:
        return next((d for d in self.documents if d.doc_id == doc_id), None)

    async def get_chunk(self, chunk_id: str) -> Chunk | None:
        return self.chunks.get(chunk_id)

    async def sheet_chunks(self, doc_id: str, sheet: str) -> Sequence[Chunk]:
        return [CHUNK]


def make_client(tmp_path: Path, repository: FakeRepository | None = None) -> TestClient:
    async def ask(request: AskRequest) -> AskOutcome:
        assert request.on_event is not None
        request.on_event({"type": "status", "stage": "retrieve"})
        return AskOutcome(result=NotFound(reason="yok"), timings={"retrieve": 0.1})

    services = ApiServices(
        repository=repository or FakeRepository(), ask=ask, storage_directory=tmp_path
    )
    return TestClient(create_app(Settings(_env_file=None), services))


def _events(body: str) -> list[dict[str, object]]:
    return [json.loads(line[6:]) for line in body.splitlines() if line.startswith("data: ")]


def test_ask_streams_events_and_final_typed_result(tmp_path: Path) -> None:
    response = make_client(tmp_path).post("/api/ask", json={"question": "soru nedir"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    events = _events(response.text)
    assert events[0] == {"type": "status", "stage": "retrieve"}
    assert events[-1]["type"] == "done"
    assert events[-1]["result"] == {"kind": "not_found", "reason": "yok", "suggested_doc_ids": []}


@pytest.mark.parametrize("question", ["", "   ", "x" * 2001])
def test_invalid_question_is_rejected(tmp_path: Path, question: str) -> None:
    assert make_client(tmp_path).post("/api/ask", json={"question": question}).status_code == 422


def test_context_reaches_the_pipeline_and_the_next_context_is_returned(tmp_path: Path) -> None:
    received: list[AskRequest] = []
    context = {"question": "Önceki soru?", "doc_ids": ["a"], "titles": ["Belge"]}

    async def ask(request: AskRequest) -> AskOutcome:
        received.append(request)
        assert request.context is not None
        return AskOutcome(
            result=NotFound(),
            timings={},
            question="Tam soru?",
            context=request.context,
            scope_inherited=True,
        )

    services = ApiServices(repository=FakeRepository(), ask=ask, storage_directory=tmp_path)
    client = TestClient(create_app(Settings(_env_file=None), services))

    events = _events(client.post("/api/ask", json={"question": "Peki?", "context": context}).text)

    assert received[0].context is not None
    assert received[0].context.question == "Önceki soru?"
    assert events[-1]["question"] == "Tam soru?"
    assert events[-1]["scope_inherited"] is True
    assert events[-1]["context"] == context


@pytest.mark.parametrize(
    "context", [{"question": ""}, {"question": "x" * 2001}, {"doc_ids": ["a"]}]
)
def test_invalid_context_is_rejected(tmp_path: Path, context: dict[str, object]) -> None:
    body = {"question": "soru", "context": context}

    assert make_client(tmp_path).post("/api/ask", json=body).status_code == 422


def test_failure_during_answering_is_reported_without_details(tmp_path: Path) -> None:
    async def ask(request: AskRequest) -> AskOutcome:
        raise RuntimeError("gizli ayrıntı")

    services = ApiServices(repository=FakeRepository(), ask=ask, storage_directory=tmp_path)
    client = TestClient(create_app(Settings(_env_file=None), services))

    events = _events(client.post("/api/ask", json={"question": "soru"}).text)

    assert events[-1]["type"] == "error"
    assert "gizli" not in str(events[-1])


def test_upload_stores_file_and_queues_it(tmp_path: Path) -> None:
    repository = FakeRepository()
    client = make_client(tmp_path, repository)

    response = client.post(
        "/api/documents",
        files={"file": ("kılavuz.pdf", b"%PDF-1.7 icerik", "application/pdf")},
        data={"title": "Kılavuz"},
    )

    assert response.status_code == 201
    created = repository.created[0]
    assert created.title == "Kılavuz"
    assert created.status is DocumentStatus.QUEUED
    assert Path(created.stored_path).read_bytes() == b"%PDF-1.7 icerik"
    assert Path(created.stored_path).is_relative_to(tmp_path)


def test_upload_uses_file_name_when_title_is_missing(tmp_path: Path) -> None:
    repository = FakeRepository()

    make_client(tmp_path, repository).post(
        "/api/documents", files={"file": ("rapor.pdf", b"%PDF-1.7", "application/pdf")}
    )

    assert repository.created[0].title == "rapor"


def test_upload_cannot_escape_the_storage_directory(tmp_path: Path) -> None:
    repository = FakeRepository()

    make_client(tmp_path, repository).post(
        "/api/documents", files={"file": ("../../evil.pdf", b"%PDF-1.7", "application/pdf")}
    )

    assert Path(repository.created[0].stored_path).resolve().is_relative_to(tmp_path.resolve())


def test_unsupported_upload_is_rejected_with_a_reason(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/api/documents", files={"file": ("virus.exe", b"MZ", "application/octet-stream")}
    )

    assert response.status_code == 415
    assert "desteklenmiyor" in response.json()["detail"]
    assert not any(tmp_path.iterdir())


def test_oversized_upload_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("apps.api.main.MAX_UPLOAD_BYTES", 10)

    response = make_client(tmp_path).post(
        "/api/documents", files={"file": ("a.pdf", b"%PDF-" + b"x" * 20, "application/pdf")}
    )

    assert response.status_code == 413
    assert not any(tmp_path.iterdir())


def test_documents_are_listed(tmp_path: Path) -> None:
    body = make_client(tmp_path).get("/api/documents").json()

    assert body[0]["doc_id"] == "d1"
    assert body[0]["status"] == "ready"
    assert "stored_path" not in body[0]


def test_sheet_source_returns_rows_with_highlight(tmp_path: Path) -> None:
    body = make_client(tmp_path).get("/api/chunks/d1:0/source").json()

    assert body["kind"] == "sheet"
    assert body["sheet"] == "Ölçüler"
    assert body["highlight_row"] == 4
    assert body["rows"] == [{"row": 4, "text": "Beden: M"}]


def test_text_source_without_a_location_returns_the_text(tmp_path: Path) -> None:
    plain = CHUNK.model_copy(update={"chunk_id": "d1:1", "location": SourceLocation()})
    repository = FakeRepository(chunks={plain.chunk_id: plain})

    body = make_client(tmp_path, repository).get("/api/chunks/d1:1/source").json()

    assert body == {"kind": "text", "text": "Beden: M", "title": "Belge"}


def test_unknown_chunk_returns_not_found(tmp_path: Path) -> None:
    assert make_client(tmp_path).get("/api/chunks/yok/source").status_code == 404


def _write_pdf(path: Path) -> None:
    Image.new("RGB", (200, 300), "white").save(path, format="PDF", resolution=72)


def test_page_preview_draws_the_highlight(tmp_path: Path) -> None:
    pdf = tmp_path / "a.pdf"
    _write_pdf(pdf)
    box = Box(page=1, left=10, top=10, right=100, bottom=50, page_width=200, page_height=300)

    png = render_highlighted_page(pdf, 1, (box,))

    with Image.open(__import__("io").BytesIO(png)) as image:
        rgb = image.convert("RGB")
        scale = rgb.width / 200
        assert rgb.getpixel((int(50 * scale), int(30 * scale))) != (255, 255, 255)
        assert rgb.getpixel((int(150 * scale), int(200 * scale))) == (255, 255, 255)


def test_page_source_points_to_the_preview(tmp_path: Path) -> None:
    pdf = tmp_path / "a.pdf"
    _write_pdf(pdf)
    box = Box(page=1, left=10, top=10, right=100, bottom=50, page_width=200, page_height=300)
    page_chunk = CHUNK.model_copy(
        update={"chunk_id": "d1:2", "location": SourceLocation(page=1, boxes=(box,))}
    )
    document = stored().model_copy(update={"display_pdf": str(pdf)})
    repository = FakeRepository(documents=[document], chunks={page_chunk.chunk_id: page_chunk})
    client = make_client(tmp_path, repository)

    body = client.get("/api/chunks/d1:2/source").json()
    image = client.get(body["image_url"])

    assert body["kind"] == "page"
    assert body["page"] == 1
    assert image.status_code == 200
    assert image.headers["content-type"] == "image/png"


def test_services_missing_returns_unavailable() -> None:
    client = TestClient(create_app(Settings(_env_file=None)))

    assert client.get("/api/documents").status_code == 503
