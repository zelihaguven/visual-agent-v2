"""Sınır seti ölçümü: soruları çalışan uygulamanın `/api/ask` yolundan sorar (yazılı). Soru
bağlamsızdır; takip turları (`follow_ups`) önceki turun bağlamıyla sorulur (ilk tur netleştirme ya
da "bulunamadı" ise bağlam yoktur, arayüzdeki gibi).

Her koşu × tur için bir satır yazar (JSON lines) ve özet verir. Süre kullanıcının gördüğüdür:
isteğin gönderilmesinden ilk doğrulanmış cümleye. Sınıflar (doğru / güvenli / yanlış) cevap
metni okunarak elle verilir; betik vermez. Uygulama önce açılır ve birkaç soruyla ısıtılır
(ilk soru modelleri yükler).

Sorular arasında beklenir: art arda sorulunca cevap sağlayıcısı istek sınırına takılıyor ve
yedeğe geçiliyor (2026-11-19: yarım saatte 366 soruda Makora 6 kez 429); o zaman süre ölçümü
sağlayıcıyı ölçer. Özet, ölçüm sırasında yedeğe geçen soru sayısını soru günlüğünden okur.

    python -m evals.sinir_seti --runs 5 --output evals/output/sinir.jsonl
"""

import argparse
import asyncio
import json
import statistics
import time
from collections import Counter
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from apps.api.question_log import QuestionRecord, percentile, read_records
from visual_agent.settings import Settings

DEFAULT_SET = Path("evals/sinir_yuklu_belgeler.json")
DEFAULT_URL = "http://127.0.0.1:8080"
_TIMEOUT_SECONDS = 120.0
DEFAULT_PAUSE_SECONDS = 5.0


def _events(response: httpx.Response) -> Iterator[dict[str, Any]]:
    for line in response.iter_lines():
        if line.startswith("data: "):
            yield json.loads(line[len("data: ") :])


def ask(
    client: httpx.Client, question: str, context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Cevabın türü, gösterilen (doğrulanmış) cümleler ve kullanıcının gördüğü süreler.
    context: önceki turun bağlamı (takip sorusu); dönen satırda bu turun bağlamı da var."""
    started = time.perf_counter()
    first_verified: float | None = None
    result: dict[str, Any] = {}
    turn_context: dict[str, Any] | None = None
    body: dict[str, Any] = {"question": question}
    if context is not None:
        body["context"] = context
    with client.stream("POST", "/api/ask", json=body) as response:
        response.raise_for_status()
        for event in _events(response):
            if event.get("type") == "item_verified" and first_verified is None:
                first_verified = time.perf_counter() - started
            if event.get("type") == "done":
                result = event.get("result") or {}
                turn_context = event.get("context")
    items = result.get("items") or []
    return {
        "kind": result.get("kind", "error"),
        "status": result.get("status"),
        "shown": [item["text"] for item in items if item.get("verified") and item.get("text")],
        "hidden": sum(1 for item in items if not item.get("verified")),
        "reason": result.get("reason") or result.get("question"),
        "options": [option.get("label") for option in result.get("options") or []],
        "first_verified": round(first_verified, 3) if first_verified is not None else None,
        "total": round(time.perf_counter() - started, 3),
        "context": turn_context,
    }


def summary(
    rows: Sequence[dict[str, Any]], records: Sequence[QuestionRecord] = ()
) -> dict[str, Any]:
    """records: ölçüm sırasında soru günlüğüne yazılan kayıtlar (sağlayıcı denemeleri için)."""
    times = [row["first_verified"] for row in rows if row["first_verified"] is not None]
    errors = Counter(
        provider for record in records for provider, error in record.provider_errors if error
    )
    return {
        "cevap": len(rows),
        "tür": dict(Counter(row["kind"] for row in rows)),
        "ilk doğrulanmış cümle": {
            "ortanca": round(statistics.median(times), 2) if times else None,
            "p95": round(percentile(times, 0.95), 2) if times else None,
            "n": len(times),
        },
        "yedeğe geçen soru": sum(1 for record in records if record.provider_attempts > 1),
        "sağlayıcı hataları": dict(errors),
    }


def measured_records(records: Sequence[QuestionRecord], since: str) -> list[QuestionRecord]:
    """Ölçüm başladıktan sonra yazılan kayıtlar (ısınma soruları ölçümden önce sorulur)."""
    return [record for record in records if record.created_at >= since]


def main() -> None:
    parser = argparse.ArgumentParser(description="Sınır seti ölçümü (/api/ask üzerinden).")
    parser.add_argument("--set", type=Path, default=DEFAULT_SET)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--pause",
        type=float,
        default=DEFAULT_PAUSE_SECONDS,
        help=f"sorular arasında bekleme, sn (varsayılan {DEFAULT_PAUSE_SECONDS:g})",
    )
    parser.add_argument("--database", type=Path, help="soru günlüğü; varsayılan: VA_DATABASE_PATH")
    arguments = parser.parse_args()
    questions = json.loads(arguments.set.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    since = datetime.now(UTC).isoformat(timespec="milliseconds")
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with (
        # Her soru yeni bağlantıyla: uvicorn boştaki bağlantıyı 5 sn sonra kapatıyor; bekleme
        # (--pause) aynı sürede bitince istemci kapanan bağlantıyı kullanıp düşüyordu.
        httpx.Client(
            base_url=arguments.url,
            timeout=_TIMEOUT_SECONDS,
            limits=httpx.Limits(max_keepalive_connections=0),
        ) as client,
        arguments.output.open("w", encoding="utf-8") as output,
    ):
        for run in range(1, arguments.runs + 1):
            for question in questions:
                # Takip turları (follow_ups) önceki turun bağlamıyla sorulur; satır kimliği "-t2"…
                turns = [
                    question["question"],
                    *(t["question"] for t in question.get("follow_ups", [])),
                ]
                context: dict[str, Any] | None = None
                for number, text in enumerate(turns, start=1):
                    if rows:
                        time.sleep(arguments.pause)
                    turn_id = question["id"] if number == 1 else f"{question['id']}-t{number}"
                    row = {"run": run, "id": turn_id, **ask(client, text, context)}
                    context = row["context"]
                    rows.append(row)
                    output.write(json.dumps(row, ensure_ascii=False) + "\n")
                    output.flush()
                    print(run, row["id"], row["kind"], row["first_verified"], flush=True)
    database = arguments.database or Path(Settings().database_path)
    time.sleep(1.0)  # uygulama son kaydı arka planda yazıyor
    records = measured_records(asyncio.run(read_records(database, len(rows) * 2)), since)
    print(json.dumps(summary(rows, records), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
