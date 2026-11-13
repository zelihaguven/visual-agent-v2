"""Doğrudan cevap yoksa getirilen parçaların başlıkları gösterilir; içerik aktarılmaz."""

from tests.test_ask_pipeline import FakeClient, FakeRetriever, ask, chunk, make_deps
from visual_agent.ask.related import with_related_headings
from visual_agent.domain.document import ChunkKind
from visual_agent.domain.result import Answered, ClarifyChoice, Hit, NotFound

NOT_FOUND = {"tur": "bulunamadi", "cevap": [], "celiski_var": False}


def _hit(chunk_id: str, doc_id: str, title: str, section: str = "") -> Hit:
    item = chunk(chunk_id, doc_id, "Gizli içerik 42", ChunkKind.TEXT, title=title)
    return Hit(chunk=item.model_copy(update={"section": section}), score=1.0)


def test_not_found_lists_headings_of_retrieved_parts() -> None:
    hits = [
        _hit("a:1", "a", "Kılavuz", "Kılavuz · Dışa aktarma"),
        _hit("a:2", "a", "Kılavuz", "Kılavuz · Dışa aktarma"),
        _hit("b:1", "b", "Ürünler"),
    ]

    result = with_related_headings(NotFound(), hits, "tr")

    assert isinstance(result, NotFound)
    assert result.reason == (
        "Doğrudan cevap bulunamadı. Aramada en yakın çıkan başlıklar: "
        "Kılavuz · Dışa aktarma; Ürünler."
    )
    assert result.suggestions == ()  # en yakın belgeler yalnız metin; düğme değil
    assert "42" not in result.reason


def test_at_most_four_headings_in_the_question_language() -> None:
    hits = [_hit(f"{n}:1", str(n), f"Başlık {n}") for n in range(6)]

    result = with_related_headings(NotFound(), hits, "en")

    assert isinstance(result, NotFound)
    assert result.reason.startswith("No direct answer was found.")
    assert result.reason.count(";") == 3


def test_other_results_and_reasoned_not_found_are_kept() -> None:
    hits = [_hit("a:1", "a", "Kılavuz")]
    reasoned = NotFound(
        reason="PNT-1 belgelerde geçmiyor.", suggestions=(ClarifyChoice(doc_id="x", label="X"),)
    )

    assert with_related_headings(reasoned, hits, "tr") == reasoned
    assert with_related_headings(NotFound(), [], "tr") == NotFound()


def test_pipeline_not_found_carries_the_headings() -> None:
    retriever = FakeRetriever(
        hits=[chunk("b:1", "b", "E050 açıklaması", ChunkKind.TEXT, "Kılavuz")]
    )

    outcome = ask(make_deps(FakeClient(NOT_FOUND), retriever), "SAP entegrasyonu nasıl?")

    assert isinstance(outcome.result, NotFound)
    assert outcome.result.reason.endswith("başlıklar: Kılavuz.")


def test_pipeline_answer_is_untouched() -> None:
    payload = {
        "tur": "cevap",
        "cevap": [{"alintilar": [{"kaynak_no": 1, "metin": "Beden M: 76,5"}], "metin": "76,5."}],
        "celiski_var": False,
    }

    assert isinstance(ask(make_deps(FakeClient(payload)), "İç paça kaç?").result, Answered)
