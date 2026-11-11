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
    assert len(gold.questions) == 15


def test_boundary_values_appear_in_their_documents(boundary: tuple[GoldSet, Path]) -> None:
    gold, _ = boundary

    for question in gold.questions:
        text = gold.document_texts[question.sources[0].doc_id]
        assert all(value in text for value in question.expected_values), question.question_id


def test_boundary_set_does_not_change_the_main_set(tmp_path: Path) -> None:
    main = generate_set(seed=7, output=tmp_path / "ana")

    assert "sinir" not in {document.domain for document in main.documents}
