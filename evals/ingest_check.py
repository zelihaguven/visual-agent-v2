"""Üretilen setin belge işlemeden doğru kaynakla çıktığını ölçer (işçi imajında çalışır).

Parçalar run_questions ile aynı önbellekten (--work) okunur: önbellek varsa belgeler yeniden
işlenmez. İşleme kodunu ölçmek için boş bir --work verin. İşlenemeyen belge varsa önbellek
yazılmaz (run_questions o klasörde durur); sonraki koşu bütün belgeleri yeniden işler.
"""

import argparse
import json
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from evals.gold import GoldQuestion, GoldSet
from evals.index_cache import load_or_ingest
from evals.run_questions import gold_documents
from evals.scoring import extract_tokens, question_found
from visual_agent.domain.document import Chunk


def unsafe_tokens(chunks: Sequence[Chunk], truth: str) -> list[str]:
    """OCR'dan gelen, belgede olmayan ve belirsiz işaretlenmemiş değerler: 0 olmalı."""
    known = extract_tokens(truth)
    unsafe: list[str] = []
    for chunk in chunks:
        if chunk.from_ocr:
            flagged = extract_tokens(" ".join(chunk.ocr_uncertain))
            unsafe += sorted(extract_tokens(chunk.text) - known - flagged)
    return unsafe


def blocked_values(question: GoldQuestion, chunks: Sequence[Chunk]) -> list[str]:
    """Doğru okunduğu halde belirsiz işaretlenip cevabı engelleyecek beklenen değerler."""
    flagged = extract_tokens(" ".join(token for chunk in chunks for token in chunk.ocr_uncertain))
    return [value for value in question.expected_values if extract_tokens(value) <= flagged]


def run(set_directory: Path, work: Path) -> dict[str, object]:
    """Belgeler run_questions ile aynı biçimde ve aynı parça önbelleğiyle işlenir."""
    gold = GoldSet.model_validate_json((set_directory / "gold.json").read_text(encoding="utf-8"))
    work.mkdir(parents=True, exist_ok=True)
    found_chunks, manifest = load_or_ingest(
        gold_documents(gold, set_directory), work, keep_partial=False
    )
    chunks = {document.doc_id: found_chunks.get(document.doc_id, []) for document in gold.documents}
    per_document = [
        {"doc_id": document.doc_id, "carrier": document.carrier.value, **info}
        for document in gold.documents
        if (info := manifest.get("per_document", {}).get(document.doc_id)) is not None
    ]
    carriers = {document.doc_id: document.carrier.value for document in gold.documents}
    totals: Counter[str] = Counter()
    found: Counter[str] = Counter()
    missing: list[dict[str, object]] = []
    for question in gold.questions:
        if not question.sources:
            continue
        carrier = carriers[question.sources[0].doc_id]
        relevant = [c for s in question.sources for c in chunks[s.doc_id]]
        totals[carrier] += 1
        if question_found(question, relevant):
            found[carrier] += 1
        else:
            missing.append(
                {
                    "question": question.question_id,
                    "carrier": carrier,
                    "expected": list(question.expected_values),
                    "sources": [s.model_dump(exclude_none=True) for s in question.sources],
                    "sample": [c.text[:140] for c in relevant[:4]],
                }
            )
    unsafe = {
        document.doc_id: unsafe_tokens(
            chunks[document.doc_id], gold.document_texts[document.doc_id]
        )
        for document in gold.documents
    }
    blocked = {
        question.question_id: blocked_values(
            question, [c for s in question.sources for c in chunks[s.doc_id]]
        )
        for question in gold.questions
        if question.sources
    }
    return {
        "errors": manifest.get("errors", {}),
        "unsafe_tokens": {key: value for key, value in unsafe.items() if value},
        "blocked_expected_values": {key: value for key, value in blocked.items() if value},
        "by_carrier": {carrier: [found[carrier], totals[carrier]] for carrier in sorted(totals)},
        "missing": missing,
        "documents": per_document,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Belge işleme kapsamını ölçer.")
    parser.add_argument("--set", type=Path, required=True)
    parser.add_argument(
        "--work",
        type=Path,
        required=True,
        help="o setin parça önbelleği (run_questions ile aynı klasör); önbellek varsa belgeler "
        "yeniden işlenmez, işleme kodunu ölçmek için boş bir klasör verin",
    )
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.set, arguments.work), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
