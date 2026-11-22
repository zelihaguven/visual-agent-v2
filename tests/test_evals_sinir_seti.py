import json

import httpx

from apps.api.question_log import QuestionRecord, percentile
from evals.sinir_seti import ask, measured_records, summary


def _stream(*events: dict[str, object]) -> httpx.MockTransport:
    body = "".join(f"data: {json.dumps(event, ensure_ascii=False)}\n\n" for event in events)

    def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content) == {"question": "Bel kaç?"}
        return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})

    return httpx.MockTransport(handler)


def test_answer_keeps_only_verified_text_and_first_verified_time() -> None:
    transport = _stream(
        {"type": "item_stream", "index": 0, "text": "Bel …"},
        {"type": "item_verified", "index": 0, "text": "Bel 40,5."},
        {
            "type": "done",
            "result": {
                "kind": "answered",
                "status": "partial",
                "items": [
                    {"text": "Bel 40,5.", "verified": True},
                    {"text": "", "verified": False},
                ],
            },
        },
    )
    with httpx.Client(base_url="http://test", transport=transport) as client:
        row = ask(client, "Bel kaç?")

    assert (row["kind"], row["status"], row["shown"], row["hidden"]) == (
        "answered",
        "partial",
        ["Bel 40,5."],
        1,
    )
    assert row["first_verified"] is not None


def test_clarification_keeps_question_and_options() -> None:
    result = {
        "kind": "clarify",
        "question": "Hangi revizyon için?",
        "options": [{"doc_id": "a", "label": "dikim rev a"}, {"doc_id": "b", "label": "rev b"}],
    }
    with httpx.Client(
        base_url="http://test", transport=_stream({"type": "done", "result": result})
    ) as client:
        row = ask(client, "Bel kaç?")

    assert (row["reason"], row["options"], row["first_verified"]) == (
        "Hangi revizyon için?",
        ["dikim rev a", "rev b"],
        None,
    )


def test_summary_reports_median_and_p95_of_answered_questions() -> None:
    rows = [{"kind": "answered", "first_verified": float(n)} for n in range(1, 21)]
    rows.append({"kind": "not_found", "first_verified": None})

    result = summary(rows)

    assert result["tür"] == {"answered": 20, "not_found": 1}
    assert result["ilk doğrulanmış cümle"] == {"ortanca": 10.5, "p95": 19.0, "n": 20}
    assert percentile([3.0, 1.0, 2.0], 0.95) == 3.0


def _record(created_at: str, attempts: tuple[tuple[str, str], ...]) -> QuestionRecord:
    return QuestionRecord(
        created_at=created_at,
        question="Bel kaç?",
        resolved_question=None,
        input_mode="text",
        result_kind="answered",
        total_seconds=2.0,
        provider_attempts=len(attempts),
        provider_errors=attempts,
    )


def test_summary_counts_questions_that_fell_back_to_another_provider() -> None:
    since = "2026-11-19T09:00:00.000+00:00"
    records = [
        _record("2026-11-19T08:59:59.000+00:00", (("makora", "429: sınır"), ("deepinfra", ""))),
        _record("2026-11-19T09:00:01.000+00:00", (("makora", ""),)),
        _record("2026-11-19T09:00:05.000+00:00", (("makora", "429: sınır"), ("deepinfra", ""))),
        _record("2026-11-19T09:00:09.000+00:00", (("makora", "ilk token"), ("deepinfra", ""))),
    ]

    measured = measured_records(records, since)
    result = summary([{"kind": "answered", "first_verified": 2.0}], measured)

    assert len(measured) == 3  # ısınma sorusu ölçüm başlamadan önce
    assert result["yedeğe geçen soru"] == 2
    assert result["sağlayıcı hataları"] == {"makora": 2}


def test_follow_up_is_asked_with_the_previous_turn_context() -> None:
    seen: list[dict[str, object]] = []
    context = {"question": "6026417 MD paça ağzı kaç?", "doc_ids": ["d"], "titles": ["şort"]}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        done = {"type": "done", "result": {"kind": "answered", "items": []}, "context": context}
        body = f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
        return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"})

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(handler)) as client:
        first = ask(client, "6026417 MD paça ağzı kaç?")
        ask(client, "Peki XL?", first["context"])

    assert first["context"] == context
    assert seen == [
        {"question": "6026417 MD paça ağzı kaç?"},
        {"question": "Peki XL?", "context": context},
    ]
