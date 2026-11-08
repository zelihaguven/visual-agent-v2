"""Üretilen setin belge işlemeden doğru kaynakla çıktığını ölçer (işçi imajında çalışır)."""

import argparse
import json
import tempfile
import time
from collections import Counter
from collections.abc import Sequence
from pathlib import Path

from evals.gold import GoldQuestion, GoldSet, GoldSource
from evals.scoring import extract_tokens
from visual_agent.domain.document import Chunk, DocumentMeta


def source_matches(chunk: Chunk, source: GoldSource) -> bool:
    if chunk.doc_id != source.doc_id:
        return False
    location = chunk.location
    return (
        (source.page is None or location.page == source.page)
        and (source.sheet is None or location.sheet == source.sheet)
        and (source.row is None or location.row == source.row)
    )


def question_found(question: GoldQuestion, chunks: Sequence[Chunk]) -> bool:
    """Her beklenen değer, doğru konumdaki parçalardan birinde bulunmalıdır."""
    expected = frozenset().union(*(extract_tokens(value) for value in question.expected_values))
    candidates = [c for c in chunks if any(source_matches(c, s) for s in question.sources)]
    available = (
        frozenset().union(*(extract_tokens(chunk.text) for chunk in candidates))
        if candidates
        else frozenset()
    )
    return expected <= available


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


def run(set_directory: Path) -> dict[str, object]:
    from visual_agent.ingest.pipeline import ingest_document
    from visual_agent.ingest.tools import default_tools

    gold = GoldSet.model_validate_json((set_directory / "gold.json").read_text(encoding="utf-8"))
    tools = default_tools()
    chunks: dict[str, tuple[Chunk, ...]] = {}
    per_document: list[dict[str, object]] = []
    for document in gold.documents:
        started = time.perf_counter()
        with tempfile.TemporaryDirectory() as work:
            result = ingest_document(
                set_directory / document.filename,
                DocumentMeta(doc_id=document.doc_id, title=Path(document.filename).stem),
                tools,
                Path(work),
            )
        chunks[document.doc_id] = result.chunks
        per_document.append(
            {
                "doc_id": document.doc_id,
                "carrier": document.carrier.value,
                "seconds": round(time.perf_counter() - started, 1),
                "report": result.report.model_dump(),
            }
        )
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
        "unsafe_tokens": {key: value for key, value in unsafe.items() if value},
        "blocked_expected_values": {key: value for key, value in blocked.items() if value},
        "by_carrier": {carrier: [found[carrier], totals[carrier]] for carrier in sorted(totals)},
        "missing": missing,
        "documents": per_document,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Belge işleme kapsamını ölçer.")
    parser.add_argument("--set", type=Path, default=Path("evals/output/set"))
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.set), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
