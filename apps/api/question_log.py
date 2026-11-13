"""Soru kaydı: her soru SQLite'a yazılır, gecikme kararı bu kayıttan verilir.

Kaydedilenler: zaman, kullanıcının sorusu ve tamamlanmış hali, sonuç türü, doğrulama durumu ve
sorunlar, atıf yapılan belgeler, sağlayıcı, maliyet, ilk doğrulanmış cümleye kadar geçen süre,
sesli ya da yazılı oluşu ve adım adım süreler. Ses ve cevap metninin tamamı yazılmaz.
Kayıt başarısız olursa cevap etkilenmez. Okumak için HTTP ucu yoktur:

    python -m apps.api.question_log --last 20
"""

import argparse
import json
import logging
import re
import sqlite3
import statistics
from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from visual_agent.catalog.repository import SqliteDatabase
from visual_agent.domain.result import Answered, AskOutcome
from visual_agent.settings import Settings

logger = logging.getLogger(__name__)

InputMode = Literal["text", "voice"]
ERROR_KIND = "error"
STEP_LABELS = {
    "context": "takip tamamlama",
    "scope": "kapsam",
    "intent": "niyet",
    "translate": "çeviri",
    "retrieve": "arama",
    "generate": "cevap modeli",
    "verify": "doğrulama",
}
_SCHEMA = """
CREATE TABLE IF NOT EXISTS question_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    question TEXT NOT NULL,
    resolved_question TEXT,
    input_mode TEXT NOT NULL,
    result_kind TEXT NOT NULL,
    verification_status TEXT,
    problems TEXT NOT NULL,
    cited_doc_ids TEXT NOT NULL,
    provider TEXT,
    cost_usd REAL NOT NULL,
    first_verified_seconds REAL,
    total_seconds REAL NOT NULL,
    timings TEXT NOT NULL,
    provider_attempts INTEGER NOT NULL DEFAULT 0,
    provider_wait_seconds REAL
);
CREATE INDEX IF NOT EXISTS question_log_time_idx ON question_log (created_at);
"""
_SOURCE_NUMBER = re.compile(r"\[\d+\]")


def problem_kind(problem: str) -> str:
    """Tanının yalnız türü kalır: cevaptaki sayı, kod ya da alıntı kayda girmez."""
    return _SOURCE_NUMBER.sub("[n]", problem.split(":", 1)[0]).strip()


def problem_kinds(problems: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(problem_kind(problem) for problem in problems))


_COLUMNS = (
    "created_at, question, resolved_question, input_mode, result_kind, verification_status,"
    " problems, cited_doc_ids, provider, cost_usd, first_verified_seconds, total_seconds, timings,"
    " provider_attempts, provider_wait_seconds"
)
_ADDED_COLUMNS = {
    "provider_attempts": "INTEGER NOT NULL DEFAULT 0",
    "provider_wait_seconds": "REAL",
}


class QuestionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    created_at: str
    question: str
    resolved_question: str | None
    input_mode: InputMode
    result_kind: str
    verification_status: str | None = None
    problems: tuple[str, ...] = ()
    cited_doc_ids: tuple[str, ...] = ()
    provider: str | None = None
    cost_usd: float = 0.0
    first_verified_seconds: float | None = None
    total_seconds: float
    timings: dict[str, float] = {}
    provider_attempts: int = 0
    provider_wait_seconds: float | None = None


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def record_for(
    question: str,
    input_mode: InputMode,
    kind: str,
    outcome: AskOutcome | None,
    total_seconds: float,
    first_verified_seconds: float | None,
    follow_up: bool = False,
) -> QuestionRecord:
    """Cevabın metni değil, türü, doğrulaması ve atıf yaptığı belgeler kaydedilir.

    Takip tamamlama süresi yalnız bağlamla gelen soruda anlamlıdır; diğerlerinde yazılmaz.
    """
    if outcome is None:
        return QuestionRecord(
            created_at=_now(),
            question=question,
            resolved_question=None,
            input_mode=input_mode,
            result_kind=ERROR_KIND,
            total_seconds=total_seconds,
        )
    result = outcome.result
    answered = result if isinstance(result, Answered) else None
    problems = (
        (*answered.problems, *(p for item in answered.items for p in item.problems))
        if answered
        else ()
    )
    cited = (
        tuple(dict.fromkeys(c.doc_id for item in answered.items for c in item.citations))
        if answered
        else ()
    )
    return QuestionRecord(
        created_at=_now(),
        question=question,
        resolved_question=outcome.question if outcome.question != question else None,
        input_mode=input_mode,
        result_kind=kind,
        verification_status=answered.status.value if answered else None,
        problems=problem_kinds(problems),
        cited_doc_ids=cited,
        provider=outcome.provider,
        cost_usd=outcome.cost_usd,
        first_verified_seconds=first_verified_seconds,
        total_seconds=total_seconds,
        timings={
            step: seconds
            for step, seconds in outcome.timings.items()
            if follow_up or step != "context"
        },
        provider_attempts=outcome.provider_attempts,
        provider_wait_seconds=outcome.provider_seconds if outcome.provider_attempts else None,
    )


def _row_values(record: QuestionRecord) -> tuple[object, ...]:
    return (
        record.created_at,
        record.question,
        record.resolved_question,
        record.input_mode,
        record.result_kind,
        record.verification_status,
        json.dumps(list(record.problems), ensure_ascii=False),
        json.dumps(list(record.cited_doc_ids)),
        record.provider,
        record.cost_usd,
        record.first_verified_seconds,
        record.total_seconds,
        json.dumps(record.timings),
        record.provider_attempts,
        record.provider_wait_seconds,
    )


def _from_row(row: sqlite3.Row) -> QuestionRecord:
    return QuestionRecord(
        created_at=row["created_at"],
        question=row["question"],
        resolved_question=row["resolved_question"],
        input_mode=row["input_mode"],
        result_kind=row["result_kind"],
        verification_status=row["verification_status"],
        problems=tuple(json.loads(row["problems"])),
        cited_doc_ids=tuple(json.loads(row["cited_doc_ids"])),
        provider=row["provider"],
        cost_usd=row["cost_usd"],
        first_verified_seconds=row["first_verified_seconds"],
        total_seconds=row["total_seconds"],
        timings=json.loads(row["timings"]),
        provider_attempts=row["provider_attempts"],
        provider_wait_seconds=row["provider_wait_seconds"],
    )


def _add_missing_columns(connection: sqlite3.Connection) -> None:
    """Önceki sürümde açılmış tabloya sonradan eklenen sütunlar eklenir."""
    present = {row[1] for row in connection.execute("PRAGMA table_info(question_log)")}
    for name, definition in _ADDED_COLUMNS.items():
        if name not in present:
            connection.execute(f"ALTER TABLE question_log ADD COLUMN {name} {definition}")


# Veritabanı dosyası belge kataloğuyla ortaktır; `user_version` yalnız soru kaydının tek
# seferlik göçlerini sayar (katalog kullanmaz).
_LOG_VERSION = 1


def _reduce_stored_problems(connection: sqlite3.Connection) -> int:
    """Eski kayıtlardaki tam tanı metinleri türlerine indirilir; dosya başına bir kez çalışır."""
    if connection.execute("PRAGMA user_version").fetchone()[0] >= _LOG_VERSION:
        return 0
    changed = 0
    for row_id, stored in connection.execute("SELECT id, problems FROM question_log").fetchall():
        reduced = json.dumps(list(problem_kinds(json.loads(stored))), ensure_ascii=False)
        if reduced != stored:
            connection.execute(
                "UPDATE question_log SET problems = ? WHERE id = ?", (reduced, row_id)
            )
            changed += 1
    connection.execute(f"PRAGMA user_version = {_LOG_VERSION}")
    return changed


class QuestionLog:
    def __init__(self, database: SqliteDatabase) -> None:
        self._db = database

    async def migrate(self) -> None:
        await self._db.migrate(_SCHEMA)
        await self._db.run(_add_missing_columns)
        await self._db.run(_reduce_stored_problems)

    async def add(self, record: QuestionRecord) -> None:
        values = _row_values(record)
        await self._db.run(
            lambda connection: connection.execute(
                f"INSERT INTO question_log ({_COLUMNS}) VALUES ({', '.join('?' * len(values))})",  # noqa: S608
                values,
            )
        )

    async def record(self, record: QuestionRecord) -> None:
        """Kayıt başarısız olsa da soru cevabı etkilenmez; yalnız uyarı yazılır."""
        try:
            await self.add(record)
        except Exception:
            logger.warning("Soru kaydı yazılamadı", exc_info=True)

    async def last(self, count: int) -> list[QuestionRecord]:
        rows = await self._db.run(
            lambda connection: connection.execute(
                f"SELECT {_COLUMNS} FROM question_log ORDER BY id DESC LIMIT ?",  # noqa: S608
                (count,),
            ).fetchall()
        )
        return [_from_row(row) for row in rows]


def _seconds(values: Sequence[float]) -> str:
    if not values:
        return "-"
    ordered = sorted(values)
    p90 = ordered[min(len(ordered) - 1, round(0.9 * (len(ordered) - 1)))]
    return f"ortanca {statistics.median(ordered):.2f} sn, p90 {p90:.2f} sn ({len(ordered)} soru)"


def summary_lines(records: Sequence[QuestionRecord]) -> list[str]:
    """Sonuç türü ve adım sürelerinin özeti; adım yalnız çalıştığı sorularda sayılır."""
    if not records:
        return ["Kayıt yok."]
    kinds = Counter(record.result_kind for record in records)
    modes = Counter(record.input_mode for record in records)
    lines = [
        f"{len(records)} soru: "
        + ", ".join(f"{kind} {count}" for kind, count in kinds.most_common()),
        "giriş: " + ", ".join(f"{mode} {count}" for mode, count in modes.most_common()),
        f"toplam süre: {_seconds([r.total_seconds for r in records])}",
        "ilk doğrulanmış cümle: "
        + _seconds([r.first_verified_seconds for r in records if r.first_verified_seconds]),
    ]
    steps = [step for step in STEP_LABELS if any(step in r.timings for r in records)]
    for step in steps:
        values = [record.timings[step] for record in records if step in record.timings]
        lines.append(f"  {STEP_LABELS[step]}: {_seconds(values)}")
    asked = [record for record in records if record.provider_attempts]
    retried = [record for record in asked if record.provider_attempts > 1]
    if asked:
        lines.append(
            f"birden çok sağlayıcı denemesi: {len(retried)}/{len(asked)} soru"
            f" (%{100 * len(retried) / len(asked):.0f}); sağlayıcı bekleme "
            + _seconds([r.provider_wait_seconds for r in asked if r.provider_wait_seconds])
        )
    cost = sum(record.cost_usd for record in records)
    lines.append(f"maliyet: {cost:.5f} $")
    return lines


def _optional_seconds(value: float | None) -> str:
    return f"{value:5.2f} sn" if value is not None else "    -   "


def record_lines(records: Sequence[QuestionRecord]) -> list[str]:
    return [
        f"{r.created_at}  {r.input_mode:<5}  {r.result_kind:<10}"
        f"  {r.verification_status or '-':<9}  {r.total_seconds:5.2f} sn"
        f"  ilk {_optional_seconds(r.first_verified_seconds)}  {r.provider or '-':<10}"
        f"  {r.question[:70]}"
        for r in records
    ]


def open_log(path: Path) -> QuestionLog:
    return QuestionLog(SqliteDatabase(path))


async def _read(path: Path, count: int) -> list[QuestionRecord]:
    """Yalnız okur: açık uygulamanın tablosunu değiştirmez (göç uygulama açılırken yapılır)."""
    if not path.exists():
        return []
    try:
        return await open_log(path).last(count)
    except sqlite3.OperationalError as error:
        raise SystemExit(f"Soru kaydı okunamadı ({error}); uygulamayı bir kez açın.") from error


def main() -> None:
    import asyncio

    parser = argparse.ArgumentParser(description="Son soru kayıtlarını ve süre özetini döker.")
    parser.add_argument("--last", type=int, default=20, help="kaç kayıt")
    parser.add_argument("--database", type=Path, help="varsayılan: VA_DATABASE_PATH")
    arguments = parser.parse_args()
    path = arguments.database or Path(Settings().database_path)
    records = asyncio.run(_read(path, arguments.last))
    print("\n".join([*record_lines(records), "", *summary_lines(records)]))


if __name__ == "__main__":
    main()
