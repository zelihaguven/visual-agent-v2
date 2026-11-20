"""Niteleyici denetimi: başka kaynağın adı ve düşen varyant (karar: doğrulayıcının son kuralı).

Kaynak metinleri yüklü belgelerin bugünkü parçalarından birebir (6013448, 6029322, CKT-7308).
"""

import pytest

from visual_agent.ask.deps import AskRequest
from visual_agent.ask.steps import AskState, user_text
from visual_agent.ask.streaming import StreamAssembler
from visual_agent.domain.answer import AnswerKind, ItemCheck, ModelAnswer, ModelItem, PromptSource
from visual_agent.domain.conversation import ConversationContext
from visual_agent.verification.answer import verify_answer, verify_item
from visual_agent.verification.qualifier import Qualifiers, build_qualifiers

SIZE_RANGE = "Sub Category | Sportstyle | Size Range | XS-4XL, SMT-4XLT"
CHART_SIZE_RANGE = (
    "Measurement Chart | 6013448-FW27-MMC-US | Chart Size Range | Apparel (XS-5XL) | "
    "Fit Type Regular"
)
LOGO_RED = (
    "Material Details: GR-SS27-9211/Left Chest Logo/High Solids Waterbase/ | Qty: 1.0000 | "
    "Usage: SEE UA GRAPHIC STANDARD PLACEMENT GUIDE - MEDIUM HEATHER | "
    "100: White // Venom Red: Venom Red 690"
)
LOGO_BLUE_HEADERLESS = (
    "GR-SS27-9211/Left Chest Logo/High Solids Waterbase/ | (boş) | 1.0000 | "
    "SEE UA GRAPHIC STANDARD PLACEMENT GUIDE - SOILD | (boş) | (boş) | Blue Haze 425"
)
BOM_HEADER = (
    "Material Details | Location | Qty | Usage | Only for Product Alternatives | "
    "100: White / / Venom Red | 001: Black / / Blue Haze"
)
THREAD = (
    "Material Details: TT-100156/ECO100 Recycled Thread or Gramax EcoVerde or Eco Flexo or Epic"
    " - Continuous Texturized Filament - Note Tex 21 and Tex 24 are interchangeable (Recycled "
    "version of TT-100107)/COATS or A&E or GUNZETAL-Tex 24//Approved/m | Qty: 130.0000 | Usage: "
    "BOTTOM FOR ALL SEWING UNLESS OTHERWISE NOTED. | 100: White // Venom Red: White 100 | "
    "001: Black // Blue Haze: Black 001"
)
WAIST = "Ebat: Bel | S: 38,0 | M: 40,0 | L: 42,0 | Tolerans (cm): 1,0"
INSEAM = "Ebat: İç paça | S: 73,5 | M: 75,5 | L: 77,5 | Tolerans (cm): 1,0"
OUTSEAM = "Ebat: Dış paça | S: 100,0 | M: 102,0 | L: 104,0 | Tolerans (cm): 1,0"


def _sources(*texts: str, language: str = "en", context: str = "") -> dict[int, PromptSource]:
    return {
        number: PromptSource(
            number=number, text=text, context=context, is_table_row=True, language=language
        )
        for number, text in enumerate(texts, start=1)
    }


def _item(text: str, quote: str, source_no: int = 1) -> ModelItem:
    return ModelItem.model_validate(
        {"metin": text, "alintilar": [{"kaynak_no": source_no, "metin": quote}]}
    )


def _check(
    text: str, quote: str, sources: dict[int, PromptSource], source_no: int = 1, asked: str = ""
) -> ItemCheck:
    return verify_item(
        _item(text, quote, source_no), sources, "tr", build_qualifiers(sources, asked)
    )


D6 = _sources(SIZE_RANGE, CHART_SIZE_RANGE)
LOGO = _sources(LOGO_RED, LOGO_BLUE_HEADERLESS, BOM_HEADER)
LOGO_QUESTION = "6029322'de göğüs logosunun rengi ne?"


# --- 19 Kasım teşhisindeki dört cümle ---


def test_wrong_field_name_on_another_fields_value_is_hidden() -> None:
    check = _check("Chart Size Range değeri XS-4XL, SMT-4XLT.", "XS-4XL, SMT-4XLT", D6)
    assert not check.ok
    assert any("chart size range" in problem for problem in check.problems)


def test_wrong_colorway_name_is_hidden() -> None:
    text = "Black / Blue Haze renk yolunda göğüs logosu Venom Red 690."
    assert not _check(text, "Venom Red 690", LOGO, asked=LOGO_QUESTION).ok


def test_dropped_colorway_is_hidden() -> None:
    check = _check(
        "Göğüs logosunun rengi Venom Red 690.", "Venom Red 690", LOGO, asked=LOGO_QUESTION
    )
    assert not check.ok
    assert any("varyantı yok" in problem for problem in check.problems)


def test_numbered_wrong_colorway_stays_hidden() -> None:
    text = "001 Black / Blue Haze renk yolunda göğüs logosu Venom Red 690."
    assert not _check(text, "Venom Red 690", LOGO, asked=LOGO_QUESTION).ok


# --- Doğru cümleler geçer ---


@pytest.mark.parametrize(
    ("text", "quote", "source_no"),
    [
        ("Chart Size Range değeri Apparel (XS-5XL).", "Chart Size Range | Apparel (XS-5XL)", 2),
        ("Size Range değeri XS-4XL, SMT-4XLT.", "Size Range | XS-4XL, SMT-4XLT", 1),
    ],
)
def test_field_named_from_its_own_source_passes(text: str, quote: str, source_no: int) -> None:
    assert _check(text, quote, D6, source_no).ok


def test_colorway_named_from_its_own_row_passes() -> None:
    text = "100: White // Venom Red renk yolunda göğüs logosu Venom Red 690."
    quote = "100: White // Venom Red: Venom Red 690"
    assert _check(text, quote, LOGO, asked=LOGO_QUESTION).ok


@pytest.mark.parametrize(
    "colorway", ["Black / Blue Haze", "Black // Blue Haze", "Black / / Blue Haze"]
)
def test_colorway_spellings_match(colorway: str) -> None:
    sources = _sources(THREAD, BOM_HEADER)
    text = f"{colorway} renk yolunda TT-100156 ipliğinin rengi Black 001."
    assert _check(text, "001: Black // Blue Haze: Black 001", sources).ok


# --- Beden ---

SIZES = _sources(WAIST, INSEAM, OUTSEAM, language="tr")


def test_size_in_sentence_passes() -> None:
    assert _check("S beden bel 38,0.", "S: 38,0", SIZES).ok


def test_size_only_in_users_question_passes() -> None:
    assert _check("38,0", "S: 38,0", SIZES, asked="CKT-7308 S beden bel kaç?").ok


def test_dropped_size_is_hidden() -> None:
    check = _check("Bel 38,0.", "S: 38,0", SIZES, asked="CKT-7308 bel kaç?")
    assert not check.ok
    assert any("varyantı yok" in problem for problem in check.problems)


def test_size_in_question_must_be_the_values_own_column() -> None:
    sources = _sources("Ebat: Kalça | S: 40,0 | M: 42,0 | L: 44,0", language="tr")
    assert not _check("42,0", "M: 42,0", sources, asked="L beden kalça kaç?").ok


@pytest.mark.parametrize("asked", ["M.CODE alanında kalça kaç?", "SMT-4XLT kalça kaç?"])
def test_short_codes_match_whole_words_only(asked: str) -> None:
    sources = _sources("Ebat: Kalça | S: 40,0 | M: 42,0 | L: 44,0", language="tr")
    assert not _check("42,0", "M: 42,0", sources, asked=asked).ok


def test_value_equal_in_every_size_needs_no_size() -> None:
    sources = _sources("Dim: AB005 | XS: 1 3/4 | SM: 1 3/4 | MD: 1 3/4")
    assert _check("AB005 ölçüsü 1 3/4.", "SM: 1 3/4", sources).ok


def test_short_attribute_headers_are_not_variants() -> None:
    sources = _sources("Tip: Vida | Adet: 4 | Kod: VD-12", language="tr")
    assert _check("Vida için kod VD-12.", "Kod: VD-12", sources).ok
    assert _check("Vidadan 4 tane kullanılır.", "Adet: 4", sources).ok


# --- Türkçe büyük/küçük harf ---


@pytest.mark.parametrize(
    "text", ["S beden İÇ PAÇA 73,5.", "S beden IÇ PAÇA 73,5.", "S beden iç paça 73,5."]
)
def test_turkish_case_is_ignored(text: str) -> None:
    assert _check(text, "S: 73,5", SIZES, source_no=2).ok


@pytest.mark.parametrize("text", ["S beden DIŞ PAÇA 73,5.", "S beden dış paça 73,5."])
def test_measure_name_from_another_row_is_hidden(text: str) -> None:
    assert not _check(text, "S: 73,5", SIZES, source_no=2).ok


# --- Kural A'da bölüm yolu sayılmaz ---


def test_section_path_does_not_vouch_for_a_name() -> None:
    sources = _sources(SIZE_RANGE, CHART_SIZE_RANGE, context="6013448 · Chart Size Range")
    assert not _check("Chart Size Range değeri XS-4XL, SMT-4XLT.", "XS-4XL, SMT-4XLT", sources).ok


# --- Etiket kümesi cevap başına bir kez; soru yalnız kullanıcının metni ---


def test_qualifiers_built_once_per_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def counted(sources: dict[int, PromptSource], asked: str) -> Qualifiers:
        calls.append(asked)
        return build_qualifiers(sources, asked)

    monkeypatch.setattr("visual_agent.verification.answer.build_qualifiers", counted)
    answer = ModelAnswer(
        kind=AnswerKind.ANSWER,
        items=(_item("S beden bel 38,0.", "S: 38,0"), _item("M beden bel 40,0.", "M: 40,0")),
    )
    verification = verify_answer(answer, SIZES, "tr", "bel kaç?")
    assert all(check.ok for check in verification.items)
    assert calls == ["bel kaç?"]


def test_stream_assembler_uses_the_users_question() -> None:
    assembler = StreamAssembler(SIZES, "tr", lambda event: None, "CKT-7308 S beden bel kaç?")
    item = '{"metin": "38,0", "alintilar": [{"kaynak_no": 1, "metin": "S: 38,0"}]}'
    content = f'{{"tur": "cevap", "cevap": [{item}]}}'
    assembler.feed(content, 0.1)
    assert [check.ok for _, check in assembler.verified] == [True]


def test_user_text_takes_only_grounded_words_from_the_previous_turn() -> None:
    request = AskRequest(
        "peki kalça?", context=ConversationContext(question="CKT-7308 L beden bel kaç?")
    )
    state = AskState(request=request, resolved_question="CKT-7308 M beden kalça kaç?")
    text = user_text(state)
    assert "peki kalça?" in text and "l" in text.split()
    assert "m" not in text.split()  # modelin tamamladığı soru girmez
    assert "bel" not in text.split()  # önceki turdan yalnız kod, sayı, beden


SIZES_WITH_PREFIX = _sources(
    "Ölçü noktası: İç paça | Beden S: 72,0 | Beden M: 74,0 | Beden L: 76,0 | Tolerans (cm): 0,5",
    language="tr",
)


def test_size_labels_with_shared_prefix_are_variants() -> None:
    asked = "PNT-1126 modelinde iç paça kaç?"
    assert not _check("İç paça 74,0.", "Beden M: 74,0", SIZES_WITH_PREFIX, asked=asked).ok
    assert _check("M beden iç paça 74,0.", "Beden M: 74,0", SIZES_WITH_PREFIX, asked=asked).ok
