"""Sınır durumları: doğrulamanın kurallarını gerçek model cevabında sınar.

Binlik ayraç, ondalıklı tutar, eksi değer, birim, yazıyla sayı, numaralı adım ve küçük harfli
kod. Ayrıca aynı satırda komşu sütunun değerini yazma (yanlış sütun) ve olumsuzlamayı tersine
çevirme. Olumsuzlama soruları sayı taşımaz; puanlayıcı bunları ayırt edemez, cevap metni ayrıca
okunur. Ana setlerden (seed 7 ve 11) ayrı üretilir; taban karşılaştırmalarını değiştirmez.
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
SIZES = (
    ("Bel", "72", "74", "76"),
    ("Basen", "98", "100", "102"),
    ("İç paça", "76", "77", "78"),
)
WASHING = (("Pamuk", "30", "60"), ("Polyester", "20", "40"), ("Yün", "20", "30"))
MOTORS = (("Tork (Nm)", "12", "15"), ("Devir (dev/dk)", "1.400", "2.800"))
RULES = (
    "Kesim masasında eldiven kullanımı zorunlu değildir. Koruyucu gözlük zorunludur. Makine"
    " çalışırken koruma kapağı açılmaz. Bakım sırasında koruma kapağı açılabilir."
)
SAFETY = (
    "Hearing protection is not required in the packing area. Safety shoes are required in the"
    " warehouse. Do not lubricate the chain while the motor is running."
)


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


def _column_and_negation_documents() -> tuple[ScenarioDocument, ...]:
    return (
        _document(
            "sinir-beden",
            "xlsx",
            Carrier.XLSX,
            "Beden Ölçüleri",
            (
                TableBlock(
                    title="Ölçüler",
                    headers=("Ölçü noktası", "Beden S", "Beden M", "Beden L"),
                    rows=SIZES,
                ),
            ),
        ),
        _document(
            "sinir-yikama",
            "pdf",
            Carrier.PDF,
            "Yıkama Sıcaklıkları",
            (
                TableBlock(
                    title="Sıcaklıklar",
                    headers=("Malzeme", "En düşük (°C)", "En yüksek (°C)"),
                    rows=WASHING,
                ),
            ),
        ),
        _document(
            "sinir-motor",
            "docx",
            Carrier.DOCX,
            "Motor Değerleri",
            (TableBlock(title="Modeller", headers=("Değer", "A-100", "A-200"), rows=MOTORS),),
        ),
        _document(
            "sinir-kurallar",
            "pdf",
            Carrier.PDF,
            "Atölye Kuralları",
            (TextBlock("Kurallar", RULES),),
        ),
        _document(
            "sinir-safety", "docx", Carrier.DOCX, "Safety Notes", (TextBlock("Rules", SAFETY),)
        ),
    )


def _column_questions(
    sizes: ScenarioDocument, washing: ScenarioDocument, motors: ScenarioDocument
) -> tuple[GoldQuestion, ...]:
    """Doğru değerin komşu sütununda yakın bir değer durur; kanıt yalnız doğru hücredir."""

    def ask(
        question_id: str,
        text: str,
        value: str,
        evidence: str,
        source: GoldSource,
        kind: QuestionKind = QuestionKind.TABLE_LOOKUP,
    ) -> GoldQuestion:
        return make_question(
            question_id=question_id,
            text=text,
            kind=kind,
            expected_values=(value,),
            evidence=evidence,
            sources=(source,),
        )

    return (
        ask(
            "sinir-sutun-basen-m",
            "M beden basen kaç?",
            "100",
            "Beden M: 100",
            source_for(sizes, 0, 1),
        ),
        ask(
            "sinir-sutun-bel-l-teyit",
            "L beden bel 74 mü?",
            "76",
            "Beden L: 76",
            source_for(sizes, 0, 0),
            QuestionKind.CONFIRM_WRONG,
        ),
        ask(
            "sinir-sutun-icpaca-s",
            "S bedenin iç paçası ne kadar?",
            "76",
            "Beden S: 76",
            source_for(sizes, 0, 2),
        ),
        ask(
            "sinir-sutun-polyester-en-yuksek",
            "Polyester en fazla kaç derecede yıkanır?",
            "40",
            "En yüksek (°C): 40",
            source_for(washing, 0),
        ),
        ask(
            "sinir-sutun-yun-en-dusuk",
            "Yün en düşük kaç derecede yıkanır?",
            "20",
            "En düşük (°C): 20",
            source_for(washing, 0),
        ),
        ask(
            "sinir-sutun-a200-tork",
            "A-200 modelinin tork değeri nedir?",
            "15",
            "A-200: 15",
            source_for(motors, 0),
        ),
        ask(
            "sinir-sutun-a100-devir",
            "A-100 kaç devirde çalışır?",
            "1.400",
            "A-100: 1.400",
            source_for(motors, 0),
        ),
    )


def _negation_questions(
    rules: ScenarioDocument, safety: ScenarioDocument
) -> tuple[GoldQuestion, ...]:
    """Doğru cevap olumsuz (biri olumlu denetim); kanıt cümlenin kendisidir."""

    def ask(question_id: str, text: str, evidence: str, source: GoldSource) -> GoldQuestion:
        return make_question(
            question_id=question_id, text=text, evidence=evidence, sources=(source,)
        )

    return (
        ask(
            "sinir-olumsuz-eldiven",
            "Kesim masasında eldiven takmak zorunlu mu?",
            "eldiven kullanımı zorunlu değildir",
            source_for(rules, 0),
        ),
        ask(
            "sinir-olumsuz-kapak",
            "Makine çalışırken koruma kapağı açılabilir mi?",
            "Makine çalışırken koruma kapağı açılmaz",
            source_for(rules, 0),
        ),
        ask(
            "sinir-olumlu-gozluk",
            "Koruyucu gözlük takmak zorunlu mu?",
            "Koruyucu gözlük zorunludur",
            source_for(rules, 0),
        ),
        ask(
            "sinir-olumsuz-kulaklik",
            "Paketleme alanında kulak koruyucu takmak zorunlu mu?",
            "Hearing protection is not required in the packing area",
            source_for(safety, 0),
        ),
        ask(
            "sinir-olumsuz-zincir",
            "Motor çalışırken zincir yağlanabilir mi?",
            "Do not lubricate the chain while the motor is running",
            source_for(safety, 0),
        ),
    )


def build_boundary() -> Scenario:
    fees, storage, seams, steps, meters = _documents()
    sizes, washing, motors, rules, safety = _column_and_negation_documents()

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
    return Scenario(
        documents=(fees, storage, seams, steps, meters, sizes, washing, motors, rules, safety),
        questions=(
            *questions,
            *_column_questions(sizes, washing, motors),
            *_negation_questions(rules, safety),
        ),
    )
