"""Sınır durumları: doğrulamanın sayı biçimi kurallarını gerçek model cevabında sınar.

Binlik ayraç, ondalıklı tutar, eksi değer, birim, yazıyla sayı, numaralı adım ve küçük harfli
kod. Ana setlerden (seed 7 ve 11) ayrı üretilir; taban karşılaştırmalarını değiştirmez.
"""

from functools import partial

from evals.content import (
    DocumentContent,
    Scenario,
    ScenarioDocument,
    TableBlock,
    TextBlock,
    source_for,
)
from evals.gold import Carrier, GoldDocument, GoldQuestion, GoldSource, Outcome, QuestionKind

DOMAIN = "sinir"

make_question = partial(
    GoldQuestion, domain=DOMAIN, kind=QuestionKind.DIRECT, outcome=Outcome.ANSWERED
)


def _document(
    doc_id: str,
    suffix: str,
    carrier: Carrier,
    title: str,
    blocks: tuple[TextBlock | TableBlock, ...],
) -> ScenarioDocument:
    return ScenarioDocument(
        gold=GoldDocument(
            doc_id=doc_id, filename=f"{doc_id}.{suffix}", domain=DOMAIN, carrier=carrier
        ),
        content=DocumentContent(title=title, blocks=blocks),
    )


FEES = (
    ("Yıllık bakım", "1.250"),
    ("Parça değişimi", "3.400"),
    ("Acil servis", "12.500"),
    ("Yerinde eğitim", "2.450,75"),
)
STORAGE = (
    "Ürün en düşük -18 °C sıcaklıkta saklanır. Çözdürüldükten sonra en fazla 4 °C sıcaklıkta"
    " tutulur. Taşıma sırasında sıcaklık -5 ile 5 °C arasında kalmalıdır."
)
SEAMS = "Yan dikiş payı 12 mm, etek kıvırma payı 4 cm olmalıdır. Kol ağzı payı 1,5 cm'dir."
TRIAL = (
    "Yeni operatörler için deneme süresi iki aydır. Her operatör günde üç kez kalite kontrolü"
    " yapar."
)
STEPS = (
    "1. Makineyi kapatın.\n2. Koruma kapağını açın.\n3. 15 dakika soğumasını bekleyin.\n"
    "4. kb-204 kodlu kayışı takın."
)
METERS = (("M-01", "1.840"), ("M-02", "920"), ("M-03", "10.305"))


def _documents() -> tuple[ScenarioDocument, ...]:
    return (
        _document(
            "sinir-ucret",
            "pdf",
            Carrier.PDF,
            "Bakım Ücret Listesi",
            (TableBlock(title="Ücretler", headers=("Hizmet", "Ücret (TL)"), rows=FEES),),
        ),
        _document(
            "sinir-depolama",
            "docx",
            Carrier.DOCX,
            "Depolama Koşulları",
            (TextBlock("Sıcaklık", STORAGE),),
        ),
        _document(
            "sinir-dikis",
            "pdf",
            Carrier.PDF,
            "Dikiş Talimatı",
            (TextBlock("Paylar", SEAMS), TextBlock("Deneme ve kontrol", TRIAL)),
        ),
        _document(
            "sinir-bakim", "docx", Carrier.DOCX, "Kayış Değişimi", (TextBlock("Adımlar", STEPS),)
        ),
        _document(
            "sinir-sayac",
            "xlsx",
            Carrier.XLSX,
            "Sayaç Okumaları",
            (
                TableBlock(
                    title="Çalışma saatleri", headers=("Makine", "Çalışma saati"), rows=METERS
                ),
            ),
        ),
    )


def build_boundary() -> Scenario:
    fees, storage, seams, steps, meters = _documents()

    def ask(
        question_id: str, text: str, values: tuple[str, ...], evidence: str, source: GoldSource
    ) -> GoldQuestion:
        return make_question(
            question_id=question_id,
            text=text,
            expected_values=values,
            evidence=evidence,
            sources=(source,),
        )

    questions = (
        ask(
            "sinir-ucret-bakim",
            "Yıllık bakım ücreti ne kadar?",
            ("1.250",),
            "Yıllık bakım 1.250",
            source_for(fees, 0, 0),
        ),
        ask(
            "sinir-ucret-acil",
            "Acil servis ücreti kaç TL?",
            ("12.500",),
            "Acil servis 12.500",
            source_for(fees, 0, 2),
        ),
        ask(
            "sinir-ucret-egitim",
            "Yerinde eğitim ücreti ne kadar?",
            ("2.450,75",),
            "Yerinde eğitim 2.450,75",
            source_for(fees, 0, 3),
        ),
        ask(
            "sinir-sicaklik-en-dusuk",
            "Ürün en düşük kaç derecede saklanır?",
            ("-18",),
            "-18 °C",
            source_for(storage, 0),
        ),
        ask(
            "sinir-sicaklik-cozdurme",
            "Çözdürülen ürün en fazla kaç derecede tutulur?",
            ("4",),
            "4 °C",
            source_for(storage, 0),
        ),
        ask(
            "sinir-sicaklik-tasima",
            "Taşıma sırasında sıcaklık hangi aralıkta olmalı?",
            ("-5", "5"),
            "-5 ile 5 °C",
            source_for(storage, 0),
        ),
        ask(
            "sinir-pay-yan",
            "Yan dikiş payı ne kadar?",
            ("12",),
            "Yan dikiş payı 12 mm",
            source_for(seams, 0),
        ),
        ask(
            "sinir-pay-etek",
            "Etek kıvırma payı kaç santimetre?",
            ("4",),
            "etek kıvırma payı 4 cm",
            source_for(seams, 0),
        ),
        ask(
            "sinir-pay-kol",
            "Kol ağzı payı ne kadar?",
            ("1,5",),
            "Kol ağzı payı 1,5 cm",
            source_for(seams, 0),
        ),
        ask(
            "sinir-deneme-suresi",
            "Deneme süresi kaç ay?",
            ("iki",),
            "deneme süresi iki aydır",
            source_for(seams, 1),
        ),
        ask(
            "sinir-kontrol-sayisi",
            "Günde kaç kez kalite kontrolü yapılır?",
            ("üç",),
            "günde üç kez",
            source_for(seams, 1),
        ),
        ask(
            "sinir-adim-bekleme",
            "Koruma kapağı açıldıktan sonra kaç dakika beklenir?",
            ("15",),
            "3. 15 dakika",
            source_for(steps, 0),
        ),
        ask(
            "sinir-adim-kayis",
            "Kayış değişiminde hangi kodlu kayış takılır?",
            ("kb-204",),
            "4. kb-204",
            source_for(steps, 0),
        ),
        ask(
            "sinir-sayac-buyuk",
            "M-03 makinesinin çalışma saati kaç?",
            ("10.305",),
            "M-03 10.305",
            source_for(meters, 0, 2),
        ),
        ask(
            "sinir-sayac-kucuk",
            "M-02 makinesinin çalışma saati kaç?",
            ("920",),
            "M-02 920",
            source_for(meters, 0, 1),
        ),
    )
    return Scenario(documents=(fees, storage, seams, steps, meters), questions=questions)
