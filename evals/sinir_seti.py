"""Sınır seti ölçümü: soruları çalışan uygulamanın `/api/ask` yolundan sorar (bağlamsız, yazılı).

Her koşu × soru için bir satır yazar (JSON lines) ve özet verir. Süre kullanıcının gördüğüdür:
isteğin gönderilmesinden ilk doğrulanmış cümleye. Sınıflar (doğru / güvenli / yanlış) cevap
metni okunarak elle verilir; betik vermez. Kilitli sorular varsayılan olarak sorulmaz (karar
0014). Uygulama önce açılır ve birkaç soruyla ısıtılır (ilk soru modelleri yükler).

    python -m evals.sinir_seti --runs 5 --output evals/output/sinir.jsonl
"""

import argparse
import json
import statistics
import time
from collections import Counter
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import httpx

from apps.api.question_log import percentile

DEFAULT_SET = Path("evals/sinir_yuklu_belgeler.json")
DEFAULT_URL = "http://127.0.0.1:8080"
_TIMEOUT_SECONDS = 120.0


def _events(response: httpx.Response) -> Iterator[dict[str, Any]]:
    for line in response.iter_lines():
        if line.startswith("data: "):
            yield json.loads(line[len("data: ") :])


def ask(client: httpx.Client, question: str) -> dict[str, Any]:
    """Cevabın türü, gösterilen (doğrulanmış) cümleler ve kullanıcının gördüğü süreler."""
    started = time.perf_counter()
    first_verified: float | None = None
    result: dict[str, Any] = {}
    with client.stream("POST", "/api/ask", json={"question": question}) as response:
        response.raise_for_status()
        for event in _events(response):
            if event.get("type") == "item_verified" and first_verified is None:
                first_verified = time.perf_counter() - started
            if event.get("type") == "done":
                result = event.get("result") or {}
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
    }


def summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    times = [row["first_verified"] for row in rows if row["first_verified"] is not None]
    return {
        "cevap": len(rows),
        "tür": dict(Counter(row["kind"] for row in rows)),
        "ilk doğrulanmış cümle": {
            "ortanca": round(statistics.median(times), 2) if times else None,
            "p95": round(percentile(times, 0.95), 2) if times else None,
            "n": len(times),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sınır seti ölçümü (/api/ask üzerinden).")
    parser.add_argument("--set", type=Path, default=DEFAULT_SET)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--with-locked", action="store_true", help="kilitli soruları da sor")
    arguments = parser.parse_args()
    questions = [
        question
        for question in json.loads(arguments.set.read_text(encoding="utf-8"))
        if arguments.with_locked or not question["locked"]
    ]
    rows = []
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    with (
        httpx.Client(base_url=arguments.url, timeout=_TIMEOUT_SECONDS) as client,
        arguments.output.open("w", encoding="utf-8") as output,
    ):
        for run in range(1, arguments.runs + 1):
            for question in questions:
                row = {"run": run, "id": question["id"], **ask(client, question["question"])}
                rows.append(row)
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
                output.flush()
                print(run, row["id"], row["kind"], row["first_verified"], flush=True)
    print(json.dumps(summary(rows), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
