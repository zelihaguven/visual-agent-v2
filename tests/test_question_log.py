import asyncio
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api import question_log
from apps.api.main import ApiServices, create_app
from apps.api.question_log import (
    QuestionRecord,
    open_log,
    problem_kind,
    record_for,
    record_lines,
    summary_lines,
)
from tests.test_api_documents import FakeRepository, _events
from visual_agent.ask.deps import AskRequest
from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.document import SourceLocation
from visual_agent.domain.result import (
    Answered,
    AnsweredItem,
    AskOutcome,
    Citation,
    NotFound,
)
from visual_agent.settings import Settings

ANSWER_TEXT = "PNT-1162 M beden bel 76 cm."


def _citation(doc_id: str) -> Citation:
    return Citation(
        chunk_id=f"{doc_id}:0", doc_id=doc_id, title="Föy", location=SourceLocation(page=1)
    )


ANSWERED = AskOutcome(
    result=Answered(
        status=VerificationStatus.PARTIAL,
        items=(
            AnsweredItem(
                text=ANSWER_TEXT,
                citations=(_citation("a"), _citation("b")),
                verified=True,
            ),
            AnsweredItem(
                text="Kalça 98 cm.",
                citations=(_citation("a"),),
                verified=False,
                problems=("cümlede kendi alıntısında olmayan sayı: ['98']",),
            ),
        ),
        problems=("aynı cümle tekrar ediyor",),
    ),
    timings={"context": 0.4, "intent": 0.2, "translate": 0.3, "retrieve": 0.1, "generate": 1.5},
    cost_usd=0.0004,
    provider="deepinfra",
    question="PNT-1162 M beden bel kaç?",
)


def test_record_keeps_kind_verification_sources_and_steps_but_not_the_answer() -> None:
    record = record_for("Peki bel?", "voice", "answered", ANSWERED, 2.5, 1.9)

    assert record.resolved_question == "PNT-1162 M beden bel kaç?"
    assert record.input_mode == "voice"
    assert record.verification_status == "partial"
    assert record.problems == (
        "aynı cümle tekrar ediyor",
        "cümlede kendi alıntısında olmayan sayı",
    )
    assert record.cited_doc_ids == ("a", "b")
    assert (record.provider, record.cost_usd) == ("deepinfra", 0.0004)
    assert (record.total_seconds, record.first_verified_seconds) == (2.5, 1.9)
    assert record.timings["translate"] == 0.3
    assert ANSWER_TEXT not in record.model_dump_json()


def test_question_that_needed_no_completion_has_no_resolved_question() -> None:
    outcome = AskOutcome(result=NotFound(reason="yok"), timings={}, question="Soru?")

    record = record_for("Soru?", "text", "not_found", outcome, 0.5, None)

    assert record.resolved_question is None
    assert record.verification_status is None
    assert record.cited_doc_ids == ()


def test_failed_question_is_recorded_as_an_error() -> None:
    record = record_for("Soru?", "text", "error", None, 3.0, None)

    assert (record.result_kind, record.timings) == ("error", {})


def test_records_are_stored_and_read_back_newest_first(tmp_path: Path) -> None:
    log = open_log(tmp_path / "va.db")

    async def run() -> list[QuestionRecord]:
        await log.migrate()
        for question in ("ilk", "ikinci", "üçüncü"):
            await log.add(
                record_for(question, "text", "answered", ANSWERED, 1.0, 0.5, follow_up=True)
            )
        return await log.last(2)

    records = asyncio.run(run())

    assert [r.question for r in records] == ["üçüncü", "ikinci"]
    assert records[0].timings == ANSWERED.timings
    assert records[0].cited_doc_ids == ("a", "b")


def test_failed_write_is_only_logged(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    log = open_log(tmp_path)

    asyncio.run(log.record(record_for("Soru?", "text", "error", None, 1.0, None)))

    assert "Soru kaydı yazılamadı" in caplog.text


def _record(**overrides: object) -> QuestionRecord:
    values: dict[str, object] = {
        "created_at": "2026-11-10T10:00:00.000+00:00",
        "question": "soru",
        "resolved_question": None,
        "input_mode": "text",
        "result_kind": "answered",
        "total_seconds": 2.0,
        "timings": {"intent": 0.2, "retrieve": 0.1},
    }
    return QuestionRecord.model_validate({**values, **overrides})


def test_summary_counts_kinds_and_reads_each_step_apart() -> None:
    records = [
        _record(first_verified_seconds=1.0, timings={"context": 0.6, "intent": 0.2}),
        _record(input_mode="voice", timings={"intent": 0.4, "translate": 0.3}),
        _record(result_kind="not_found", total_seconds=4.0, timings={"intent": 0.3}),
    ]

    lines = summary_lines(records)

    assert lines[0] == "3 soru: answered 2, not_found 1"
    assert lines[1] == "giriş: text 2, voice 1"
    assert "ortanca 2.00 sn" in lines[2]
    assert "(1 soru)" in lines[3]
    assert "  takip tamamlama: ortanca 0.60 sn, p90 0.60 sn (1 soru)" in lines
    assert "  niyet: ortanca 0.30 sn, p90 0.40 sn (3 soru)" in lines
    assert "  çeviri: ortanca 0.30 sn, p90 0.30 sn (1 soru)" in lines
    assert not any("arama" in line for line in lines)


def test_empty_log_says_so() -> None:
    assert summary_lines([]) == ["Kayıt yok."]
    assert record_lines([]) == []


def test_command_prints_the_last_records_and_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    database = tmp_path / "va.db"

    async def seed() -> None:
        log = open_log(database)
        await log.migrate()
        await log.add(_record(question="PNT-1162 bel kaç?"))

    asyncio.run(seed())
    monkeypatch.setattr(sys, "argv", ["question_log", "--last", "5", "--database", str(database)])

    question_log.main()

    output = capsys.readouterr().out
    assert "PNT-1162 bel kaç?" in output
    assert "1 soru: answered 1" in output


@dataclass
class Recorder:
    records: list[QuestionRecord] = field(default_factory=list)
    error: Exception | None = None

    async def record(self, record: QuestionRecord) -> None:
        if self.error is not None:
            raise self.error
        self.records.append(record)


def _client(recorder: Recorder, fail: bool = False) -> TestClient:
    async def ask(request: AskRequest) -> AskOutcome:
        if fail:
            raise RuntimeError("model kapalı")
        assert request.on_event is not None
        request.on_event({"type": "item_verified", "index": 0, "text": ANSWER_TEXT})
        return ANSWERED

    services = ApiServices(
        repository=FakeRepository(),
        ask=ask,
        storage_directory=Path("."),
        question_log=recorder,
    )
    return TestClient(create_app(Settings(_env_file=None, web_directory=None), services))


def test_each_question_is_recorded_with_its_input_mode() -> None:
    recorder = Recorder()

    with _client(recorder) as client:
        client.post("/api/ask", json={"question": "yazılı soru"})
        client.post("/api/ask", json={"question": "dikte", "input_mode": "voice"})

    assert [(r.question, r.input_mode) for r in recorder.records] == [
        ("yazılı soru", "text"),
        ("dikte", "voice"),
    ]
    first = recorder.records[0]
    assert first.result_kind == "answered"
    assert first.first_verified_seconds is not None
    assert first.first_verified_seconds <= first.total_seconds


def test_failed_question_is_recorded_and_still_answered_with_an_error() -> None:
    recorder = Recorder()

    with _client(recorder, fail=True) as client:
        events = _events(client.post("/api/ask", json={"question": "soru"}).text)

    assert events[-1]["type"] == "error"
    assert [r.result_kind for r in recorder.records] == ["error"]


def test_answer_is_unaffected_when_the_record_cannot_be_written() -> None:
    recorder = Recorder(error=OSError("disk dolu"))

    with _client(recorder) as client:
        events = _events(client.post("/api/ask", json={"question": "soru"}).text)

    assert events[-1]["type"] == "done"
    assert json.dumps(events[-1]["result"], ensure_ascii=False).count(ANSWER_TEXT) == 1


def test_follow_up_time_is_kept_only_for_questions_with_a_context() -> None:
    first = record_for("Soru?", "text", "answered", ANSWERED, 1.0, None)
    follow = record_for("Peki?", "text", "answered", ANSWERED, 1.0, None, follow_up=True)

    assert "context" not in first.timings
    assert follow.timings["context"] == 0.4


def test_record_line_shows_missing_first_sentence_and_provider() -> None:
    line = record_lines([_record(provider="deepinfra")])[0]

    assert "ilk     -" in line
    assert "deepinfra" in line


@pytest.mark.parametrize(
    ("problem", "kind"),
    [
        ("cümlede kaynakta olmayan teknik ad: ['pnt-1162']", "cümlede kaynakta olmayan teknik ad"),
        (
            "cümlede kendi alıntısında olmayan sayı: ['80', '76']",
            "cümlede kendi alıntısında olmayan sayı",
        ),
        ("tolerans düşmüş: ±0,5 cm", "tolerans düşmüş"),
        ("OCR değeri belirsiz: 7O", "OCR değeri belirsiz"),
        ("alıntı [3] kaynakta birebir değil", "alıntı [n] kaynakta birebir değil"),
        ("kod kaynağı [12] geçersiz", "kod kaynağı [n] geçersiz"),
        ("aynı cümle tekrar ediyor", "aynı cümle tekrar ediyor"),
    ],
)
def test_only_the_kind_of_a_diagnosis_is_kept(problem: str, kind: str) -> None:
    assert problem_kind(problem) == kind


def test_repeated_diagnoses_are_kept_once_and_carry_no_answer_values() -> None:
    outcome = ANSWERED.model_copy(
        update={
            "result": Answered(
                status=VerificationStatus.FAILED,
                items=(
                    AnsweredItem(
                        text="PNT-1162 L beden bel 80 cm.",
                        citations=(_citation("a"),),
                        verified=False,
                        problems=("cümlede kaynakta olmayan teknik ad: ['pnt-1162']",),
                    ),
                ),
                problems=("cümlede kaynakta olmayan teknik ad: ['pnt-1162']",),
            )
        }
    )

    record = record_for("Peki L beden?", "text", "answered", outcome, 1.0, None)

    assert record.problems == ("cümlede kaynakta olmayan teknik ad",)
    stored = json.dumps(record.problems, ensure_ascii=False).lower()
    assert "pnt-1162" not in stored and "80" not in stored


def test_existing_records_are_reduced_to_diagnosis_kinds(tmp_path: Path) -> None:
    database = tmp_path / "va.db"
    log = open_log(database)
    old = _record(
        problems=(
            "cümlede kaynakta olmayan teknik ad: ['pnt-1162']",
            "cümlede kaynakta olmayan teknik ad: ['pnt-1162']",
            "alıntı [2] kaynakta birebir değil",
        )
    )

    async def run() -> list[QuestionRecord]:
        await log.migrate()
        await log.add(old)
        await log.migrate()
        await log.migrate()
        return await log.last(1)

    records = asyncio.run(run())

    assert records[0].problems == (
        "cümlede kaynakta olmayan teknik ad",
        "alıntı [n] kaynakta birebir değil",
    )
