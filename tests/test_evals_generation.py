from collections.abc import Iterator
from pathlib import Path

import docx
import openpyxl
import pypdfium2
import pytest

from evals.generate import generate_set
from evals.gold import Carrier, GoldSet, Outcome, QuestionKind, Split


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> tuple[GoldSet, Path]:
    output = tmp_path_factory.mktemp("set")
    return generate_set(seed=7, output=output), output


def _page_text(path: Path, page: int) -> str:
    document = pypdfium2.PdfDocument(path)
    try:
        return str(document[page - 1].get_textpage().get_text_bounded())
    finally:
        document.close()


def _docx_text(path: Path) -> str:
    document = docx.Document(str(path))
    cells = [cell.text for table in document.tables for row in table.rows for cell in row.cells]
    return "\n".join([*[p.text for p in document.paragraphs], *cells])


def _questions_with_sources(gold: GoldSet) -> Iterator[tuple[str, str, Carrier, str, int | None]]:
    documents = {document.doc_id: document for document in gold.documents}
    for question in gold.questions:
        for source in question.sources:
            document = documents[source.doc_id]
            for value in question.expected_values:
                yield question.question_id, value, document.carrier, source.doc_id, source.page


def test_set_covers_every_required_case(generated: tuple[GoldSet, Path]) -> None:
    gold, _ = generated

    assert 12 <= len(gold.documents) <= 15
    assert {document.carrier for document in gold.documents} == set(Carrier)
    assert {document.split for document in gold.documents} == set(Split)
    assert {question.kind for question in gold.questions} == set(QuestionKind)
    assert {document.domain for document in gold.documents} == {"dikim", "sql", "ik"}


def test_every_document_is_written(generated: tuple[GoldSet, Path]) -> None:
    gold, output = generated

    assert all((output / document.filename).stat().st_size > 0 for document in gold.documents)


def test_holdout_documents_are_a_separate_domain(generated: tuple[GoldSet, Path]) -> None:
    gold, _ = generated

    holdout = {d.domain for d in gold.documents if d.split is Split.HOLDOUT}
    development = {d.domain for d in gold.documents if d.split is Split.DEVELOPMENT}

    assert holdout == {"ik"}
    assert not holdout & development


def test_expected_values_appear_on_the_claimed_pdf_page(generated: tuple[GoldSet, Path]) -> None:
    gold, output = generated
    documents = {document.doc_id: document for document in gold.documents}
    checked = 0

    for question_id, value, carrier, doc_id, page in _questions_with_sources(gold):
        if carrier is Carrier.PDF:
            assert page is not None, question_id
            assert value in _page_text(output / documents[doc_id].filename, page), question_id
            checked += 1

    assert checked >= 5


def test_every_pdf_content_page_names_its_document(generated: tuple[GoldSet, Path]) -> None:
    gold, output = generated
    checked = 0

    for document in gold.documents:
        if document.carrier is not Carrier.PDF:
            continue
        title = gold.document_texts[document.doc_id].splitlines()[0]
        assert title in _page_text(output / document.filename, 2).replace("\r\n", " "), title
        checked += 1

    assert checked >= 3


def test_expected_values_appear_in_the_claimed_excel_row(generated: tuple[GoldSet, Path]) -> None:
    gold, output = generated
    documents = {document.doc_id: document for document in gold.documents}
    checked = 0

    for question in gold.questions:
        for source in question.sources:
            if documents[source.doc_id].carrier is not Carrier.XLSX:
                continue
            workbook = openpyxl.load_workbook(output / documents[source.doc_id].filename)
            assert source.sheet is not None and source.row is not None
            row = " ".join(str(cell.value) for cell in workbook[source.sheet][source.row])
            for value in question.expected_values:
                assert value in row, question.question_id
                checked += 1

    assert checked >= 3


def test_word_documents_contain_expected_values(generated: tuple[GoldSet, Path]) -> None:
    gold, output = generated
    documents = {document.doc_id: document for document in gold.documents}
    checked = 0

    for question_id, value, carrier, doc_id, _ in _questions_with_sources(gold):
        if carrier is Carrier.DOCX:
            assert value in _docx_text(output / documents[doc_id].filename), question_id
            checked += 1

    assert checked >= 3


def test_scanned_documents_have_no_text_layer(generated: tuple[GoldSet, Path]) -> None:
    gold, output = generated
    scans = [document for document in gold.documents if document.carrier is Carrier.SCAN]

    assert scans
    for document in scans:
        assert _page_text(output / document.filename, 1).strip() == ""


def test_embedded_screenshot_hides_values_from_the_word_text(
    generated: tuple[GoldSet, Path],
) -> None:
    gold, output = generated
    documents = {document.doc_id: document for document in gold.documents}
    image_questions = [
        q
        for q in gold.questions
        if q.sources and documents[q.sources[0].doc_id].carrier is Carrier.SCREENSHOT
    ]

    assert image_questions
    for question in image_questions:
        path = output / documents[question.sources[0].doc_id].filename
        assert docx.Document(str(path)).inline_shapes
        text = _docx_text(path)
        assert not any(value in text for value in question.expected_values)


def test_values_differ_where_clarification_is_required(generated: tuple[GoldSet, Path]) -> None:
    gold, _ = generated
    clarify = [q for q in gold.questions if q.kind is QuestionKind.CLARIFY]

    assert clarify
    for question in clarify:
        assert question.outcome is Outcome.CLARIFY
        assert len(set(question.differing_values)) >= 2


def test_not_found_questions_name_something_absent_from_every_document(
    generated: tuple[GoldSet, Path],
) -> None:
    gold, _ = generated

    for question in gold.questions:
        if question.kind is QuestionKind.NOT_IN_DOCUMENT:
            assert question.outcome is Outcome.NOT_FOUND
            assert question.expected_values == ()
            assert question.absent_term
            assert not any(question.absent_term in text for text in gold.document_texts.values())


def test_conversations_have_ordered_turns(generated: tuple[GoldSet, Path]) -> None:
    gold, _ = generated
    turns: dict[str, list[int]] = {}
    for question in gold.questions:
        if question.conversation_id is not None:
            assert question.turn is not None
            turns.setdefault(question.conversation_id, []).append(question.turn)

    assert len(turns) >= 3
    assert all(values == list(range(1, len(values) + 1)) for values in turns.values())
    assert all(3 <= len(values) <= 5 for values in turns.values())


def test_confirm_question_states_a_value_different_from_the_truth(
    generated: tuple[GoldSet, Path],
) -> None:
    gold, _ = generated
    confirms = [q for q in gold.questions if q.kind is QuestionKind.CONFIRM_WRONG]

    assert confirms
    for question in confirms:
        assert question.outcome is Outcome.ANSWERED
        assert not any(value in question.text for value in question.expected_values)


def test_same_seed_produces_same_gold(tmp_path: Path) -> None:
    first = generate_set(seed=11, output=tmp_path / "a")
    second = generate_set(seed=11, output=tmp_path / "b")

    assert first == second


def test_different_seed_produces_different_values(tmp_path: Path) -> None:
    first = generate_set(seed=11, output=tmp_path / "a")
    second = generate_set(seed=12, output=tmp_path / "b")

    assert first.questions != second.questions


@pytest.fixture(scope="module")
def boundary(tmp_path_factory: pytest.TempPathFactory) -> tuple[GoldSet, Path]:
    output = tmp_path_factory.mktemp("sinir")
    return generate_set(seed=7, output=output, kind="sinir"), output


def test_boundary_set_is_separate_from_the_main_set(boundary: tuple[GoldSet, Path]) -> None:
    gold, output = boundary

    assert {document.domain for document in gold.documents} == {"sinir"}
    assert all((output / document.filename).exists() for document in gold.documents)
    assert len(gold.questions) == 32


def test_boundary_values_appear_in_their_documents(boundary: tuple[GoldSet, Path]) -> None:
    gold, _ = boundary

    for question in gold.questions:
        if question.absent_term is not None:
            texts = gold.document_texts.values()
            assert all(question.absent_term not in text for text in texts), question.question_id
            continue
        text = gold.document_texts[question.sources[0].doc_id]
        assert all(value in text for value in question.expected_values), question.question_id


def test_boundary_set_does_not_change_the_main_set(tmp_path: Path) -> None:
    main = generate_set(seed=7, output=tmp_path / "ana")

    assert "sinir" not in {document.domain for document in main.documents}


def _group_ranges(path: Path) -> set[str]:
    workbook = openpyxl.load_workbook(path)
    return {str(merged) for sheet in workbook.worksheets for merged in sheet.merged_cells.ranges}


def test_group_header_spans_every_size_column(
    generated: tuple[GoldSet, Path], boundary: tuple[GoldSet, Path]
) -> None:
    gold, output = boundary
    model_sheets = next(d for d in gold.documents if d.doc_id == "sinir-model-sayfa")
    main, main_output = generated
    sewing = next(d for d in main.documents if d.carrier is Carrier.XLSX and "dikim" in d.doc_id)

    # Sınır: S, M, L üçü de grup başlığının altında. Dikim: son sütun (tolerans) dışarıda.
    assert _group_ranges(output / model_sheets.filename) == {"B2:D2"}
    assert "B2:D2" in _group_ranges(main_output / sewing.filename)


def test_synthetic_tech_packs_match_their_text_layer_and_are_reproducible(tmp_path: Path) -> None:
    """Doğru cevaptaki her değer dijital PDF'te kendi kutusunda okunur; aynı tohum aynı dosya."""
    from evals.ocr_truth import TruthDocument, ValueKind
    from evals.render.techpack_pdf import generate_set

    first = generate_set(3, 2, tmp_path / "a", "T")  # uyuşmazlıkta hata verir
    second = generate_set(3, 2, tmp_path / "b", "T")

    assert first == second
    truth = TruthDocument.model_validate_json((tmp_path / "a" / "syn1.json").read_text())
    assert [page.page_type for page in truth.pages][0] == "kapak"
    assert len(truth.pages) == 6
    kinds = {value.kind for page in truth.pages for value in page.values}
    assert kinds == {ValueKind.CELL, ValueKind.PAIR, ValueKind.TEXT}
    assert all(value.box is not None for page in truth.pages for value in page.values)


FROZEN_TECHPACK_SEED = 20261116
FROZEN_TECHPACK_SET_A = [
    ("syn1.pdf", "682d60dfc2efaf62e9b109817244062b240a673e150986d10002cc4935d5f62b"),
    ("syn2.pdf", "dbd1d9c935b568546142a12cca8cc550a6a2eb5a0e15d3fae4a652bfc65cdd1b"),
    ("syn3.pdf", "fd7bd0c4183efcbee716f8507f4b658e6a17fad8055361bd17d735b5ba0bb98b"),
    ("syn4.pdf", "6b78a4abb6dfe22b7f39722962de664e6924b95b71adfd5c3956007e79348540"),
    ("syn5.pdf", "dc6d8161a2e6962d34bd54dd3ccdf5e7c322a9f2e80a5f3844dac0fc9ea61c6a"),
    ("syn1.json", "9a06013b66bcfa6d280c7b86a1c6dbc63e195a613427e78a6b0da7ba33955812"),
    ("syn2.json", "660baddaa5eeb87424cb0bf7e90c1c25fc09b78d449566872a890d4aae120262"),
    ("syn3.json", "b48b5d3067ac25e43ca8eb5c7e1f7d80e44341b2912719ce030d8fa2ac24f169"),
    ("syn4.json", "a1bdba76db5a0f9cb0d5fdffe4b7f5890287fe474b2ebaaf9e8e70c132aec93a"),
    ("syn5.json", "d024099e7a85e7408a8d0caec816e8a068aae792b651423fa495ae464a29e24e"),
]
"""Kilitli set A (2026-11-16): hiçbir okuyucu çalıştırılmadan donduruldu. Üretici, yazı tipi ya da
reportlab değişip dosyalar değişirse bu test kırılır; set A'nın sonuçları o zaman geçersizdir ve
yeni bir tohumla yeni set üretilir (sonuçlara bakıp üretici değiştirilmez)."""


FROZEN_TECHPACK_DIR = Path(__file__).parent.parent / "evals" / "assets" / "techpack_set_a"
"""Basılıp taranan dosyalar bunlardır; kütüphane sürümü değişince yeniden üretilemeyebilirler."""


def test_committed_set_a_files_are_the_frozen_ones() -> None:
    import hashlib

    committed = [
        (name, hashlib.sha256((FROZEN_TECHPACK_DIR / name).read_bytes()).hexdigest())
        for name, _ in FROZEN_TECHPACK_SET_A
    ]
    assert committed == FROZEN_TECHPACK_SET_A


def test_generator_still_reproduces_set_a(tmp_path: Path) -> None:
    from evals.render.techpack_pdf import generate_set

    assert generate_set(FROZEN_TECHPACK_SEED, 5, tmp_path, "A") == FROZEN_TECHPACK_SET_A
