import asyncio
import sqlite3
from collections.abc import Sequence
from pathlib import Path

import pytest

from apps.worker.jobs import DocumentProcessor
from apps.worker.topics import TopicAssigner
from tests.test_catalog_repository import Report, _chunk, _document, _repository
from tests.test_worker_jobs import FakeIndexer, FakeRepository
from visual_agent.catalog.repository import DocumentRepository, DocumentStatus, open_repository
from visual_agent.generation.topic import clean_topic


class Namer:
    """Başlığa göre sabit konu verir; çağrıları sayar."""

    def __init__(self, topics: dict[str, str | None], fails: bool = False) -> None:
        self.topics = topics
        self.fails = fails
        self.calls: list[tuple[str, str, tuple[str, ...]]] = []

    async def __call__(self, title: str, excerpt: str, existing: Sequence[str]) -> str | None:
        self.calls.append((title, excerpt, tuple(existing)))
        if self.fails:
            raise RuntimeError("model yanıt vermedi")
        return self.topics.get(title)


def _ready(repository: DocumentRepository, doc_id: str) -> None:
    async def run() -> None:
        await repository.create_document(_document(doc_id))
        claimed = await repository.claim_next()
        assert claimed is not None
        await repository.mark_ready(doc_id, "tr", [_chunk(doc_id, 0)], Report(pages=1), None)

    asyncio.run(run())


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("  Ürün ölçü föyleri. ", "Ürün ölçü föyleri"),
        ("ürün ÖLÇÜ föyleri", "Ürün ölçü föyleri"),  # var olan adın yazım farkı
        ("Bu belge çok uzun bir açıklama cümlesidir ve konu adı değildir", None),
        ("", None),
        (None, None),
        (42, None),
    ],
)
def test_topic_names_are_short_and_reuse_existing_spelling(
    value: object, expected: str | None
) -> None:
    assert clean_topic(value, ["Ürün ölçü föyleri"]) == expected


def test_old_database_gets_the_topic_column(tmp_path: Path) -> None:
    path = tmp_path / "eski.db"
    connection = sqlite3.connect(path)
    connection.execute(
        "CREATE TABLE documents (doc_id TEXT PRIMARY KEY, title TEXT NOT NULL,"
        " filename TEXT NOT NULL, status TEXT NOT NULL, stored_path TEXT NOT NULL,"
        " language TEXT NOT NULL DEFAULT 'tr', display_pdf TEXT, report TEXT, error TEXT,"
        " created_at TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT '')"
    )
    connection.execute(
        "INSERT INTO documents (doc_id, title, filename, status, stored_path)"
        " VALUES ('a', 'A', 'a.pdf', 'ready', '/a.pdf')"
    )
    connection.commit()
    connection.close()
    repository = open_repository(path)

    asyncio.run(repository.migrate())
    asyncio.run(repository.migrate())  # tekrar açılış sütunu yeniden eklemeye çalışmaz

    document = asyncio.run(repository.get_document("a"))
    assert document is not None and document.topic is None


def test_ready_documents_without_a_topic_are_named_one_by_one(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    for doc_id in ("a", "b"):
        _ready(repository, doc_id)
    namer = Namer({"Belge a": "Ürün ölçü föyleri", "Belge b": "Ürün ölçü föyleri"})
    assigner = TopicAssigner(repository, namer)

    assert asyncio.run(assigner.assign_next_missing()) is True
    assert asyncio.run(assigner.assign_next_missing()) is True
    assert asyncio.run(assigner.assign_next_missing()) is False

    assert asyncio.run(repository.topics()) == ["Ürün ölçü föyleri"]
    # İkinci belge sorulurken ilk belgenin konusu seçenek olarak verildi.
    assert namer.calls[1][2] == ("Ürün ölçü föyleri",)
    assert "Satır 0" in namer.calls[0][1]


def test_failed_naming_is_not_retried_in_a_loop(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    _ready(repository, "a")
    namer = Namer({}, fails=True)
    assigner = TopicAssigner(repository, namer)

    assert asyncio.run(assigner.assign_next_missing()) is False
    assert asyncio.run(assigner.assign_next_missing()) is False

    assert len(namer.calls) == 1
    document = asyncio.run(repository.get_document("a"))
    assert document is not None and document.status is DocumentStatus.READY


def test_reprocessed_document_keeps_its_topic(tmp_path: Path) -> None:
    repository = _repository(tmp_path)
    _ready(repository, "a")
    asyncio.run(repository.set_topic("a", "İK belgeleri"))
    namer = Namer({"Belge a": "Başka konu"})

    asyncio.run(TopicAssigner(repository, namer).assign_ready("a"))

    assert namer.calls == []
    document = asyncio.run(repository.get_document("a"))
    assert document is not None and document.topic == "İK belgeleri"


class TopicsSpy:
    def __init__(self) -> None:
        self.ready: list[str] = []
        self.missing_calls = 0

    async def assign_ready(self, doc_id: str) -> None:
        self.ready.append(doc_id)

    async def assign_next_missing(self) -> bool:
        self.missing_calls += 1
        return True


def test_worker_names_new_documents_right_after_processing(tmp_path: Path) -> None:
    from tests.test_worker_jobs import document, make_processor

    repository = FakeRepository(queued=[document(tmp_path)])
    processor = make_processor(repository, FakeIndexer(), None)
    spy = TopicsSpy()
    processor = DocumentProcessor(repository, FakeIndexer(), processor._ingest, spy)  # type: ignore[arg-type]

    assert asyncio.run(processor.process_next()) is True
    assert spy.ready == ["d"]
    # Eski belgeler ayrı döngüde adlandırılır; belge kuyruğu onları beklemez.
    assert asyncio.run(processor.process_next()) is False
    assert spy.missing_calls == 0
