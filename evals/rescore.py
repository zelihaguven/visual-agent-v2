"""Kayıtlı cevapları modele gitmeden yeniden puanlar.

python -m evals.rescore --set evals/output/set7 --answers evals/output/run7-taban/answers.json
"""

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from evals.gold import GoldSet
from evals.scoring import AnswerRecord, QuestionScore, RunSummary, score_question, summarize


def rescore(
    gold: GoldSet, rows: Sequence[dict[str, Any]]
) -> tuple[list[dict[str, Any]], RunSummary]:
    """Her satırın kayıtlı cevabı bugünkü puanlayıcıyla yeniden puanlanır; sıra altın veridir."""
    by_id = {row["question"]: row for row in rows}
    missing = [q.question_id for q in gold.questions if q.question_id not in by_id]
    if missing:
        raise ValueError(f"cevabı olmayan sorular: {', '.join(missing)}")
    scores: list[QuestionScore] = []
    updated: list[dict[str, Any]] = []
    for question in gold.questions:
        row = by_id[question.question_id]
        record = AnswerRecord.model_validate(row["record"])
        score = score_question(question, record, gold.document_texts)
        scores.append(score)
        updated.append({**row, "score": score.model_dump(mode="json")})
    return updated, summarize(gold.questions, scores)


def main() -> None:
    parser = argparse.ArgumentParser(description="Kayıtlı cevapları yeniden puanlar.")
    parser.add_argument("--set", type=Path, required=True)
    parser.add_argument("--answers", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="yeniden puanlanan satırların yazılacağı dosya")
    arguments = parser.parse_args()
    gold = GoldSet.model_validate_json((arguments.set / "gold.json").read_text(encoding="utf-8"))
    rows = json.loads(arguments.answers.read_text(encoding="utf-8"))
    updated, summary = rescore(gold, rows)
    if arguments.output is not None:
        arguments.output.write_text(
            json.dumps(updated, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    json.dump(summary.model_dump(mode="json"), sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
