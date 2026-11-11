"""Test setini üretir: python -m evals.generate --seed 7 --output evals/output/set."""

import argparse
import tempfile
from pathlib import Path
from random import Random

from evals.content import Scenario, ScenarioDocument
from evals.gold import Carrier, GoldSet
from evals.render.imaging import write_photo, write_scan
from evals.render.office import render_docx, render_sql_text, render_xlsx
from evals.render.pdf import render_pdf
from evals.scenarios.boundary import build_boundary
from evals.scenarios.hr_policy import build_hr_policy
from evals.scenarios.sewing import build_sewing
from evals.scenarios.sql_tool import build_sql_tool

GOLD_FILENAME = "gold.json"
KINDS = ("standart", "sinir")


def _render_via_pdf(document: ScenarioDocument, target: Path, rng: Random) -> None:
    with tempfile.TemporaryDirectory() as directory:
        pdf_path = Path(directory) / "source.pdf"
        render_pdf(document.content, pdf_path)
        if document.gold.carrier is Carrier.SCAN:
            write_scan(pdf_path, target, rng)
        else:
            write_photo(pdf_path, target, rng)


def _render(document: ScenarioDocument, output: Path, rng: Random) -> None:
    target = output / document.gold.filename
    content = document.content
    match document.gold.carrier:
        case Carrier.PDF:
            render_pdf(content, target)
        case Carrier.DOCX:
            render_docx(content, target)
        case Carrier.SCREENSHOT:
            render_docx(content, target, tables_as_images=True)
        case Carrier.XLSX:
            render_xlsx(content, target)
        case Carrier.SQL_TEXT:
            render_sql_text(content, target)
        case Carrier.SCAN | Carrier.PHOTO:
            _render_via_pdf(document, target, rng)


def _scenarios(seed: int, kind: str) -> tuple[Scenario, ...]:
    """ "standart" ana settir; "sinir" doğrulamanın sayı kurallarını sınayan ayrı settir."""
    if kind == "sinir":
        return (build_boundary(),)
    return (
        build_sewing(Random(f"{seed}:dikim")),
        build_sql_tool(Random(f"{seed}:sql")),
        build_hr_policy(Random(f"{seed}:ik")),
    )


def generate_set(seed: int, output: Path, kind: str = "standart") -> GoldSet:
    output.mkdir(parents=True, exist_ok=True)
    scenarios = _scenarios(seed, kind)
    documents = [document for scenario in scenarios for document in scenario.documents]
    render_rng = Random(f"{seed}:render")
    for document in documents:
        _render(document, output, render_rng)
    gold = GoldSet(
        seed=seed,
        documents=tuple(document.gold for document in documents),
        questions=tuple(question for scenario in scenarios for question in scenario.questions),
        document_texts={
            document.gold.doc_id: document.content.full_text() for document in documents
        },
    )
    (output / GOLD_FILENAME).write_text(gold.model_dump_json(indent=2), encoding="utf-8")
    return gold


def main() -> None:
    parser = argparse.ArgumentParser(description="Test belgelerini ve doğru cevapları üretir.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", type=Path, default=Path("evals/output/set"))
    parser.add_argument("--kind", choices=KINDS, default="standart")
    arguments = parser.parse_args()
    gold = generate_set(arguments.seed, arguments.output, arguments.kind)
    print(f"{len(gold.documents)} belge, {len(gold.questions)} soru: {arguments.output}")


if __name__ == "__main__":
    main()
