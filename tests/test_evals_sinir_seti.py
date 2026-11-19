import json

import httpx

from apps.api.question_log import percentile
from evals.sinir_seti import ask, summary


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
