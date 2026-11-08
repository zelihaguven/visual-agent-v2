"""İK politikaları: yalnız son sınavda kullanılan, ayar yapılmayan alan."""

from functools import partial
from random import Random

from evals.content import (
    DocumentContent,
    Scenario,
    ScenarioDocument,
    TableBlock,
    TextBlock,
    source_for,
)
from evals.gold import Carrier, GoldDocument, GoldQuestion, Outcome, QuestionKind, Split

DOMAIN = "ik"
ABSENT_TERM = "kreş"
TENURES = ("1-5 yıl", "5-15 yıl", "15 yıl üzeri")
GRADES = ("A", "B", "C")

make_question = partial(GoldQuestion, domain=DOMAIN, split=Split.HOLDOUT)


def _document(
    doc_id: str,
    suffix: str,
    carrier: Carrier,
    title: str,
    blocks: tuple[TextBlock | TableBlock, ...],
) -> ScenarioDocument:
    return ScenarioDocument(
        gold=GoldDocument(
            doc_id=doc_id,
            filename=f"{doc_id}.{suffix}",
            domain=DOMAIN,
            split=Split.HOLDOUT,
            carrier=carrier,
        ),
        content=DocumentContent(title=title, blocks=blocks),
    )


def build_hr_policy(rng: Random) -> Scenario:
    leave_days = [rng.randint(14, 16), rng.randint(20, 22), rng.randint(26, 30)]
    allowances = rng.sample(range(1200, 4800, 50), 3)
    notice_days = rng.randint(14, 56)

    leave = _document(
        "ik-izin",
        "pdf",
        Carrier.PDF,
        "Yıllık İzin Politikası",
        (
            TableBlock(
                title="İzin süreleri",
                headers=("Kıdem", "İzin (gün)"),
                rows=tuple(
                    (tenure, str(days)) for tenure, days in zip(TENURES, leave_days, strict=True)
                ),
            ),
        ),
    )
    allowance = _document(
        "ik-yan-haklar",
        "xlsx",
        Carrier.XLSX,
        "Yan Haklar",
        (
            TableBlock(
                title="Yol yardımı",
                headers=("Derece", "Aylık tutar (TL)"),
                rows=tuple(
                    (grade, str(amount)) for grade, amount in zip(GRADES, allowances, strict=True)
                ),
            ),
        ),
    )
    notice = _document(
        "ik-ihbar",
        "docx",
        Carrier.DOCX,
        "İşten Ayrılma Süreci",
        (TextBlock("İhbar", f"İhbar süresi {notice_days} gündür."),),
    )

    questions = (
        make_question(
            question_id="ik-izin-kidem",
            text=f"{TENURES[1]} kıdemde yıllık izin kaç gün?",
            kind=QuestionKind.TABLE_LOOKUP,
            outcome=Outcome.ANSWERED,
            expected_values=(str(leave_days[1]),),
            evidence=f"{TENURES[1]} {leave_days[1]}",
            sources=(source_for(leave, 0, 1),),
        ),
        make_question(
            question_id="ik-yol-yardimi",
            text=f"{GRADES[2]} derecesinde aylık yol yardımı ne kadar?",
            kind=QuestionKind.TABLE_LOOKUP,
            outcome=Outcome.ANSWERED,
            expected_values=(str(allowances[2]),),
            evidence=f"{GRADES[2]} {allowances[2]}",
            sources=(source_for(allowance, 0, 2),),
        ),
        make_question(
            question_id="ik-ihbar-suresi",
            text="İhbar süresi kaç gün?",
            kind=QuestionKind.DIRECT,
            outcome=Outcome.ANSWERED,
            expected_values=(str(notice_days),),
            evidence=f"İhbar {notice_days}",
            sources=(source_for(notice, 0),),
        ),
        make_question(
            question_id="ik-netlestir",
            text="Yıllık izin kaç gün?",
            kind=QuestionKind.CLARIFY,
            outcome=Outcome.CLARIFY,
            differing_values=tuple(str(days) for days in leave_days),
        ),
        make_question(
            question_id="ik-yok",
            text="Kreş yardımı ne kadar?",
            kind=QuestionKind.NOT_IN_DOCUMENT,
            outcome=Outcome.NOT_FOUND,
            absent_term=ABSENT_TERM,
        ),
    )
    return Scenario(documents=(leave, allowance, notice), questions=questions)
