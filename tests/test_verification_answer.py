from concurrent.futures import ThreadPoolExecutor

import pytest

from visual_agent.domain.answer import (
    AnswerKind,
    ClarifyOption,
    ClarifyRequest,
    ModelAnswer,
    ModelItem,
    PromptSource,
    Quote,
    VerificationStatus,
)
from visual_agent.verification.answer import ABSENCE_CLAIM, verify_answer, verify_item

ROW = "İç paça | M: 76,5 | Tolerans: 0,5"
SOURCES = {
    1: PromptSource(number=1, text=ROW, context="PNT-4417 ölçü föyü"),
    2: PromptSource(number=2, text="Kullanım basıncı 11 (± 1) bar olmalıdır."),
    3: PromptSource(
        number=3,
        text="ALTER TABLE SIPARIS RENAME COLUMN SIP_TARIH TO SIPARIS_TARIHI;",
        is_code=True,
    ),
    4: PromptSource(number=4, text="Şekil: düğme solda. Otomatik açıklama: kırmızı düğme."),
    5: PromptSource(number=5, text="Debi 299.999% olarak okundu.", ocr_uncertain=("299.999%",)),
}


def item(text: str, quote: str = "M: 76,5", source_no: int = 1) -> ModelItem:
    return ModelItem(text=text, quotes=(Quote(source_no=source_no, text=quote),))


def answer(*items: ModelItem) -> ModelAnswer:
    return ModelAnswer(kind=AnswerKind.ANSWER, items=items)


def test_correct_item_passes() -> None:
    assert verify_item(item("İç paça 76,5."), SOURCES, "tr").ok


def test_quote_must_exist_in_the_source() -> None:
    check = verify_item(item("İç paça 76,5.", quote="M: 76,5 cm tam"), SOURCES, "tr")

    assert not check.ok
    assert "birebir" in check.problems[0]


def test_unknown_source_number_fails() -> None:
    assert not verify_item(item("İç paça 76,5.", source_no=9), SOURCES, "tr").ok


def test_number_must_come_from_its_own_quote() -> None:
    check = verify_item(item("İç paça 78.", quote="M: 76,5"), SOURCES, "tr")

    assert not check.ok
    assert "78" in check.problems[0]


def test_number_at_the_start_of_a_sentence_is_checked_like_any_value() -> None:
    sources = {1: PromptSource(number=1, text="Başvuru 30. Gün içinde yapılır.")}
    quote = "Başvuru 30. Gün içinde yapılır"

    wrong = verify_item(item("45. Gün içinde başvurulur.", quote=quote), sources, "tr")
    assert not wrong.ok
    assert "45" in wrong.problems[0]
    assert verify_item(item("30. Gün içinde başvurulur.", quote=quote), sources, "tr").ok


def test_list_mark_in_the_source_only_backs_the_same_mark() -> None:
    steps = "Adımlar: 1. Vanayı açın. 2. Bekleyin. Bakım 30. Gün yapılır"
    sources = {1: PromptSource(number=1, text=steps)}

    def check(text: str) -> bool:
        return verify_item(item(text, quote=steps), sources, "tr").ok

    assert check("1. Vanayı açın.")
    assert check("2) Bekleyin [1].")
    assert not check("Bakım: 2. Gün yapılır.")  # "2. Bekleyin" adımı gün değeri değil
    assert not check("Vanayı 1 kez açın.")


def test_identifier_not_in_quote_or_source_context_fails() -> None:
    check = verify_item(item("PNT-4471 için iç paça 76,5."), SOURCES, "tr")

    assert not check.ok
    assert "pnt-4471" in check.problems[0]


def test_identifier_from_cited_source_title_is_allowed() -> None:
    assert verify_item(item("PNT-4417 için iç paça 76,5."), SOURCES, "tr").ok


def test_tolerance_cannot_be_dropped() -> None:
    quote = "11 (± 1) bar"

    assert not verify_item(item("Basınç 11 bar.", quote=quote, source_no=2), SOURCES, "tr").ok
    assert verify_item(item("Basınç 11 (± 1) bar.", quote=quote, source_no=2), SOURCES, "tr").ok


def test_foreign_alphabet_fails() -> None:
    assert not verify_item(item("İç paça 76,5 金额."), SOURCES, "tr").ok


def test_uncertain_ocr_value_blocks_the_item() -> None:
    check = verify_item(item("Debi 299.999%.", quote="299.999%", source_no=5), SOURCES, "tr")

    assert not check.ok
    assert "OCR" in check.problems[0]


OCR_ROW = "Dış paça | S: 100,5 | M: 102,5 | Tolerans (cm): 10"
OCR_SOURCES = {1: PromptSource(number=1, text=OCR_ROW, ocr_uncertain=("10",), from_ocr=True)}


def test_uncertain_value_does_not_hide_a_longer_value_that_contains_it() -> None:
    check = verify_item(item("M beden dış paça 102,5.", quote="M: 102,5"), OCR_SOURCES, "tr")

    assert check.ok, check.problems


def test_uncertain_value_itself_is_still_hidden() -> None:
    check = verify_item(item("Tolerans 10 cm.", quote="Tolerans (cm): 10"), OCR_SOURCES, "tr")

    assert not check.ok
    assert "OCR" in check.problems[0]


LABEL_ROW = "Beden: M | Etiket kodu: ETK-3392"
UNCERTAIN_HEADING_SOURCES = {
    1: PromptSource(
        number=1,
        text=LABEL_ROW,
        context="GML-6473 ölçü föyü · Etiket kodları",
        ocr_uncertain=("GML-6473",),
        from_ocr=True,
        is_table_row=True,
    )
}
"""Okuyucu başlıktaki kodu belirsiz okudu ("iGML-6473"); kod satırın bağlamında duruyor."""


def test_uncertain_code_from_the_row_context_is_hidden_in_the_sentence() -> None:
    check = verify_item(
        item("GML-6473 M beden etiket kodu ETK-3392.", quote=LABEL_ROW),
        UNCERTAIN_HEADING_SOURCES,
        "tr",
    )

    assert not check.ok
    assert any("OCR" in problem for problem in check.problems)


def test_sentence_without_the_uncertain_code_still_passes() -> None:
    check = verify_item(
        item("M beden etiket kodu ETK-3392.", quote=LABEL_ROW), UNCERTAIN_HEADING_SOURCES, "tr"
    )

    assert check.ok, check.problems


@pytest.mark.parametrize(
    ("source", "text"),
    [
        ("Ceza tutarı 1.000 TL", "Ceza tutarı 1 TL."),
        ("Parti 1.500 adet", "Parti 1,5 adet."),
        ("Çalışma sıcaklığı -5 °C", "Çalışma sıcaklığı 5 °C."),
    ],
)
def test_thousands_and_sign_cannot_change_a_value(source: str, text: str) -> None:
    sources = {1: PromptSource(number=1, text=source)}

    assert not verify_item(item(text, quote=source), sources, "tr").ok


def test_same_value_written_the_same_way_still_passes() -> None:
    sources = {1: PromptSource(number=1, text="Çalışma sıcaklığı -5 °C, ceza 1.000 TL")}
    quote = "Çalışma sıcaklığı -5 °C, ceza 1.000 TL"

    assert verify_item(item("Sıcaklık -5 °C, ceza 1.000 TL.", quote=quote), sources, "tr").ok


@pytest.mark.parametrize(
    ("source", "text"),
    [
        ("Ödeme 60. günde yapılır", "30. günde ödeme yapılır."),
        ("İzin 3 gündür", "İzin beş gündür."),
        ("Model PNT-1162 kumaş", "Model pnt-9999 kumaş."),
        ("Boy 50 cm", "Değer boy-99 cm."),
    ],
)
def test_numbers_hidden_in_words_or_codes_are_still_checked(source: str, text: str) -> None:
    sources = {1: PromptSource(number=1, text=source)}

    assert not verify_item(item(text, quote=source), sources, "tr").ok


@pytest.mark.parametrize(
    ("source", "text"),
    [
        ("İzin 1 gün sürer", "İzin bir gün sürer."),
        ("Toplam 2 adım vardır", "Toplam iki adım vardır."),
        ("Model PNT-1162 kumaş", "Bu bir pnt-1162 kumaşıdır."),
    ],
)
def test_same_value_in_words_or_lower_case_still_passes(source: str, text: str) -> None:
    sources = {1: PromptSource(number=1, text=source)}

    assert verify_item(item(text, quote=source), sources, "tr").ok


@pytest.mark.parametrize(
    ("source", "quote", "text", "ok"),
    [
        # Birim yalnız başka sütunun başlığında; kaynakta hiç yok; tek harfli sütun adı birim değil.
        ("Bel | Beden L: 42,5 | Tolerans (cm): 1,0", "Beden L: 42,5", "L beden 42,5 cm.", False),
        ("Bel | M: 40,5 | L: 42,5", "Bel | M: 40,5 | L: 42,5", "M beden bel 40,5 cm.", False),
        ("Bel | Beden M: 74", "Beden M: 74", "M beden bel 74 m.", False),
        (
            "PNT-1126 | Beden S: ETK-6154",
            "PNT-1126 | Beden S: ETK-6154",
            "PNT-1126 S beden ETK-6154.",
            True,
        ),
        ("Hizmet: Bakım | Ücret (TL): 1.250", "Ücret (TL): 1.250", "Bakım 1.250 TL.", True),
        ("Malzeme: Yün | En yüksek (°C): 30", "En yüksek (°C): 30", "Yün en fazla 30 °C.", True),
        ("Adım | Süre (dk): 15", "Süre (dk): 15", "15 dakika beklenir.", True),
        ("Hizmet: Acil | Ücret (TL): 12.500", "12.500", "Acil servis 12.500 TL.", True),
        # Devrik tablo: birim satırın ilk hücresinde, o satırın değerlerine sayılır.
        ("Değer: Tork (Nm) | A-100: 12 | A-200: 15", "A-200: 15", "A-200 tork 15 Nm.", True),
        ("Değer: Tork (Nm) | A-100: 12 | A-200: 15", "A-200: 15", "A-200 tork 15 kg.", False),
        # Alıntıdaki birimle aynı ya da eş anlamlı birim geçer, başka birim geçmez.
        ("Dikiş payı 5 mm", "Dikiş payı 5 mm", "Dikiş payı 5 mm'dir.", True),
        ("Bekleme 30 dk", "Bekleme 30 dk", "Bekleme 30 dakika.", True),
        ("Pay 5 mm, kenar 5 cm", "Pay 5 mm, kenar 5 cm", "Kenar 5 cm.", True),
        ("Bel | M: 40,5 | L: 42,5", "Bel | M: 40,5 | L: 42,5", "M beden bel 40,5.", True),
        ("Dikiş payı 5 mm", "Dikiş payı 5 mm", "Dikiş payı 5 cm.", False),
        ("Sıcaklık 40 °C", "Sıcaklık 40 °C", "Sıcaklık 40 °F.", False),
        ("Bekleme 30 sn", "Bekleme 30 sn", "Bekleme 30 dakika.", False),
    ],
)
def test_unit_must_be_in_the_quote_or_its_own_column_header(
    source: str, quote: str, text: str, ok: bool
) -> None:
    check = verify_item(item(text, quote=quote), {1: PromptSource(number=1, text=source)}, "tr")

    assert check.ok is ok, check.problems


def test_capitalised_number_word_is_checked_without_crashing() -> None:
    sources = {1: PromptSource(number=1, text="İzin 3 gündür")}

    check = verify_item(item("İki gün izin var.", quote="İzin 3 gündür"), sources, "tr")

    assert not check.ok


def test_cut_quote_at_the_limit_is_tolerated() -> None:
    long_text = "a" * 20 + " " + " ".join(f"kelime{i}" for i in range(40))
    sources = {1: PromptSource(number=1, text=long_text)}
    cut_quote = long_text[:140] + " bozuk**"

    assert verify_item(item("Metin burada.", quote=cut_quote), sources, "tr").ok


def test_short_quote_with_different_ending_is_not_tolerated() -> None:
    assert not verify_item(item("Metin.", quote="M: 76,5 başka"), SOURCES, "tr").ok


def test_field_label_quote_matches_a_cell() -> None:
    assert verify_item(item("Tolerans 0,5.", quote="Tolerans: 0,5"), SOURCES, "tr").ok


def test_quote_joining_two_cells_is_rejected() -> None:
    assert not verify_item(item("76,5.", quote="M: 76,5 | Tolerans: 0,5 fazla"), SOURCES, "tr").ok


def test_code_reference_supplies_identifiers_without_a_quote() -> None:
    reference = ModelItem(text="SIP_TARIH kolonu SIPARIS_TARIHI olur.", code_source_no=3)

    assert verify_item(reference, SOURCES, "tr").ok


def test_code_reference_must_point_to_a_code_source() -> None:
    reference = ModelItem(text="Komut bu.", code_source_no=1)

    assert not verify_item(reference, SOURCES, "tr").ok


def test_wrong_identifier_next_to_code_reference_fails() -> None:
    reference = ModelItem(text="SIP_TARIHI kolonu değişir.", code_source_no=3)

    assert not verify_item(reference, SOURCES, "tr").ok


def test_item_from_ocr_text_is_marked_and_makes_answer_partial() -> None:
    sources = {1: PromptSource(number=1, text="Bağlantı limiti: 386", from_ocr=True)}
    candidate = item("Bağlantı limiti 386.", quote="Bağlantı limiti: 386")

    assert verify_item(candidate, sources, "tr").ok
    assert verify_item(candidate, sources, "tr").from_ocr
    assert verify_answer(answer(candidate), sources, "tr").status is VerificationStatus.PARTIAL


def test_one_ocr_item_makes_the_whole_answer_partial() -> None:
    sources = {
        1: PromptSource(number=1, text="M: 76,5"),
        2: PromptSource(number=2, text="L: 80,5", from_ocr=True),
    }
    result = verify_answer(
        answer(item("M 76,5.", quote="M: 76,5"), item("L 80,5.", quote="L: 80,5", source_no=2)),
        sources,
        "tr",
    )

    assert result.status is VerificationStatus.PARTIAL


def test_command_read_by_ocr_is_marked() -> None:
    sources = {1: PromptSource(number=1, text="DROP TABLE T;", is_code=True, from_ocr=True)}
    command = ModelItem(text="Tabloyu siler.", code_source_no=1)

    assert verify_item(command, sources, "tr").from_ocr


def test_code_written_without_its_hyphen_matches_the_source() -> None:
    sources = {1: PromptSource(number=1, text="GML-6473 Kalça: 48,0")}
    candidate = item("GML6473 kalça 48,0.", quote="GML-6473 Kalça: 48,0")

    assert verify_item(candidate, sources, "tr").ok


def test_all_items_valid_is_verified() -> None:
    assert verify_answer(answer(item("76,5.")), SOURCES, "tr").status is VerificationStatus.VERIFIED


def test_one_bad_item_fails_the_answer_but_keeps_item_results() -> None:
    result = verify_answer(answer(item("76,5."), item("78.")), SOURCES, "tr")

    assert result.status is VerificationStatus.FAILED
    assert [check.ok for check in result.items] == [True, False]


def test_repeated_verified_sentence_does_not_fail_the_answer() -> None:
    """Tekrar cevabı başarısız saymaz; tekrarlar cevap kurulurken teke iner (ask/steps)."""
    sentence = "Bu ayar her zaman sol tarafta yapılır."

    result = verify_answer(answer(item(sentence), item(sentence)), SOURCES, "tr")

    assert result.status is VerificationStatus.VERIFIED
    assert result.problems == ()


def test_empty_answer_fails() -> None:
    assert verify_answer(answer(), SOURCES, "tr").status is VerificationStatus.FAILED


def test_not_found_is_reported() -> None:
    result = verify_answer(ModelAnswer(kind=AnswerKind.NOT_FOUND), SOURCES, "tr")

    assert result.status is VerificationStatus.NOT_FOUND


def test_clarification_needs_real_sources() -> None:
    def clarify(*numbers: int) -> ModelAnswer:
        options = tuple(ClarifyOption(source_no=number) for number in numbers)
        return ModelAnswer(
            kind=AnswerKind.CLARIFY,
            clarify=ClarifyRequest(question="Hangisi?", options=options),
        )

    valid = verify_answer(clarify(1, 2), SOURCES, "tr")

    assert valid.status is VerificationStatus.CLARIFY
    assert valid.clarify_options == (1, 2)
    assert verify_answer(clarify(1, 9), SOURCES, "tr").status is VerificationStatus.FAILED


def test_concurrent_verification_gives_identical_results() -> None:
    target = answer(item("76,5."), item("78."))
    expected = verify_answer(target, SOURCES, "tr")

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: verify_answer(target, SOURCES, "tr"), range(200)))

    assert all(result == expected for result in results)


@pytest.mark.parametrize(
    ("quote", "expected"),
    [
        ("Remedy: and check", True),
        ("Remedy: turn check", False),
        ("Code: turn off", False),
        ("Code: E050 | Remedy: off and", False),
    ],
)
def test_field_quote_requires_contiguous_text_in_the_named_cell(quote: str, expected: bool) -> None:
    sources = {1: PromptSource(number=1, text="Code: E050 | Remedy: turn off and check")}

    assert verify_item(item("Kontrol edin.", quote=quote), sources, "tr").ok is expected


def test_one_source_can_hold_all_options_of_a_clarification() -> None:
    answer = ModelAnswer(
        kind=AnswerKind.CLARIFY,
        items=(),
        clarify=ClarifyRequest(question="Hangi beden?", options=(ClarifyOption(source_no=1),)),
    )

    result = verify_answer(answer, SOURCES, "tr")

    assert result.status is VerificationStatus.CLARIFY
    assert result.clarify_options == (1,)


def test_sentence_failing_only_on_its_unit_carries_its_quote() -> None:
    sources = {1: PromptSource(number=1, text="Bel | M: 40,5 | L: 42,5")}

    check = verify_item(item("L beden bel 42,5 cm.", quote="L: 42,5"), sources, "tr")

    assert not check.ok
    assert check.quote == "L: 42,5"


@pytest.mark.parametrize(
    "text",
    [
        "L beden bel 42,5 cm, M beden 99.",  # birim dışında bir sorun daha var
        "L beden bel 42,5.",  # geçen cümle alıntı gerektirmez
    ],
)
def test_quote_is_only_for_a_unit_only_failure(text: str) -> None:
    sources = {1: PromptSource(number=1, text="Bel | M: 40,5 | L: 42,5")}

    assert verify_item(item(text, quote="L: 42,5"), sources, "tr").quote is None


def _single(source: str, text: str, language: str = "tr", source_language: str = "tr") -> bool:
    sources = {1: PromptSource(number=1, text=source, language=source_language)}
    return verify_item(item(text, quote=source), sources, language).ok


def test_turkish_ten_written_as_a_word_is_checked() -> None:
    assert not _single("Bekleme 5 dakikadır", "Bekleme on dakikadır.")
    assert _single("Bekleme 10 dakikadır", "Bekleme on dakikadır.")


def test_turkish_ten_in_the_source_backs_only_the_same_written_phrase() -> None:
    assert _single("Bekleme süresi on dakikadır", "Bekleme on dakikadır.")
    assert not _single("Click on Save ve on dakika bekleyin", "Bekleme on saniyedir.")
    assert not _single("Click on Save ve bekleyin", "Bekleme on dakikadır.")
    assert not _single("Bekleme süresi on dakikadır", "Bekleme on dakikadır.", source_language="")
    assert not _single("Turn on the switch", "Şalteri on kez açın.", source_language="en")


@pytest.mark.parametrize(
    ("source", "text"),
    [
        ("Bekleme süresi on dakikadır", "Bekleme 10 dakikadır."),
        ("Anahtarı ON konumuna getirin", "Anahtarı 10 numaralı konuma getirin."),
        ("Click on Save ve bekleyin", "Bekleme 10 olmalıdır."),
    ],
)
def test_word_on_in_the_source_never_backs_the_digit_ten(source: str, text: str) -> None:
    assert not _single(source, text)


@pytest.mark.parametrize(
    ("source", "text", "ok"),
    [
        ("Bekleme 10 dakika sürer", "On dakika bekleyin.", True),
        ("Fırın 10 mm açık; 3 dakika bekleyin", "On dakika bekleyin.", False),
        ("Paket: 10 adet somun, beş vida", "On beş vida takın.", False),
        ("Süre: 10", "Süre on.", True),
    ],
)
def test_written_ten_needs_the_same_following_word(source: str, text: str, ok: bool) -> None:
    assert _single(source, text) is ok


def test_switch_state_on_is_not_a_number() -> None:
    assert _single(
        "Set the power switch to ON", "Güç anahtarını ON konumuna getirin.", source_language="en"
    )


def test_english_on_is_not_a_number_in_an_english_answer() -> None:
    assert _single("Turn on the switch", "Turn on the switch.", language="en", source_language="en")


@pytest.mark.parametrize(
    ("source", "text"),
    [
        ("Price 1,234.50 USD", "Fiyat 1,234 USD."),
        ("Fiyat 1.234,50", "Fiyat 1.234."),
        ("Tarih 12.05.2024", "Yıl 2024."),
    ],
)
def test_value_cut_from_a_grouped_number_is_not_verified(source: str, text: str) -> None:
    assert not _single(source, text)


def test_grouped_number_written_the_same_is_verified() -> None:
    assert _single("Fiyat 1.234,50 TL", "Fiyat 1.234,50 TL.")


def test_gr_is_grams_only_in_a_turkish_document() -> None:
    assert _single("Weight 5 gr", "Ağırlık 5 gr.", source_language="en", language="en")
    assert not _single("Weight 5 gr", "Ağırlık 5 g.", source_language="en", language="en")
    assert _single("Ağırlık 5 gr", "Weight 5 g.", language="en")


@pytest.mark.parametrize(
    ("source", "text", "ok"),
    [
        ("Ağırlık: 500", "Ağırlık 500 gr.", False),
        ("Hacim: 2", "Hacim 2 lt.", False),
        # "g" ivme de olabilir: kaynaktaki "g" cümledeki "gr"yi karşılamaz, tersi karşılar.
        ("Ağırlık 500 g", "Ağırlık 500 gr.", False),
        ("Ağırlık 500 gr", "Ağırlık 500 g.", True),
        ("Hacim 2 lt", "Hacim 2 l.", True),
    ],
)
def test_turkish_unit_abbreviations_are_units(source: str, text: str, ok: bool) -> None:
    assert _single(source, text) is ok


TABLE_SOURCES = {
    1: PromptSource(
        number=1,
        text="Dim: BW005 | Description: Chest Width | LG: 25 | XL: 26 1/2",
        context="Tech pack · POMs",
        is_table_row=True,
    ),
    2: PromptSource(number=2, text="Dim: BW005 Chest Width LG 25 ve AB030 Across Shoulder"),
}


def test_code_of_the_quoted_table_row_may_appear_in_the_sentence() -> None:
    """Model değeri ("LG: 25") alıntılar, satırın kodunu cümleye yazar; aynı satırdır."""
    check = verify_item(item("LG beden BW005 25.", quote="LG: 25"), TABLE_SOURCES, "tr")

    assert check.ok, check.problems


def test_code_of_another_row_is_still_rejected() -> None:
    check = verify_item(item("LG beden AB030 25.", quote="LG: 25"), TABLE_SOURCES, "tr")

    assert not check.ok
    assert any("ab030" in problem for problem in check.problems)


def test_code_outside_the_quote_of_a_text_source_is_still_rejected() -> None:
    check = verify_item(item("LG beden AB030 25.", quote="LG 25", source_no=2), TABLE_SOURCES, "tr")

    assert not check.ok


COVER = PromptSource(
    number=1,
    text="Fit Approved, Hold Sampling Main Material # Sample Status Supplier Request Round",
)


def test_sentence_claiming_the_document_lacks_something_is_not_verified() -> None:
    """Ölçüm kaydındaki cümle (2026-11-15): alıntı birebir, sayı ve kod yok; yine de geçmemeli."""
    sentence = (
        "Numune durumu (Sample Status) belgede belirtilmemiştir; ancak Fit Onaylanmıştır"
        " (Fit Approved)."
    )

    check = verify_item(item(sentence, quote="Fit Approved"), {1: COVER}, "tr")

    assert not check.ok
    assert check.problems == (ABSENCE_CLAIM,)
    assert check.quote is None


@pytest.mark.parametrize(
    "sentence",
    [
        "Numune durumu belgede yer almıyor.",
        "Bu değer kaynakta bulunmuyor.",
        "Tolerans föyde geçmiyor.",
        "Ana kumaş için bilgi yok.",
        "Numune durumu belgede bulunamadı.",
        "BELGEDE BELİRTİLMEMİŞTİR.",
        "The sample status is not specified in the document.",
        "The document does not mention the supplier round.",
        "There is no information about the fit type.",
    ],
)
def test_absence_claims_in_turkish_and_english_are_caught(sentence: str) -> None:
    check = verify_item(item(sentence, quote="Fit Approved"), {1: COVER}, "tr")

    assert ABSENCE_CLAIM in check.problems


@pytest.mark.parametrize(
    "sentence",
    [
        "Başlamış bir siparişten transfer yapılmasına izin verilmez.",
        "Numune durumu Fit Approved olarak belirtilmiştir.",
        "Değer kapak sayfasında belirtilmektedir.",
        "Numune durumunun belirtilmesi gerekir.",
        "Bu değer finansal raporlamada kullanılır; başka işlevi etkilemez.",
        "Yetkisi olmayan kullanıcı listeyi görüntüleyebilir.",
        "Transferring from a started order is not allowed.",
        "Yük %200'ü geçerse çubuğun tepesi gösterilmez.",
        "Planlama tahtası açıkken FastReact kapanmaz.",
        "Fiyat henüz verilmedi.",
    ],
)
def test_negatives_and_positive_statements_are_not_absence_claims(sentence: str) -> None:
    check = verify_item(item(sentence, quote="Fit Approved"), {1: COVER}, "tr")

    assert ABSENCE_CLAIM not in check.problems


def test_absence_stated_by_the_source_itself_passes() -> None:
    source = PromptSource(number=1, text="Tolerance: not specified for this size.")

    turkish = verify_item(
        item("Bu beden için tolerans belirtilmemiştir.", quote=source.text), {1: source}, "tr"
    )
    english = verify_item(
        item("Tolerance is not specified.", quote="not specified"), {1: source}, "en"
    )

    assert turkish.ok and english.ok


@pytest.mark.parametrize(
    "sentence",
    [
        "Kaynaklarda sadece Dış paça için bilgi var.",
        "Kaynaklarda sadece Kalça için bilgi var.",
        "Kaynaklarda sadece Bel için bilgi var.",
        "Belgede yalnızca numune durumu yazıyor.",
        "The document only covers the hip measurement.",
    ],
)
def test_sentence_about_the_sources_without_a_value_is_not_verified(sentence: str) -> None:
    """Sınır seti A4 (2026-11-17): alıntı birebir, sayı ve kod yok; kapsam iddiası denetlenemez."""
    check = verify_item(item(sentence, quote="İç paça"), SOURCES, "tr")

    assert check.problems == (ABSENCE_CLAIM,)


def test_sentence_about_the_sources_with_a_checked_value_passes() -> None:
    check = verify_item(
        item("Belgede belirtildiğine göre iç paça 76,5.", quote="İç paça | M: 76,5"), SOURCES, "tr"
    )

    assert check.ok


def test_source_talk_from_the_source_itself_passes() -> None:
    source = PromptSource(number=1, text="Bu belgede yalnızca erkek ürünleri anlatılır.")

    check = verify_item(
        item("Belgede yalnızca erkek ürünleri anlatılır.", quote=source.text), {1: source}, "tr"
    )

    assert check.ok


BOM_ROW = (
    "Material Details: TT-100157/ECO100 Recycled Thread | Qty: 60.0000 | "
    "100: White // Venom Red: White 100 | 001: Black // Blue Haze: Black 001"
)
BOM_SOURCES = {
    1: PromptSource(
        number=1, text=BOM_ROW, title="6029322-SS27-6029322-US-TORCH", is_table_row=True
    ),
    2: PromptSource(number=2, text="Season: SS27", title="6013448-SS26-6013448-US-NEXUS"),
}
BLACK = "001: Black // Blue Haze: Black 001"


def _bom_check(
    text: str, asked: str, previous: str = "", source_no: int = 1
) -> tuple[VerificationStatus, tuple[str, ...]]:
    result = verify_answer(
        answer(item(text, quote=BLACK, source_no=source_no)), BOM_SOURCES, "tr", asked, previous
    )
    return result.status, result.problems


def test_model_number_of_the_cited_document_passes_when_the_user_said_it() -> None:
    status, problems = _bom_check(
        "6029322 modelinde TT-100157 ipliği 001 kodunda Black 001 renktedir.",
        asked="6029322'de TT-100157 ipliği 001 kodunda hangi renk",
    )

    assert (status, problems) == (VerificationStatus.VERIFIED, ())


def test_model_number_from_the_previous_turn_passes() -> None:
    status, _ = _bom_check(
        "6029322 modelinde TT-100157 ipliği 001 renk yolunda Black 001'dir.",
        asked="peki 001?",
        previous="001 6029322 tt-100157",
    )

    assert status is VerificationStatus.VERIFIED


def test_model_number_the_user_did_not_say_is_hidden() -> None:
    status, problems = _bom_check(
        "6029322 modelinde TT-100157 ipliği 001 kodunda Black 001 renktedir.",
        asked="TT-100157 ipliği 001 kodunda hangi renk",
    )

    assert status is VerificationStatus.FAILED
    assert "6029322" in problems[0]


def test_other_number_than_the_title_model_number_is_hidden() -> None:
    status, problems = _bom_check(
        "6029322 modelinde TT-100157 ipliği Black 001 renktedir; miktarı 60.",
        asked="6029322'de TT-100157 ipliği 001 kodunda hangi renk",
    )

    assert status is VerificationStatus.FAILED
    assert problems == ("cümlede kendi alıntısında olmayan sayı: ['60']",)


def test_model_number_of_another_document_is_hidden() -> None:
    status, problems = _bom_check(
        "6013448 modelinde TT-100157 ipliği 001 kodunda Black 001 renktedir.",
        asked="6013448'de TT-100157 ipliği 001 kodunda hangi renk",
    )

    assert status is VerificationStatus.FAILED
    assert "6013448" in problems[0]


@pytest.mark.parametrize(
    ("title", "value"),
    [
        ("Klima 12000 BTU Kılavuzu", "12000 BTU"),
        ("Sipariş 45000", "45000 adet"),
        ("Klima-12000-BTU", "12000 BTU"),
        ("Sipariş-45000", "45000 adet"),
    ],
)
def test_title_number_outside_the_first_part_is_hidden(title: str, value: str) -> None:
    number = value.split()[0]
    sources = {1: PromptSource(number=1, text="Renk: Black 001", title=title)}
    result = verify_answer(
        answer(item(f"Miktar {value}, renk Black 001.", quote="Renk: Black 001")),
        sources,
        "tr",
        asked=f"{number} için renk ne?",
    )

    assert result.status is VerificationStatus.FAILED
    assert number in result.problems[0]


# Alıntıyı içeren hücrenin başlığındaki sayı (renk yolu, sayısal beden), kullanıcı söylediyse.
@pytest.mark.parametrize(
    ("text", "quote", "asked", "passes"),
    [
        # a. renk yolu soruda, değer "Black" alıntılandı
        ("İplik 001 kodunda Black renktedir.", "Black", "TT-100157 001 hangi renk?", True),
        # b. renk yolu soruda yok
        ("İplik 001 kodunda Black renktedir.", "Black", "TT-100157 hangi renk?", False),
        # c. sayı başka hücrenin (100) başlığı
        ("İplik 100 kodunda Black renktedir.", "Black", "TT-100157 100 hangi renk?", False),
        # f. cümlede 001, alıntı 100 sütunundan (niteleyici kuralıyla birlikte)
        ("İplik 001 kodunda White renktedir.", "White", "TT-100157 001 hangi renk?", False),
    ],
)
def test_number_from_the_quoted_cell_label_passes_when_the_user_said_it(
    text: str, quote: str, asked: str, passes: bool
) -> None:
    result = verify_answer(answer(item(text, quote=quote)), BOM_SOURCES, "tr", asked)

    assert (result.status is VerificationStatus.VERIFIED) is passes, result.problems
    if not passes:
        assert any("sayı" in problem for problem in result.problems)


SIZE_ROW = "Ölçü noktası: Bel | 36: 72,0 | 38: 76,0 | 40: 80,0"
SIZE_SOURCES = {1: PromptSource(number=1, text=SIZE_ROW, title="Föy", is_table_row=True)}


@pytest.mark.parametrize(
    ("text", "asked", "passes"),
    [
        # d. sayısal beden sütunu: soruda 38 var / yok
        ("38 beden bel 76,0.", "38 beden bel kaç?", True),
        ("38 beden bel 76,0.", "bel kaç?", False),
        # e. sütun adı alıntılanan hücrenin değil, aynı satırdaki başka hücrenin başlığı
        ("36 beden bel 76,0.", "36 beden bel kaç?", False),
    ],
)
def test_numeric_size_label_of_the_quoted_cell(text: str, asked: str, passes: bool) -> None:
    result = verify_answer(answer(item(text, quote="76,0")), SIZE_SOURCES, "tr", asked)

    assert (result.status is VerificationStatus.VERIFIED) is passes, result.problems


@pytest.mark.parametrize(
    ("row", "quotes", "asked", "text"),
    [
        # alıntı başka hücrenin sayısının parçası ("72" / "72,5")
        ("Ölçü: Bel | 36: 72 | 38: 72,5", ["72"], "38 beden bel kaç?", "38 beden bel 72."),
        # alıntı birden çok hücrede geçiyor ("Black" / "Jet Black")
        (
            "001: Navy: Black 001 | 100: Red: Jet Black 690",
            ["Black"],
            "100 hangi renk?",
            "100 kodunda Black renktedir.",
        ),
        # iki alıntı iki ayrı hücreden
        (
            "Ölçü: Bel | 36: 72,0 | 38: 76,0",
            ["72,0", "76,0"],
            "38 beden bel kaç?",
            "38 beden bel 72,0, 76,0 değil.",
        ),
        # başlık sayısı değerin yerine yazılmış
        ("Ölçü: Bel | 36: 72,0 | 38: 76,0", ["76,0"], "38 beden bel kaç?", "Bel ölçüsü 38."),
    ],
)
def test_cell_label_exemption_stays_closed_when_the_cell_is_not_certain(
    row: str, quotes: list[str], asked: str, text: str
) -> None:
    sources = {1: PromptSource(number=1, text=row, title="Föy", is_table_row=True)}
    model_item = ModelItem(text=text, quotes=tuple(Quote(source_no=1, text=q) for q in quotes))

    result = verify_answer(answer(model_item), sources, "tr", asked)

    assert result.status is VerificationStatus.FAILED
    assert any("sayı" in problem for problem in result.problems)


def test_cell_label_exemption_does_not_apply_to_prose() -> None:
    sources = {1: PromptSource(number=1, text="Adım 2: Vida 4 tur çevrilir.", title="Kılavuz")}

    result = verify_answer(
        answer(item("Vida 2 tur çevrilir.", quote="Vida")), sources, "tr", "adım 2'de vida kaç tur?"
    )

    assert result.status is VerificationStatus.FAILED
