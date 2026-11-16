"""Okuma ölçümünün doğru cevap biçimi ve değer eşdeğerliği.

Doğru cevap değer–konum temellidir: her değer belge ve sayfayla, tablodaysa satır anahtarı ve
sütun başlığıyla, formdaysa etiketiyle kaydedilir. Biçim hem sentetik belgelerin üreticisinden
hem de dijital PDF'lerin metin katmanından doldurulabilir (kutu, metnin sayfadaki yeridir).

Eşdeğerlik kuralları ölçümden önce yazıldı (2026-11-16) ve yalnız yazım biçimine bakar; değeri
tahmin etmez, bir rakamı başka rakama çevirmez:

1. Kesir yazımı: "⅜", "³⁄₈", "3⁄8", "3 / 8" ve LaTeX "\\frac{3}{8}" aynıdır: "3/8". Tam sayıya
   yapışık kesir karakteri ("27⅜", "27³⁄₈") "27 3/8" sayılır. "271/2" ile "27 1/2" farklıdır.
2. Eksi işareti: "-", "−", "–" ve "‑" aynıdır; işaretle sayı arasındaki boşluk yok sayılır.
3. Ondalık ayırıcı eşdeğer sayılmaz: "1.500" ile "1,500" farklı değerler olabilir. Yalnız
   rakamlar arasındaki virgül–nokta farkıyla ayrılan değer "ayraç farkı" olarak ayrı raporlanır
   (`separator_only`); doğru da yanlış karakter de sayılmaz (2026-11-16 düzeltmesi).
4. Boşluk: art arda boşluklar ve satır sonları tek boşluktur; baştaki ve sondaki boşluk yok
   sayılır; "%" ve kesir çizgisinden önceki ve sonraki boşluk yok sayılır.
5. Tırnaklar: inç işareti ″ ve kıvrık tırnaklar düz tırnaktır; LaTeX "$" işaretleri yok sayılır.
6. Büyük-küçük harf ve diğer bütün karakterler olduğu gibi karşılaştırılır.
"""

import re
from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

_VULGAR = {
    "½": "1/2",
    "⅓": "1/3",
    "⅔": "2/3",
    "¼": "1/4",
    "¾": "3/4",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
}
_SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
_SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_SCRIPT_FRACTION_RE = re.compile(r"(\d?)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)[⁄/∕]([₀₁₂₃₄₅₆₇₈₉0-9]+)")
_LATEX_FRACTION_RE = re.compile(r"(\d?)\s*\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}")
_MINUS_RE = re.compile(r"[−–‑]")
_SIGN_SPACE_RE = re.compile(r"(?<![\w)])- +(?=\d)")
_SEPARATOR_RE = re.compile(r"(?<=\d)[.,](?=\d)")
_SLASH_SPACE_RE = re.compile(r"(?<=\d) */ *(?=\d)")
_QUOTES = str.maketrans({"″": '"', "“": '"', "”": '"', "’": "'", "‘": "'", "$": None})


def _script_fraction(match: re.Match[str]) -> str:
    lead, top, bottom = match.groups()
    space = " " if lead else ""
    return f"{lead}{space}{top.translate(_SUPER)}/{bottom.translate(_SUB)}"


def canonical(text: str) -> str:
    """Değerin karşılaştırılan yazımı (kurallar modül açıklamasında)."""
    text = _LATEX_FRACTION_RE.sub(
        lambda m: f"{m.group(1)} {m.group(2)}/{m.group(3)}".lstrip(), text
    )
    for glyph, plain in _VULGAR.items():
        text = re.sub(rf"(\d?){glyph}", rf"\1 {plain}", text)
    text = _SCRIPT_FRACTION_RE.sub(_script_fraction, text)
    text = text.replace("⁄", "/").replace("∕", "/").translate(_QUOTES)
    text = _MINUS_RE.sub("-", text)
    text = " ".join(text.split())
    text = _SIGN_SPACE_RE.sub("-", text)
    text = _SLASH_SPACE_RE.sub("/", text)
    return text.replace(" %", "%")


def same_value(a: str, b: str) -> bool:
    return canonical(a) == canonical(b)


def separator_only(a: str, b: str) -> bool:
    """İki değer yalnız rakamlar arasındaki virgül–nokta farkıyla ayrılıyor ("ayraç farkı")."""
    left, right = canonical(a), canonical(b)
    return left != right and _SEPARATOR_RE.sub("·", left) == _SEPARATOR_RE.sub("·", right)


class ValueKind(StrEnum):
    CELL = "cell"
    """Tablo hücresi: satır anahtarı ve sütun başlığıyla."""
    PAIR = "pair"
    """Form satırı: etiket ve değer."""
    TEXT = "text"
    """Başlık, not, yorum satırı: yalnız metin."""


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


Box = tuple[float, float, float, float]
"""PDF noktası, sayfanın sol-üst köşesine göre (sol, üst, sağ, alt)."""


class TruthValue(_Model):
    kind: ValueKind
    value: str
    table: int | None = None
    row_key: str | None = None
    column: str | None = None
    label: str | None = None
    box: Box | None = None


class TruthPage(_Model):
    page: int
    page_type: str
    values: tuple[TruthValue, ...]


class TruthDocument(_Model):
    doc_id: str
    source: str
    """"synthetic" (üreticiden) ya da "digital" (metin katmanından)."""
    seed: int | None = None
    pdf_sha256: str | None = None
    pages: tuple[TruthPage, ...]


def _text_in_box(page: object, box: Box) -> str:
    height = page.get_height()  # type: ignore[attr-defined]
    left, top, right, bottom = box
    textpage = page.get_textpage()  # type: ignore[attr-defined]
    return str(textpage.get_text_bounded(left, height - bottom, right, height - top))


def layer_mismatches(pdf: Path, truth: TruthDocument) -> list[tuple[int, str, str]]:
    """Doğru cevaptaki her değer, dijital PDF'te kendi kutusunda aynen okunmalı. Uymayanlar:
    (sayfa, beklenen, metin katmanında okunan)."""
    import pypdfium2

    document = pypdfium2.PdfDocument(pdf)
    try:
        found: list[tuple[int, str, str]] = []
        for page in truth.pages:
            target = document[page.page - 1]
            for value in page.values:
                if value.box is None:
                    continue
                read = _text_in_box(target, value.box)
                if not same_value(read, value.value):
                    found.append((page.page, value.value, read))
        return found
    finally:
        document.close()


def write_truth(documents: Sequence[TruthDocument], directory: Path) -> None:
    for document in documents:
        (directory / f"{document.doc_id}.json").write_text(
            document.model_dump_json(indent=1), encoding="utf-8"
        )
