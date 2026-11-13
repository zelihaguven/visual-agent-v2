"""Okuma metni: değer kaybolmadan, kulakla anlaşılır biçime dönüşür."""

import pytest

from visual_agent.voice.reading import CODE_ON_SCREEN, spoken_text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Bel 42,5 cm.", "Bel kırk iki virgül beş santimetre."),
        ("Dış paça 103,0'dır.", "Dış paça yüz üç virgül sıfırdır."),
        ("Ölçü 42,5 cm'dir.", "Ölçü kırk iki virgül beş santimetredir."),
        ("Tolerans 0,05 mm.", "Tolerans sıfır virgül sıfır beş milimetre."),
        ("Fiyat 1200 TL.", "Fiyat bin iki yüz Türk lirası."),
        ("Oran %5.", "Oran yüzde beş."),
        ("Ölçü 11 (± 1) cm.", "Ölçü on bir (artı eksi bir) santimetre."),
        ("Süre 75 saniyedir.", "Süre yetmiş beş saniyedir."),
        ("Yıl 2026.", "Yıl iki bin yirmi altı."),
        ("Adet 21000.", "Adet yirmi bir bin."),
    ],
)
def test_numbers_and_units_are_read_in_turkish(text: str, expected: str) -> None:
    assert spoken_text(text, "tr") == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("PNT-1162 modeli", "pe ne te bir bir altı iki modeli"),
        ("Etiket ETK-3353'tür.", "Etiket e te ke üç üç beş üçtür."),
        ("Hata E050 oldu.", "Hata e sıfır beş sıfır oldu."),
        ("L beden", "le beden"),
        ("XL beden", "iks le beden"),
    ],
)
def test_codes_are_spelled_so_each_character_is_heard(text: str, expected: str) -> None:
    assert spoken_text(text, "tr") == expected


def test_technical_names_are_read_as_words() -> None:
    assert spoken_text("DEPO_SAYIM tablosu", "tr") == "depo sayım tablosu"


def test_ordinary_words_are_left_alone() -> None:
    text = "Bu bilgi kaynakta yazıyor."

    assert spoken_text(text, "tr") == text


def test_other_languages_are_not_rewritten() -> None:
    text = "Waist is 42.5 cm for PNT-1162."

    assert spoken_text(text, "en") == text


def test_command_is_never_read_aloud() -> None:
    command = "ALTER TABLE DEPO_SAYIM RENAME COLUMN SIP_TARIH TO SIPARIS_TARIHI;"

    assert spoken_text(command, "tr", has_code=True) == CODE_ON_SCREEN


def test_sentence_that_names_a_command_points_to_the_screen() -> None:
    text = "DEPO_SAYIM için komut ALTER TABLE ifadesidir."

    assert spoken_text(text, "tr", has_code=True) == CODE_ON_SCREEN


def test_plain_sentence_about_a_command_is_read_then_points_to_the_screen() -> None:
    text = "Kolon adı şu komutla değişir."

    assert spoken_text(text, "tr", has_code=True) == f"{text} {CODE_ON_SCREEN}"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Binlik mi ondalık mı belirsiz: ayraçtan sonrası rakam rakam, değer yorumlanmaz.
        ("Parti 1.500 adet.", "Parti bir nokta beş sıfır sıfır adet."),
        ("Parti 1,500 adet.", "Parti bir virgül beş sıfır sıfır adet."),
        # Türkçe biçim (binlik nokta, ondalık virgül) belirsiz değil.
        ("Fiyat 1.234,50 TL.", "Fiyat bin iki yüz otuz dört virgül beş sıfır Türk lirası."),
        ("Toplam 1.234.567 adet.", "Toplam bir iki üç dört beş altı yedi adet."),
        # Başka karışık biçimler yazıldığı gibi okunur.
        ("Değer 1,234.50.", "Değer bir virgül iki üç dört nokta beş sıfır."),
        ("Tarih 12.05.2024.", "Tarih on iki nokta sıfır beş nokta iki sıfır iki dört."),
        ("Oran 12%.", "Oran yüzde on iki."),
        ("Oran %1.500.", "Oran yüzde bir nokta beş sıfır sıfır."),
    ],
)
def test_grouped_numbers_never_change_value(text: str, expected: str) -> None:
    assert spoken_text(text, "tr") == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Ağırlık 500 gr.", "Ağırlık beş yüz gram."),
        # "g" ivme de olabilir ("50 g"): yazıldığı gibi kalır.
        ("Titreşim 50 g.", "Titreşim elli g."),
        ("Hacim 2 lt.", "Hacim iki litre."),
        ("Fiyat 5 tl.", "Fiyat beş Türk lirası."),
        ("Fiyat 5 Tl.", "Fiyat beş Türk lirası."),
        # Tek harfli birim büyük harfle yazılırsa beden olabilir; birim sayılmaz.
        ("Beden 38 M.", "Beden otuz sekiz me."),
        ("Beden 42 L.", "Beden kırk iki le."),
    ],
)
def test_units_come_from_the_shared_unit_list(text: str, expected: str) -> None:
    assert spoken_text(text, "tr") == expected
