import asyncio
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.display_names import DocumentNames, markdown_title
from apps.api.main import ApiServices, create_app
from tests.test_api_documents import FakeRepository
from visual_agent.ask.deps import AskRequest
from visual_agent.catalog.repository import DocumentStatus, StoredDocument
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.document import Chunk, ChunkKind, SourceLocation
from visual_agent.domain.result import (
    Answered,
    AnsweredItem,
    AskOutcome,
    Citation,
    Clarify,
    ClarifyChoice,
    Inventory,
    InventoryDocument,
    NotFound,
)
from visual_agent.settings import Settings


@pytest.mark.parametrize(
    ("head", "expected"),
    [
        ("# Ana Menü - Ayarlar\n\nmetin", "Ana Menü - Ayarlar"),
        ("﻿\n\n#  **Kalın** başlık ##\n", "Kalın başlık"),
        ("## İkinci düzey\n", None),
        ("Düz metin\n# Sonra başlık\n", None),
        ("#etiket\n", None),
        ("", None),
    ],
)
def test_markdown_title_reads_only_a_leading_first_level_heading(
    head: str, expected: str | None
) -> None:
    assert markdown_title(head) == expected


def _stored(
    tmp_path: Path, doc_id: str, filename: str, text: str, title: str = ""
) -> StoredDocument:
    path = tmp_path / f"{doc_id}{Path(filename).suffix}"
    path.write_text(text, encoding="utf-8")
    return StoredDocument(
        doc_id=doc_id,
        title=title or Path(filename).stem,
        filename=filename,
        status=DocumentStatus.READY,
        stored_path=str(path),
    )


def _names(tmp_path: Path) -> tuple[DocumentNames, FakeRepository]:
    repository = FakeRepository(
        documents=[
            _stored(tmp_path, "md", "08_Setup_part1.md", "# Main Menu - Setup (part 1)\n\nx"),
            _stored(tmp_path, "pdf", "dikim-pdf.pdf", "# görünmez"),
            _stored(tmp_path, "own", "a.md", "# Dosyadaki başlık", title="Kullanıcının adı"),
            _stored(tmp_path, "plain", "notlar.md", "Başlıksız metin"),
        ]
    )
    return DocumentNames(), repository


@pytest.mark.parametrize(
    ("doc_id", "expected"),
    [
        ("md", "Main Menu - Setup (part 1)"),
        ("pdf", "dikim-pdf"),
        ("own", "Kullanıcının adı"),
        ("plain", "notlar"),
        ("yok", "gelen ad"),
    ],
)
def test_readable_name_by_format(tmp_path: Path, doc_id: str, expected: str) -> None:
    names, repository = _names(tmp_path)

    assert asyncio.run(names.name(doc_id, "gelen ad", repository.get_document)) == expected


def test_name_is_read_once(tmp_path: Path) -> None:
    names, repository = _names(tmp_path)
    calls: list[str] = []

    async def find(doc_id: str) -> StoredDocument | None:
        calls.append(doc_id)
        return await repository.get_document(doc_id)

    async def twice() -> None:
        await names.name("md", "x", find)
        await names.name("md", "x", find)

    asyncio.run(twice())
    assert calls == ["md"]


def _citation(doc_id: str) -> Citation:
    return Citation(chunk_id=f"{doc_id}:0", doc_id=doc_id, title="ham", location=SourceLocation())


def _client(tmp_path: Path, outcome: AskOutcome, repository: FakeRepository) -> TestClient:
    async def ask(request: AskRequest) -> AskOutcome:
        assert request.on_event is not None
        request.on_event({"type": "sources", "sources": [_citation("md").model_dump(mode="json")]})
        return outcome

    services = ApiServices(repository=repository, ask=ask, storage_directory=tmp_path)
    return TestClient(create_app(Settings(_env_file=None), services))


def _events(body: str) -> list[dict[str, object]]:
    return [json.loads(line[6:]) for line in body.splitlines() if line.startswith("data: ")]


def test_sources_answers_and_context_show_readable_names(tmp_path: Path) -> None:
    _, repository = _names(tmp_path)
    item = AnsweredItem(text="Cümle.", citations=(_citation("md"), _citation("pdf")), verified=True)
    outcome = AskOutcome(
        result=Answered(status=VerificationStatus.VERIFIED, items=(item,)),
        timings={},
        context=ConversationContext(question="soru", doc_ids=("md",), titles=("ham",)),
    )

    events = _events(
        _client(tmp_path, outcome, repository).post("/api/ask", json={"question": "soru"}).text
    )

    assert events[0]["sources"][0]["title"] == "Main Menu - Setup (part 1)"  # type: ignore[index]
    done = events[-1]
    citations = done["result"]["items"][0]["citations"]  # type: ignore[index]
    assert [c["title"] for c in citations] == ["Main Menu - Setup (part 1)", "dikim-pdf"]
    assert done["context"]["titles"] == ["Main Menu - Setup (part 1)"]  # type: ignore[index]


def test_client_context_without_titles_does_not_break_the_answer(tmp_path: Path) -> None:
    """Eski sekme adsız bağlam gönderebilir; bağlam geri dönünce akış kopmamalı."""
    _, repository = _names(tmp_path)
    context = ConversationContext(question="soru", doc_ids=("md",))
    outcome = AskOutcome(result=Clarify(question="Hangisi?"), timings={}, context=context)

    events = _events(
        _client(tmp_path, outcome, repository).post("/api/ask", json={"question": "soru"}).text
    )

    done = events[-1]
    assert done["type"] == "done"
    assert done["context"]["titles"] == ["Main Menu - Setup (part 1)"]  # type: ignore[index]


def test_clarify_buttons_show_readable_names(tmp_path: Path) -> None:
    _, repository = _names(tmp_path)
    clarify = Clarify(
        question="Hangisi?",
        options=(ClarifyChoice(doc_id="md", label="08_Setup_part1"),),
    )

    events = _events(
        _client(tmp_path, AskOutcome(result=clarify, timings={}), repository)
        .post("/api/ask", json={"question": "soru"})
        .text
    )

    options = events[-1]["result"]["options"]  # type: ignore[index]
    assert options == [{"doc_id": "md", "label": "Main Menu - Setup (part 1)"}]


def test_page_source_panel_shows_the_readable_name(tmp_path: Path) -> None:
    _, repository = _names(tmp_path)
    chunk = Chunk(
        chunk_id="md:0",
        doc_id="md",
        kind=ChunkKind.TEXT,
        text="x",
        title="08_Setup_part1",
        location=SourceLocation(page=1),
    )
    repository.chunks = {chunk.chunk_id: chunk}

    async def ask(request: AskRequest) -> AskOutcome:
        raise AssertionError("soru sorulmaz")

    services = ApiServices(repository=repository, ask=ask, storage_directory=tmp_path)
    client = TestClient(create_app(Settings(_env_file=None), services))

    assert client.get("/api/chunks/md:0/source").json()["title"] == "Main Menu - Setup (part 1)"


def test_document_list_shows_readable_names(tmp_path: Path) -> None:
    _, repository = _names(tmp_path)

    async def ask(request: AskRequest) -> AskOutcome:
        raise AssertionError("soru sorulmaz")

    services = ApiServices(repository=repository, ask=ask, storage_directory=tmp_path)
    listed = TestClient(create_app(Settings(_env_file=None), services)).get("/api/documents")

    titles = {document["doc_id"]: document["title"] for document in listed.json()}
    assert titles["md"] == "Main Menu - Setup (part 1)"
    assert titles["own"] == "Kullanıcının adı"


def test_inventory_shows_readable_names(tmp_path: Path) -> None:
    _, repository = _names(tmp_path)
    inventory = Inventory(
        documents=(InventoryDocument(doc_id="md", title="08_Setup_part1"),),
        document_count=1,
        code_count=0,
    )

    events = _events(
        _client(tmp_path, AskOutcome(result=inventory, timings={}), repository)
        .post("/api/ask", json={"question": "soru"})
        .text
    )

    documents = events[-1]["result"]["documents"]  # type: ignore[index]
    assert documents[0]["title"] == "Main Menu - Setup (part 1)"


def test_suggested_documents_show_readable_names(tmp_path: Path) -> None:
    _, repository = _names(tmp_path)
    not_found = NotFound(
        reason="E050 seçilen belgelerde geçmiyor.",
        suggestions=(ClarifyChoice(doc_id="md", label="08_Setup_part1"),),
    )

    events = _events(
        _client(tmp_path, AskOutcome(result=not_found, timings={}), repository)
        .post("/api/ask", json={"question": "soru"})
        .text
    )

    suggestions = events[-1]["result"]["suggestions"]  # type: ignore[index]
    assert suggestions == [{"doc_id": "md", "label": "Main Menu - Setup (part 1)"}]
