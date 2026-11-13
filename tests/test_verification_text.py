import pytest

from visual_agent.verification.text import (
    canon_chars,
    identifiers_in,
    normalize,
    numbers_in,
    word_numbers,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("S-7300A makinesinde 11 dikiş, E-07 hatası, ASTM D6193", {"11"}),
        ("10-14 dikiş", {"10", "14"}),
        ("Adımlar:\n1. Gücü kapatın.\n4. Somunu (2) çevirin.\n12) Kontrol edin", {"2"}),
        ("Şu adımları izleyin: 1) Güçten ayırın. 2) Makine başını 90° kaldırın.", {"90"}),
        ("Hız 4. kademeye alınır, 3000 sti/min", {"4", "3000"}),
        ("12mm ve 3/16", {"12", "3", "16"}),
        ("Bantlar sol kolda [1, 2]. Hız 5000 [2,3,5]; ayar [1-3] ve [1; 4].", {"5000"}),
        ("ekipmanlar: [1, 5] 1. Gözlük takın. [1, 5] 2. Uygun ayakkabı giyin.", set()),
        ("Paneldeki düğmeler [1]:<br>1. Saat ekranı<br>2. Seçici düğme", set()),
        ("varsayılan 2.00, ayar 0,50 ve .5 mm", {"2", "0.5"}),
        ("Keep pressing the button ❶", {"1"}),
        ("Ceza tutarı 1.000 TL", {"1.000"}),
        ("Parti 1.500 adet, ayrıca 1,5 kg", {"1.500", "1.5"}),
        ("Kalınlık 0,500 mm", {"0.5"}),
        ("Sıcaklık -5 °C, en az −10 ve (-2)", {"-5", "-10", "-2"}),
        ("5-10 mm aralığı", {"5", "10"}),
        ("Bel 40,0 ya da 40", {"40"}),
        ("30. günde ödeme yapılır", {"30"}),
    ],
)
def test_numbers_in(text: str, expected: set[str]) -> None:
    assert numbers_in(text) == expected


def test_vulgar_fraction_reads_as_the_same_number() -> None:
    assert numbers_in("½ inch") == numbers_in("1/2 inch")


def test_word_numbers_ignore_ambiguous_words() -> None:
    text = "every six months, a team of two workers, back on again, once"
    assert word_numbers(text, "en") == {
        "6",
        "2",
    }


def test_normalize_ignores_multiplication_sign_style() -> None:
    assert normalize("Please use the needle DC × 27") == normalize("Please use the needle DC X 27")


def test_canon_chars_reads_circled_digits() -> None:
    assert canon_chars("❶ ➋ ⓷ ⓬ ① ⑳") == "1 2 3 12 1 20"


def test_normalize_handles_width_and_superscript() -> None:
    assert normalize("Ｘ²") == "x2"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Kolon SIPARIS_TARIHI olarak değişir.", {"siparis_tarihi"}),
        ("PNT-4417 modelinde", {"pnt-4417"}),
        ("E050 hatası", {"e050"}),
        ("siparis_tarihi alanı", {"siparis_tarihi"}),
        ("`dbo.Musteri` tablosu", {"dbo.musteri"}),
        ("SİPARİŞ_TARİHİ kolonu", {"sipariş_tarihi"}),
        ("Normal bir Türkçe cümle, iki-üç kelime.", set()),
    ],
)
def test_identifiers_in(text: str, expected: set[str]) -> None:
    assert identifiers_in(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [("İki gün", {"2"}), ("ALTI adım", {"6"}), ("SIX steps", {"6"}), ("Üç kez", {"3"})],
)
def test_word_numbers_read_capitalised_turkish_and_english(text: str, expected: set[str]) -> None:
    assert word_numbers(text, "tr") == expected


@pytest.mark.parametrize(
    ("text", "language", "expected"),
    [
        ("Bekleme on dakikadır.", "tr", {"10"}),
        ("Bekleme ON dakikadır.", "tr", {"10"}),
        ("Turn on the switch.", "en", set()),
        ("Turn on the switch.", "", set()),
        ("Bekleme on dakikadır.", "", set()),
        ("İki ya da two.", "en", {"2"}),
    ],
)
def test_turkish_ten_counts_only_in_turkish_text(
    text: str, language: str, expected: set[str]
) -> None:
    assert word_numbers(text, language) == expected
