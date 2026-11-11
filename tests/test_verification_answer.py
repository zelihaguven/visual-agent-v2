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
from visual_agent.verification.answer import verify_answer, verify_item

ROW = "İç paça | M: 76,5 | Tolerans: 0,5"
SOURCES = {
    1: PromptSource(number=1, text=ROW, context="PNT-4417 ölçü föyü"),
    2: PromptSource(number=2, text="Kullanım basıncı 11 (± 1) bar olmalıdır."),
    3: PromptSource(
        number=3,
        text="ALTER TABLE SIPARIS RENAME COLUMN SIP_TARIH TO SIPARIS_TARIHI;",
        is_code=True,
    ),
    4: PromptSource(
        number=4,
        text="Şekil: düğme solda. Otomatik açıklama: kırmızı düğme.",
        generated="Otomatik açıklama: kırmızı düğme.",
    ),
    5: PromptSource(number=5, text="Debi 299.999% olarak okundu.", ocr_uncertain=("299.999%",)),
}


def item(text: str, quote: str = "M: 76,5", source_no: int = 1) -> ModelItem:
    return ModelItem(text=text, quotes=(Quote(source_no=source_no, text=quote),))


def answer(*items: ModelItem) -> ModelAnswer:
    return ModelAnswer(kind=AnswerKind.ANSWER, items=items)


def test_correct_item_passes() -> None:
    assert verify_item(item("İç paça 76,5 cm."), SOURCES).ok


def test_quote_must_exist_in_the_source() -> None:
    check = verify_item(item("İç paça 76,5 cm.", quote="M: 76,5 cm tam"), SOURCES)

    assert not check.ok
    assert "birebir" in check.problems[0]


def test_unknown_source_number_fails() -> None:
    assert not verify_item(item("İç paça 76,5 cm.", source_no=9), SOURCES).ok


def test_number_must_come_from_its_own_quote() -> None:
    check = verify_item(item("İç paça 78 cm.", quote="M: 76,5"), SOURCES)

    assert not check.ok
    assert "78" in check.problems[0]


def test_identifier_not_in_quote_or_source_context_fails() -> None:
    check = verify_item(item("PNT-4471 için iç paça 76,5 cm."), SOURCES)

    assert not check.ok
    assert "pnt-4471" in check.problems[0]


def test_identifier_from_cited_source_title_is_allowed() -> None:
    assert verify_item(item("PNT-4417 için iç paça 76,5 cm."), SOURCES).ok


def test_tolerance_cannot_be_dropped() -> None:
    quote = "11 (± 1) bar"

    assert not verify_item(item("Basınç 11 bar.", quote=quote, source_no=2), SOURCES).ok
    assert verify_item(item("Basınç 11 (± 1) bar.", quote=quote, source_no=2), SOURCES).ok


def test_foreign_alphabet_fails() -> None:
    assert not verify_item(item("İç paça 76,5 金额."), SOURCES).ok


def test_uncertain_ocr_value_blocks_the_item() -> None:
    check = verify_item(item("Debi 299.999%.", quote="299.999%", source_no=5), SOURCES)

    assert not check.ok
    assert "OCR" in check.problems[0]


OCR_ROW = "Dış paça | S: 100,5 | M: 102,5 | Tolerans (cm): 10"
OCR_SOURCES = {1: PromptSource(number=1, text=OCR_ROW, ocr_uncertain=("10",), from_ocr=True)}


def test_uncertain_value_does_not_hide_a_longer_value_that_contains_it() -> None:
    check = verify_item(item("M beden dış paça 102,5.", quote="M: 102,5"), OCR_SOURCES)

    assert check.ok, check.problems


def test_uncertain_value_itself_is_still_hidden() -> None:
    check = verify_item(item("Tolerans 10 cm.", quote="Tolerans (cm): 10"), OCR_SOURCES)

    assert not check.ok
    assert "OCR" in check.problems[0]


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

    assert not verify_item(item(text, quote=source), sources).ok


def test_same_value_written_the_same_way_still_passes() -> None:
    sources = {1: PromptSource(number=1, text="Çalışma sıcaklığı -5 °C, ceza 1.000 TL")}
    quote = "Çalışma sıcaklığı -5 °C, ceza 1.000 TL"

    assert verify_item(item("Sıcaklık -5 °C, ceza 1.000 TL.", quote=quote), sources).ok


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

    assert not verify_item(item(text, quote=source), sources).ok


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

    assert verify_item(item(text, quote=source), sources).ok


@pytest.mark.parametrize(
    ("source", "text"),
    [
        ("Dikiş payı 5 mm", "Dikiş payı 5 cm."),
        ("Çalışma sıcaklığı 40 °C", "Çalışma sıcaklığı 40 °F."),
        ("Bekleme 30 sn", "Bekleme 30 dakika."),
    ],
)
def test_a_value_cannot_change_its_unit(source: str, text: str) -> None:
    sources = {1: PromptSource(number=1, text=source)}

    assert not verify_item(item(text, quote=source), sources).ok


@pytest.mark.parametrize(
    ("source", "text"),
    [
        ("Dikiş payı 5 mm", "Dikiş payı 5 mm'dir."),
        ("Bekleme 30 dk", "Bekleme 30 dakika."),
        ("Bel | M: 40,5 | L: 42,5", "M beden bel 40,5 cm."),
        ("Pay 5 mm, kenar 5 cm", "Kenar 5 cm."),
    ],
)
def test_same_or_unstated_unit_still_passes(source: str, text: str) -> None:
    sources = {1: PromptSource(number=1, text=source)}

    assert verify_item(item(text, quote=source), sources).ok


def test_cut_quote_at_the_limit_is_tolerated() -> None:
    long_text = "a" * 20 + " " + " ".join(f"kelime{i}" for i in range(40))
    sources = {1: PromptSource(number=1, text=long_text)}
    cut_quote = long_text[:140] + " bozuk**"

    assert verify_item(item("Metin burada.", quote=cut_quote), sources).ok


def test_short_quote_with_different_ending_is_not_tolerated() -> None:
    assert not verify_item(item("Metin.", quote="M: 76,5 başka"), SOURCES).ok


def test_field_label_quote_matches_a_cell() -> None:
    assert verify_item(item("Tolerans 0,5.", quote="Tolerans: 0,5"), SOURCES).ok


def test_quote_joining_two_cells_is_rejected() -> None:
    assert not verify_item(item("76,5.", quote="M: 76,5 | Tolerans: 0,5 fazla"), SOURCES).ok


def test_code_reference_supplies_identifiers_without_a_quote() -> None:
    reference = ModelItem(text="SIP_TARIH kolonu SIPARIS_TARIHI olur.", code_source_no=3)

    assert verify_item(reference, SOURCES).ok


def test_code_reference_must_point_to_a_code_source() -> None:
    reference = ModelItem(text="Komut bu.", code_source_no=1)

    assert not verify_item(reference, SOURCES).ok


def test_wrong_identifier_next_to_code_reference_fails() -> None:
    reference = ModelItem(text="SIP_TARIHI kolonu değişir.", code_source_no=3)

    assert not verify_item(reference, SOURCES).ok


def test_item_from_generated_figure_text_makes_answer_partial() -> None:
    result = verify_answer(
        answer(item("Şekle göre düğme kırmızı.", quote="kırmızı düğme", source_no=4)), SOURCES
    )

    assert result.status is VerificationStatus.PARTIAL


def test_item_from_ocr_text_is_marked_and_makes_answer_partial() -> None:
    sources = {1: PromptSource(number=1, text="Bağlantı limiti: 386", from_ocr=True)}
    candidate = item("Bağlantı limiti 386.", quote="Bağlantı limiti: 386")

    assert verify_item(candidate, sources).ok
    assert verify_item(candidate, sources).from_figure
    assert verify_answer(answer(candidate), sources).status is VerificationStatus.PARTIAL


def test_one_ocr_item_makes_the_whole_answer_partial() -> None:
    sources = {
        1: PromptSource(number=1, text="M: 76,5"),
        2: PromptSource(number=2, text="L: 80,5", from_ocr=True),
    }
    result = verify_answer(
        answer(item("M 76,5.", quote="M: 76,5"), item("L 80,5.", quote="L: 80,5", source_no=2)),
        sources,
    )

    assert result.status is VerificationStatus.PARTIAL


def test_command_read_by_ocr_is_marked() -> None:
    sources = {1: PromptSource(number=1, text="DROP TABLE T;", is_code=True, from_ocr=True)}
    command = ModelItem(text="Tabloyu siler.", code_source_no=1)

    assert verify_item(command, sources).from_figure


def test_code_written_without_its_hyphen_matches_the_source() -> None:
    sources = {1: PromptSource(number=1, text="GML-6473 Kalça: 48,0")}
    candidate = item("GML6473 kalça 48,0.", quote="GML-6473 Kalça: 48,0")

    assert verify_item(candidate, sources).ok


def test_all_items_valid_is_verified() -> None:
    assert verify_answer(answer(item("76,5 cm.")), SOURCES).status is VerificationStatus.VERIFIED


def test_one_bad_item_fails_the_answer_but_keeps_item_results() -> None:
    result = verify_answer(answer(item("76,5 cm."), item("78 cm.")), SOURCES)

    assert result.status is VerificationStatus.FAILED
    assert [check.ok for check in result.items] == [True, False]


def test_repeated_sentence_fails() -> None:
    sentence = "Bu ayar her zaman sol tarafta yapılır."

    result = verify_answer(answer(item(sentence), item(sentence)), SOURCES)

    assert result.status is VerificationStatus.FAILED


def test_empty_answer_fails() -> None:
    assert verify_answer(answer(), SOURCES).status is VerificationStatus.FAILED


def test_not_found_is_reported() -> None:
    result = verify_answer(ModelAnswer(kind=AnswerKind.NOT_FOUND), SOURCES)

    assert result.status is VerificationStatus.NOT_FOUND


def test_clarification_needs_real_sources() -> None:
    def clarify(*numbers: int) -> ModelAnswer:
        options = tuple(ClarifyOption(source_no=number) for number in numbers)
        return ModelAnswer(
            kind=AnswerKind.CLARIFY,
            clarify=ClarifyRequest(question="Hangisi?", options=options),
        )

    valid = verify_answer(clarify(1, 2), SOURCES)

    assert valid.status is VerificationStatus.CLARIFY
    assert valid.clarify_options == (1, 2)
    assert verify_answer(clarify(1, 9), SOURCES).status is VerificationStatus.FAILED


def test_concurrent_verification_gives_identical_results() -> None:
    target = answer(item("76,5 cm."), item("78 cm."))
    expected = verify_answer(target, SOURCES)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: verify_answer(target, SOURCES), range(200)))

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

    assert verify_item(item("Kontrol edin.", quote=quote), sources).ok is expected


def test_one_source_can_hold_all_options_of_a_clarification() -> None:
    answer = ModelAnswer(
        kind=AnswerKind.CLARIFY,
        items=(),
        clarify=ClarifyRequest(question="Hangi beden?", options=(ClarifyOption(source_no=1),)),
    )

    result = verify_answer(answer, SOURCES)

    assert result.status is VerificationStatus.CLARIFY
    assert result.clarify_options == (1,)
