"""Dikim departmanı: ölçü föyleri ve etiketler."""

from dataclasses import dataclass, replace
from functools import partial
from random import Random

from evals.content import DocumentContent, Scenario, ScenarioDocument, TableBlock, source_for
from evals.gold import (
    Carrier,
    GoldDocument,
    GoldQuestion,
    GoldSource,
    Mess,
    Outcome,
    QuestionKind,
)

DOMAIN = "dikim"
SIZES = ("S", "M", "L")
MEASURES = ("İç paça", "Dış paça", "Bel", "Kalça")
BASE_CM = {"İç paça": 74.0, "Dış paça": 102.0, "Bel": 38.0, "Kalça": 48.0}
SIZE_OFFSET = {"S": -2.0, "M": 0.0, "L": 2.0}
ABSENT_TERM = "ordon boyu"
FILE_SUFFIX = {Carrier.PHOTO: "jpg", Carrier.DOCX: "docx", Carrier.XLSX: "xlsx"}
IMAGE_CARRIERS = (Carrier.SCAN, Carrier.PHOTO)

make_question = partial(GoldQuestion, domain=DOMAIN)


def _cm(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


@dataclass(frozen=True)
class Spec:
    doc_id: str
    model: str
    carrier: Carrier
    bases: dict[str, float]
    tolerance: str
    labels: dict[str, str]
    mess: tuple[Mess, ...] = ()
    revision: str = ""
    measure_header: str = "Ölçü noktası"
    has_labels: bool = True

    def value(self, size: str, measure: str) -> str:
        return _cm(self.bases[measure] + SIZE_OFFSET[size])


def _random_bases(rng: Random) -> dict[str, float]:
    return {measure: base + rng.randint(0, 6) * 0.5 for measure, base in BASE_CM.items()}


def _random_labels(rng: Random) -> dict[str, str]:
    start = rng.randint(1000, 9000)
    return {size: f"ETK-{start + index}" for index, size in enumerate(SIZES)}


def _document(spec: Spec) -> ScenarioDocument:
    measure_rows = tuple(
        (measure, *(spec.value(size, measure) for size in SIZES), spec.tolerance)
        for measure in MEASURES
    )
    measures = TableBlock(
        title="Ölçü tablosu",
        headers=(spec.measure_header, *SIZES, "Tolerans (cm)"),
        rows=measure_rows,
        group_header="Beden",
        group_width=len(SIZES),
    )
    labels = TableBlock(
        title="Etiket kodları",
        headers=("Beden", "Etiket kodu"),
        rows=tuple((size, spec.labels[size]) for size in SIZES),
    )
    suffix = FILE_SUFFIX.get(spec.carrier, "pdf")
    title = f"{spec.model} ölçü föyü {spec.revision}".strip()
    return ScenarioDocument(
        gold=GoldDocument(
            doc_id=spec.doc_id,
            filename=f"{spec.doc_id}.{suffix}",
            domain=DOMAIN,
            carrier=spec.carrier,
            mess=spec.mess,
        ),
        content=DocumentContent(
            title=title, blocks=(measures, labels) if spec.has_labels else (measures,)
        ),
    )


def _measure_source(document: ScenarioDocument, measure: str) -> GoldSource:
    return source_for(document, 0, MEASURES.index(measure))


def _measure_evidence(spec: Spec, size: str, measure: str) -> str:
    return f"{spec.model} {size} {measure} {spec.value(size, measure)} cm ±{spec.tolerance}"


def _lookup_fields(
    spec: Spec, document: ScenarioDocument, size: str, measure: str
) -> dict[str, object]:
    return {
        "outcome": Outcome.ANSWERED,
        "expected_values": (spec.value(size, measure),),
        "evidence": _measure_evidence(spec, size, measure),
        "sources": (_measure_source(document, measure),),
    }


def _label_fields(spec: Spec, document: ScenarioDocument, size: str) -> dict[str, object]:
    return {
        "outcome": Outcome.ANSWERED,
        "expected_values": (spec.labels[size],),
        "evidence": f"{spec.model} {size} {spec.labels[size]}",
        "sources": (source_for(document, 1, SIZES.index(size)),),
    }


def _not_found(question_id: str, text: str, **extra: object) -> GoldQuestion:
    return make_question(
        question_id=question_id,
        text=text,
        kind=QuestionKind.NOT_IN_DOCUMENT,
        outcome=Outcome.NOT_FOUND,
        absent_term=ABSENT_TERM,
        **extra,
    )


def _single_questions(spec: Spec, document: ScenarioDocument, rng: Random) -> list[GoldQuestion]:
    size, measure = rng.choice(SIZES), rng.choice(MEASURES)
    kind = QuestionKind.IN_IMAGE if spec.carrier in IMAGE_CARRIERS else QuestionKind.TABLE_LOOKUP
    questions = [
        make_question(
            question_id=f"{spec.doc_id}-olcu",
            text=f"{spec.model} modelinde {size} beden {measure.lower()} kaç?",
            kind=kind,
            **_lookup_fields(spec, document, size, measure),
        ),
        _not_found(f"{spec.doc_id}-yok", f"{spec.model} modelinde kordon boyu kaç?"),
    ]
    if spec.has_labels:
        questions.append(
            make_question(
                question_id=f"{spec.doc_id}-etiket",
                text=f"{spec.model} {size} beden için hangi etiket takılıyor?",
                kind=QuestionKind.DIRECT,
                **_label_fields(spec, document, size),
            )
        )
    return questions


def _clarify(spec: Spec, measure: str) -> GoldQuestion:
    return make_question(
        question_id=f"{spec.doc_id}-netlestir",
        text=f"{spec.model} modelinde {measure.lower()} kaç?",
        kind=QuestionKind.CLARIFY,
        outcome=Outcome.CLARIFY,
        differing_values=tuple(spec.value(size, measure) for size in SIZES),
    )


def _confirm_wrong(spec: Spec, document: ScenarioDocument) -> GoldQuestion:
    measure = "İç paça"
    wrong = _cm(spec.bases[measure] + SIZE_OFFSET["M"] + 2.0)
    return make_question(
        question_id=f"{spec.doc_id}-yanlis-onay",
        text=f"{spec.model} M beden iç paça {wrong} cm miydi?",
        kind=QuestionKind.CONFIRM_WRONG,
        **_lookup_fields(spec, document, "M", measure),
    )


def _conversation_with_model_switch(
    first: Spec, first_doc: ScenarioDocument, second: Spec, second_doc: ScenarioDocument
) -> list[GoldQuestion]:
    conversation = {"conversation_id": "dikim-sohbet-1"}
    value = first.value("M", "İç paça")
    return [
        make_question(
            question_id="dikim-sohbet-1-t1",
            text=f"{first.model} M beden iç paça {value} cm miydi?",
            kind=QuestionKind.TABLE_LOOKUP,
            turn=1,
            **conversation,
            **_lookup_fields(first, first_doc, "M", "İç paça"),
        ),
        make_question(
            question_id="dikim-sohbet-1-t2",
            text="Peki dış paça kaç?",
            kind=QuestionKind.FOLLOW_UP,
            turn=2,
            **conversation,
            **_lookup_fields(first, first_doc, "M", "Dış paça"),
        ),
        _not_found("dikim-sohbet-1-t3", "Peki kordon boyu kaç?", turn=3, **conversation),
        make_question(
            question_id="dikim-sohbet-1-t4",
            text=f"Peki {second.model} modelinde iç paça kaç?",
            kind=QuestionKind.FOLLOW_UP,
            turn=4,
            **conversation,
            **_lookup_fields(second, second_doc, "M", "İç paça"),
        ),
    ]


def _conversation_with_label(spec: Spec, document: ScenarioDocument) -> list[GoldQuestion]:
    conversation = {"conversation_id": "dikim-sohbet-2"}
    return [
        make_question(
            question_id="dikim-sohbet-2-t1",
            text=f"{spec.model} S beden bel kaç?",
            kind=QuestionKind.TABLE_LOOKUP,
            turn=1,
            **conversation,
            **_lookup_fields(spec, document, "S", "Bel"),
        ),
        make_question(
            question_id="dikim-sohbet-2-t2",
            text="L beden?",
            kind=QuestionKind.FOLLOW_UP,
            turn=2,
            **conversation,
            **_lookup_fields(spec, document, "L", "Bel"),
        ),
        make_question(
            question_id="dikim-sohbet-2-t3",
            text="Etiketi ne?",
            kind=QuestionKind.FOLLOW_UP,
            turn=3,
            **conversation,
            **_label_fields(spec, document, "L"),
        ),
    ]


def _revision_questions(old: Spec, new: Spec, new_doc: ScenarioDocument) -> list[GoldQuestion]:
    return [
        make_question(
            question_id="dikim-revizyon-belirli",
            text=f"{new.model} Rev B, M beden iç paça kaç?",
            kind=QuestionKind.TABLE_LOOKUP,
            **_lookup_fields(new, new_doc, "M", "İç paça"),
        ),
        make_question(
            question_id="dikim-revizyon-netlestir",
            text=f"{new.model} M beden iç paça kaç?",
            kind=QuestionKind.CLARIFY,
            outcome=Outcome.CLARIFY,
            differing_values=(old.value("M", "İç paça"), new.value("M", "İç paça")),
        ),
    ]


def _build_specs(rng: Random) -> tuple[Spec, ...]:
    head = rng.randint(10, 99)
    first, second = rng.sample(range(10), 2)
    similar = (f"PNT-{head}{first}{second}", f"PNT-{head}{second}{first}")
    tolerances = ("0,5", "1,0")

    def spec(doc_id: str, model: str, carrier: Carrier, *mess: Mess, **kwargs: object) -> Spec:
        return Spec(
            doc_id=doc_id,
            model=model,
            carrier=carrier,
            bases=_random_bases(rng),
            tolerance=rng.choice(tolerances),
            labels=_random_labels(rng),
            mess=mess,
            **kwargs,  # type: ignore[arg-type]
        )

    return (
        spec("dikim-excel", similar[0], Carrier.XLSX, Mess.MERGED_CELLS, Mess.MULTI_SHEET),
        spec("dikim-pdf", similar[1], Carrier.PDF),
        spec(
            "dikim-word",
            f"CKT-{rng.randint(1000, 9999)}",
            Carrier.DOCX,
            Mess.INCONSISTENT_HEADERS,
            measure_header="Ebat",
        ),
        spec("dikim-tarama", f"GML-{rng.randint(1000, 9999)}", Carrier.SCAN, Mess.SKEWED),
        spec(
            "dikim-foto",
            f"MNT-{rng.randint(1000, 9999)}",
            Carrier.PHOTO,
            Mess.SKEWED,
            Mess.BLURRED,
            has_labels=False,
        ),
    )


def build_sewing(rng: Random) -> Scenario:
    specs = _build_specs(rng)
    revision_model = f"SRT-{rng.randint(1000, 9999)}"
    current = Spec(
        doc_id="dikim-rev-b",
        model=revision_model,
        carrier=Carrier.PDF,
        bases=_random_bases(rng),
        tolerance="0,5",
        labels=_random_labels(rng),
        mess=(Mess.NEAR_DUPLICATE_VERSION,),
        revision="Rev B",
    )
    previous = replace(
        current,
        doc_id="dikim-rev-a",
        revision="Rev A",
        bases={measure: value - 1.0 for measure, value in current.bases.items()},
    )
    documents = {item.doc_id: _document(item) for item in (*specs, previous, current)}

    questions = [
        question
        for spec in specs
        for question in _single_questions(spec, documents[spec.doc_id], rng)
    ]
    questions.append(_clarify(specs[0], "İç paça"))
    questions.append(_confirm_wrong(specs[1], documents[specs[1].doc_id]))
    questions += _conversation_with_model_switch(
        specs[0], documents[specs[0].doc_id], specs[1], documents[specs[1].doc_id]
    )
    questions += _conversation_with_label(specs[2], documents[specs[2].doc_id])
    questions += _revision_questions(previous, current, documents[current.doc_id])
    return Scenario(documents=tuple(documents.values()), questions=tuple(questions))
