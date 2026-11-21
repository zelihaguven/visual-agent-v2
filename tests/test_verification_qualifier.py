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
    text: str,
    quote: str,
    sources: dict[int, PromptSource],
    source_no: int = 1,
    asked: str = "",
    previous: str = "",
) -> ItemCheck:
    qualifiers = build_qualifiers(sources, asked, previous)
    return verify_item(_item(text, quote, source_no), sources, "tr", qualifiers)


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

    def counted(sources: dict[int, PromptSource], asked: str, previous: str = "") -> Qualifiers:
        calls.append(asked)
        return build_qualifiers(sources, asked, previous)

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
    question, previous = user_text(state)
    assert question == "peki kalça?" and "l" in previous.split()
    assert "m" not in previous.split()  # modelin tamamladığı soru girmez
    assert "bel" not in previous.split()  # önceki turdan yalnız kod, sayı, beden


SIZES_WITH_PREFIX = _sources(
    "Ölçü noktası: İç paça | Beden S: 72,0 | Beden M: 74,0 | Beden L: 76,0 | Tolerans (cm): 0,5",
    language="tr",
)


def test_size_labels_with_shared_prefix_are_variants() -> None:
    asked = "PNT-1126 modelinde iç paça kaç?"
    assert not _check("İç paça 74,0.", "Beden M: 74,0", SIZES_WITH_PREFIX, asked=asked).ok
    assert _check("M beden iç paça 74,0.", "Beden M: 74,0", SIZES_WITH_PREFIX, asked=asked).ok


# --- İnceleme bulguları: doğru cümle gizlenmez, renk yolu numarası ad sayılmaz ---


@pytest.mark.parametrize(
    ("row", "text", "quote"),
    [
        ("Min: 10 | Max: 20", "Minimum basınç 10 bar.", "Min: 10"),
        ("Adet: 4 | Kod: 12", "Vidadan 4 tane kullanılır.", "Adet: 4"),
        ("Volt: 220 | Amp: 16", "Gerilim 220 V.", "Volt: 220"),
        ("Ön: 3 | Arka: 4", "Arkada 4 vida var.", "Arka: 4"),
        ("Karışım: 1:4 | Süre: 10:30", "Karışım oranı 1:4, süre 10:30.", "Karışım: 1:4"),
    ],
)
def test_attribute_columns_are_not_variants(row: str, text: str, quote: str) -> None:
    check = _check(text, quote, _sources(row, language="tr"))
    assert not any("varyant" in problem for problem in check.problems)


def test_prose_lines_are_not_names() -> None:
    sources = {
        1: PromptSource(number=1, text="Cihazı kapatın ve fişi çekin; bekleme süresi 5 dakika."),
        2: PromptSource(number=2, text="Cihazı kapatın"),
        3: PromptSource(number=3, text="Çalışma sıcaklığı"),
    }
    text = "Cihazı kapatın ve fişi çekin; bekleme süresi 5 dakika."
    assert _check(text, text, sources).ok


def test_colorway_number_inside_the_value_does_not_name_the_colorway() -> None:
    sources = _sources(THREAD, BOM_HEADER)
    check = _check(
        "TT-100156 ipliğinin rengi Black 001.", "001: Black // Blue Haze: Black 001", sources
    )
    assert not check.ok
    assert any("varyantı yok" in problem for problem in check.problems)


# --- Önceki turun bedeni: bu tur gruptan ad söylüyorsa önceki turun adı sayılmaz ---

PREVIOUS = "ckt-7308 l"  # önceki tur "CKT-7308 L beden bel kaç?" (is_grounded sözcükleri)


def test_previous_size_does_not_vouch_when_this_turn_names_another_size() -> None:
    check = _check("Bel 42,0.", "L: 42,0", SIZES, asked="peki M?", previous=PREVIOUS)
    assert not check.ok
    assert any("varyantı yok" in problem for problem in check.problems)


def test_this_turns_size_vouches_for_its_own_value() -> None:
    assert _check("Bel 40,0.", "M: 40,0", SIZES, asked="peki M?", previous=PREVIOUS).ok


def test_previous_size_still_counts_when_this_turn_names_no_size() -> None:
    assert _check(
        "Kalça 52,5.",
        "L: 52,5",
        _sources("Ebat: Kalça | S: 48,5 | M: 50,5 | L: 52,5 | Tolerans (cm): 1,0", language="tr"),
        asked="peki kalça?",
        previous=PREVIOUS,
    ).ok


def test_previous_colorway_does_not_vouch_when_this_turn_names_a_header_sibling() -> None:
    quote = "100: White // Venom Red: Venom Red 690"
    for asked in ("peki 001?", "peki Black / Blue Haze?"):
        check = _check("Göğüs logosu Venom Red 690.", quote, LOGO, asked=asked, previous="100")
        assert not check.ok, asked
    assert _check("Göğüs logosu Venom Red 690.", quote, LOGO, asked="peki?", previous="100").ok


# --- Kural C: çok hücreli alıntıda adı anılan hücrenin değeri ---

CELL_PROBLEM = "cümlede adı geçen hücrenin değeri değil"


@pytest.mark.parametrize(
    ("row", "text", "quote", "ok"),
    [
        # Sayısal ve tek sözcüklü etiketler (Kural B görmez): yanlış hücrenin değeri gizlenir.
        (
            "Ebat: İç paça | 38: 72,0 | 40: 74,0 | 42: 76,0",
            "40 beden iç paça 72,0.",
            "38: 72,0 | 40: 74,0",
            False,
        ),
        (
            "Ebat: İç paça | Small: 72,0 | Medium: 74,0",
            "Medium iç paça 72,0.",
            "Small: 72,0 | Medium: 74,0",
            False,
        ),
        ("Ebat: İç paça | S: 72,0 | M: 74,0", "M beden iç paça 72,0.", "S: 72,0 | M: 74,0", False),
        # Tek hücre alıntısı ve kendi hücresinin değeri geçer.
        ("Ebat: İç paça | 38: 72,0 | 40: 74,0", "40 beden iç paça 74,0.", "40: 74,0", True),
        (
            "Ebat: İç paça | 38: 72,0 | 40: 74,0",
            "40 beden iç paça 74,0.",
            "Ebat: İç paça | 38: 72,0 | 40: 74,0",
            True,
        ),
        # Öznitelik karışması da yakalanır; doğru eşleşme geçer.
        ("Min: 5 | Max: 10", "Max 5.", "Min: 5 | Max: 10", False),
        ("Min: 5 | Max: 10", "Max 10.", "Min: 5 | Max: 10", True),
    ],
)
def test_value_must_sit_in_the_cell_the_sentence_names(
    row: str, text: str, quote: str, ok: bool
) -> None:
    check = _check(text, quote, _sources(row, language="tr"), asked="iç paça kaç?")
    assert check.ok is ok, check.problems


def test_sentence_naming_no_cell_is_left_to_the_other_rules() -> None:
    """Ad anılmayan çok hücreli alıntı bu kurala girmez; sayısal etiketlerde Kural B bakar."""
    sources = _sources("Ebat: İç paça | 38: 72,0 | 40: 74,0", language="tr")
    check = _check("İç paça 72,0.", "38: 72,0 | 40: 74,0", sources, asked="38 beden iç paça?")
    assert not any(CELL_PROBLEM in problem for problem in check.problems)


def test_short_code_inside_another_word_does_not_name_a_cell() -> None:
    sources = _sources("Kod: X | S: 72,0 | M: 74,0", language="tr")
    check = _check("M.CODE alanı 72,0.", "S: 72,0 | M: 74,0", sources)
    assert not any(CELL_PROBLEM in problem for problem in check.problems)


def test_non_numeric_attribute_cells_do_not_trigger_the_cell_rule() -> None:
    sources = _sources("Renk: Siyah | Malzeme: Pamuk | Gramaj: 180", language="tr")
    assert _check("Malzemesi pamuk.", "Renk: Siyah | Malzeme: Pamuk", sources).ok
    assert _check("Gramaj 180.", "Malzeme: Pamuk | Gramaj: 180", sources).ok


def test_year_columns_with_a_single_cell_sentence_pass() -> None:
    sources = _sources("Satış: Toplam | 2024: 120 | 2025: 140", language="tr")
    assert _check("2025 satışı 140.", "2025: 140", sources).ok
    assert _check("2025 satışı 140.", "2024: 120 | 2025: 140", sources).ok
    assert not _check("2025 satışı 120.", "2024: 120 | 2025: 140", sources).ok


@pytest.mark.parametrize(
    ("row", "text", "quote", "ok"),
    [
        # Satırın anahtarı (rakamsız) adı anılan hücre sayılmaz (n25'te gizlenen doğru cümleler).
        (
            "Beden: S | Etiket kodu: ETK-6154",
            "PNT-1126 S beden için ETK-6154 etiket kodu.",
            "Beden: S | Etiket kodu: ETK-6154",
            True,
        ),
        (
            "Beden: L | Etiket kodu: ETK-7827",
            "L beden etiketi ETK-7827'dir.",
            "Beden: L | Etiket kodu: ETK-7827",
            True,
        ),
        # Adı anılan hücrenin değeri de söylenince yan bilgi geçer.
        (WAIST, "M beden bel 40,0, tolerans 1,0.", WAIST, True),
        ("Volt: 220 | Amp: 5", "Volt 220, akım 5.", "Volt: 220 | Amp: 5", True),
        # İki hücreyi kendi değerleriyle anan cümle geçer.
        (
            "Ebat: İç paça | S: 72,0 | M: 74,0",
            "S beden 72,0, M beden 74,0.",
            "S: 72,0 | M: 74,0",
            True,
        ),
        (
            "Ebat: İç paça | 38: 72,0 | 40: 74,0",
            "38 beden 72,0, 40 beden 74,0.",
            "38: 72,0 | 40: 74,0",
            True,
        ),
        # Renk yolu: etiket numarası değerin içinde de geçer.
        (THREAD, "100 renk yolunda iplik White 100.", THREAD, True),
        (THREAD, "100 renk yolunda iplik Black 001.", THREAD, False),
        # Rakamsız ad hücresi ("Ebat: Bel") tek başına kuralı tetiklemez.
        (WAIST, "Ebat bel, M beden 40,0.", WAIST, True),
    ],
)
def test_correct_sentences_pass_the_cell_rule(row: str, text: str, quote: str, ok: bool) -> None:
    check = _check(text, quote, _sources(row, language="tr"))
    assert (not any(CELL_PROBLEM in problem for problem in check.problems)) is ok, check.problems


# --- Kural B: salt sayısal kardeş etiketler varyanttır (Kural C'nin 1. sınırı, sayısal) ---

VARIANT_PROBLEM = "cümlede değerin varyantı yok"
NUMERIC_SIZES = "Ebat: İç paça | 38: 72,0 | 40: 74,0"
YEARS = "Satış: Toplam | 2024: 120 | 2025: 140"


@pytest.mark.parametrize(
    ("row", "text", "quote", "asked", "ok"),
    [
        # Etiketsiz değer: hangi bedenin değeri olduğu ne cümlede ne soruda.
        (NUMERIC_SIZES, "İç paça 72,0.", "38: 72,0 | 40: 74,0", "iç paça kaç?", False),
        (NUMERIC_SIZES, "İç paça 72,0.", "38: 72,0", "iç paça kaç?", False),
        # Kullanıcı başka bedeni sorduysa öbür bedenin etiketsiz değeri yine gizlenir.
        (NUMERIC_SIZES, "İç paça 72,0.", "38: 72,0 | 40: 74,0", "40 beden iç paça kaç?", False),
        # Etiket soruda ya da cümlede geçiyorsa geçer.
        (NUMERIC_SIZES, "İç paça 72,0.", "38: 72,0 | 40: 74,0", "38 beden iç paça kaç?", True),
        (NUMERIC_SIZES, "38 beden iç paça 72,0.", "38: 72,0 | 40: 74,0", "iç paça kaç?", True),
        # Başka bir sayının parçası etiketi söylemez.
        (NUMERIC_SIZES, "İç paça 72,0.", "38: 72,0 | 40: 74,0", "138 numaralı iç paça?", False),
        (NUMERIC_SIZES, "İç paça 72,0.", "38: 72,0 | 40: 74,0", "38,5 mi iç paça?", False),
        # Değer bütün bedenlerde aynıysa etiket gerekmez.
        ("Ebat: Tolerans | 38: 1,0 | 40: 1,0", "Tolerans 1,0.", "38: 1,0 | 40: 1,0", "", True),
        # Tek sayısal etiket varyant grubu değildir.
        ("Ebat: İç paça | Adet: 3 | 38: 72,0", "İç paça 72,0.", "38: 72,0", "", True),
        # Yıl sütunları da salt sayısal kardeştir: yıl söylenmeden değer verilemez.
        (YEARS, "Toplam satış 120.", "2024: 120 | 2025: 140", "toplam satış kaç?", False),
        (YEARS, "2024 toplam satışı 120.", "2024: 120 | 2025: 140", "toplam satış kaç?", True),
        (YEARS, "Toplam satış 120.", "2024: 120 | 2025: 140", "2024 satışı kaç?", True),
        (YEARS, "Toplam satış 120.", "2024: 120 | 2025: 140", "2025 satışı kaç?", False),
    ],
)
def test_numeric_sibling_labels_are_variants(
    row: str, text: str, quote: str, asked: str, ok: bool
) -> None:
    check = _check(text, quote, _sources(row, language="tr"), asked=asked)
    assert check.ok is ok, check.problems
    assert ok or any(VARIANT_PROBLEM in problem for problem in check.problems)


def test_unlabelled_value_under_single_word_labels_is_a_known_gap() -> None:
    """Tek sözcüklü etiketler ("Small", "Medium") varyant sayılmaz: öznitelik sütunlarından
    ("Min", "Max") ayırt edilemez. Etiketsiz değer burada hâlâ doğrulanır (karar 0019)."""
    sources = _sources("Ebat: İç paça | Small: 72,0 | Medium: 74,0", language="tr")
    assert _check("İç paça 72,0.", "Small: 72,0 | Medium: 74,0", sources, asked="iç paça?").ok


def test_previous_turns_numeric_size_is_replaced_by_this_turns() -> None:
    sources = _sources(NUMERIC_SIZES, language="tr")
    quote = "38: 72,0 | 40: 74,0"
    assert _check("İç paça 72,0.", quote, sources, asked="peki iç paça?", previous="38").ok
    assert not _check("İç paça 72,0.", quote, sources, asked="peki 40?", previous="38").ok
