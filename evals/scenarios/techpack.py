"""Sentetik tech pack içeriği: okuma ölçümünün kilitli seti için.

Yalnız gerçek föylerin sayfa yapısı alındı; bütün adlar, kodlar ve değerler bu üreticide
rastgele üretilir. Altı sayfa türü değer taşır: kapak formu, yorumlar, numune değerlendirme
tablosu, malzeme listesi, ölçü tablosu ve fark tablosu. Görünüş (yazı tipi, sütun ve satır
sayısı, çizgi, kesir yazımı) belgeden belgeye değişir; çizim `evals/render/techpack_pdf.py`.
"""

from dataclasses import dataclass, field
from random import Random

SIZE_SETS: tuple[tuple[str, ...], ...] = (
    ("XS", "SM", "MD", "LG", "XL", "XXL", "3XL", "4XL", "5XL"),
    ("XS", "S", "M", "L", "XL", "XXL"),
    ("34", "36", "38", "40", "42", "44", "46", "48"),
    ("2", "4", "6", "8", "10", "12", "14"),
    ("S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "6XL", "7XL", "8XL"),
)
_SYLLABLES: tuple[str, ...] = (
    "ka",
    "ro",
    "vi",
    "len",
    "tas",
    "mor",
    "da",
    "zel",
    "pi",
    "nu",
    "ser",
    "ko",
    "ya",
)
_SYLLABLES += ("bel", "tu", "mi", "rak", "son", "ve", "lo", "dan", "gi", "har", "fe", "nis")
_CONFUSABLE = "0O1lI4A5S8B2Z"
_POMS_TR: tuple[str, ...] = (
    "Ön boy",
    "Göğüs genişliği",
    "Bel genişliği",
    "Etek genişliği",
    "Kol boyu",
    "Omuz",
)
_POMS_TR += ("Yaka açıklığı", "Kapüşon yüksekliği", "Cep genişliği", "Manşet yüksekliği")
_POMS_TR += ("Arka boy", "Kol ağzı", "Kalça genişliği", "İç paça", "Dış paça", "Ağ yüksekliği")
_POMS_EN: tuple[str, ...] = (
    "Front length",
    "Chest width",
    "Waist width",
    "Hem width",
    "Sleeve length",
)
_POMS_EN += ("Across shoulder", "Neck opening", "Hood height", "Pocket width", "Cuff height")
_POMS_EN += ("Back length", "Sleeve opening", "Hip width", "Inseam", "Outseam", "Rise")
_MATERIALS: tuple[str, ...] = (
    "Örme kumaş",
    "Ribana",
    "Fermuar",
    "Düğme",
    "İplik",
    "Etiket",
    "Kordon",
)
_MATERIALS += ("Jersey knit", "Rib trim", "Zipper", "Button", "Thread", "Label", "Drawcord")
_UNITS = ("m", "ad.", "kg", "yd", "pcs")
_COLORS: tuple[str, ...] = (
    "Gece",
    "Kum",
    "Kiremit",
    "Bulut",
    "Zeytin",
    "Mürdüm",
    "Slate",
    "Ember",
    "Moss",
)
_COLORS += ("Fjord", "Ochre", "Lilac", "Kömür", "Fildişi")
_STATUSES = ("Onaylandı", "Beklemede", "Düzeltme istendi", "Approved", "On hold", "Revise")
_SENTENCES_TR = (
    "{pom} {value} olmalı.",
    "{pom} numunede {value} ölçüldü, lütfen düzeltin.",
    "{pom} için tolerans {value} korunmalı.",
)
_SENTENCES_EN = (
    "{pom} should be {value}.",
    "{pom} is measuring {value} on the sample, please correct.",
    "Keep {pom} tolerance at {value}.",
)


@dataclass(frozen=True)
class Style:
    """Belgenin görünüşü; içerik değil."""

    font: str
    size: float
    landscape: bool
    ruling: str
    """"grid", "rows" ya da "zebra"."""
    fraction: str
    """"plain" (3/8), "stacked" (küçük rakamlarla çizilir) ya da "glyph" (⅜)."""
    minus: str
    decimal: str
    language: str
    """"tr", "en" ya da "mixed"."""


@dataclass(frozen=True)
class Table:
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    """Tek hücreli satır bölüm etiketidir ve bütün genişliği kaplar."""
    key_column: int = 0
    wide_column: int | None = None
    """Uzun metinli sütun: satır kaydırılır."""
    note: str = ""


@dataclass(frozen=True)
class Page:
    page_type: str
    title: str
    pairs: tuple[tuple[str, str], ...] = ()
    form_columns: int = 2
    table: Table | None = None
    lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class Document:
    doc_id: str
    banner: tuple[str, ...]
    style: Style
    pages: tuple[Page, ...] = field(default=())


def _word(rng: Random, parts: int) -> str:
    return "".join(rng.choice(_SYLLABLES) for _ in range(parts)).capitalize()


def _code(rng: Random) -> str:
    letters = "".join(rng.choice("ABCDEFGHKLMNPRSTVZ" + _CONFUSABLE[1::2]) for _ in range(2))
    digits = "".join(rng.choice("0123456789" + _CONFUSABLE[::2]) for _ in range(rng.randint(3, 5)))
    return rng.choice(
        (f"{letters}{digits}", f"{letters}-{digits}", f"{letters}{digits[:3]}-{letters[0]}")
    )


def _date(rng: Random, first: int, last: int) -> str:
    return f"{rng.randint(1, 28):02d}.{rng.randint(1, 12):02d}.{rng.randint(first, last)}"


def _person(rng: Random) -> str:
    return f"{_word(rng, 2)} {_word(rng, 3)}"


def _text(rng: Random, style: Style, tr: str, en: str) -> str:
    language = style.language if style.language != "mixed" else rng.choice(("tr", "en"))
    return tr if language == "tr" else en


def _fraction(eighths: int, style: Style) -> str:
    """Sekizde birlik değerin yazımı: "27 3/8", "-1/2", "0"."""
    sign = style.minus if eighths < 0 else ""
    whole, rest = divmod(abs(eighths), 8)
    if rest == 0:
        return f"{sign}{whole}"
    top, bottom = rest, 8
    while top % 2 == 0:
        top, bottom = top // 2, bottom // 2
    fraction = f"{top}/{bottom}"
    if style.fraction == "glyph":
        fraction = {
            "1/2": "½",
            "1/4": "¼",
            "3/4": "¾",
            "1/8": "⅛",
            "3/8": "⅜",
            "5/8": "⅝",
            "7/8": "⅞",
        }[fraction]
        return f"{sign}{whole or ''}{fraction}"
    return f"{sign}{whole} {fraction}" if whole else f"{sign}{fraction}"


def _decimal(value: float, places: int, style: Style) -> str:
    text = f"{value:.{places}f}".replace("-", style.minus)
    return text.replace(".", style.decimal)


def _measure(rng: Random, style: Style, inch: bool, units: int | None = None) -> str:
    """İnçte sekizde bir, santimetrede milimetre birimiyle verilen değerin yazımı."""
    if inch:
        return _fraction(units if units is not None else rng.randint(40, 280), style)
    return _decimal((units if units is not None else rng.randint(150, 1100)) / 10, 1, style)


def _pom_rows(rng: Random, style: Style, count: int) -> list[tuple[str, str]]:
    names = rng.sample(_POMS_TR if style.language == "tr" else _POMS_EN, k=min(count, 16))
    return [(_code(rng), name) for name in names]


def _cover(rng: Random, style: Style, banner: tuple[str, ...]) -> Page:
    labels = [
        (_text(rng, style, "Model no", "Style #"), banner[2]),
        (_text(rng, style, "Model adı", "Style name"), banner[3]),
        (
            _text(rng, style, "Sezon", "Season"),
            f"{rng.choice(('SS', 'FW', 'İY', 'SK'))}{rng.randint(24, 29)}",
        ),
        (_text(rng, style, "Ana kumaş", "Main material"), _code(rng)),
        (
            _text(rng, style, "Kumaş açıklaması", "Material description"),
            f"{_word(rng, 2)} - {rng.choice(_MATERIALS)}",
        ),
        (_text(rng, style, "Numune durumu", "Sample status"), rng.choice(_STATUSES)),
        (_text(rng, style, "Hazırlayan", "Created by"), _person(rng)),
        (_text(rng, style, "Değiştiren", "Modified by"), _person(rng)),
        (
            _text(rng, style, "Beden aralığı", "Size range"),
            f"{rng.choice(SIZE_SETS)[0]}-{rng.choice(('4XL', '5XL', '48', '14'))}",
        ),
        (
            _text(rng, style, "Kalıp", "Fit type"),
            rng.choice(("Regular", "Slim", "Oversize", "Rahat")),
        ),
        (
            _text(rng, style, "Bileşim", "Composition"),
            f"%{rng.randint(50, 95)} {rng.choice(('Pamuk', 'Cotton'))}",
        ),
        (
            _text(rng, style, "Tedarikçi", "Supplier"),
            f"{_word(rng, 3)} {rng.choice(('Tekstil', 'Ltd.', 'A.Ş.', 'Mills'))}",
        ),
        (_text(rng, style, "Tedarikçi turu", "Supplier round"), ""),
        (_text(rng, style, "Bölge", "Region"), rng.choice(("EU", "US", "TR", "UK"))),
    ]
    rng.shuffle(labels)
    pairs = tuple(labels[: rng.randint(10, len(labels))])
    return Page(
        "kapak", _text(rng, style, "Kapak bilgileri", "Cover sheet"), pairs, rng.choice((2, 3))
    )


def _comments(rng: Random, style: Style) -> Page:
    lines: list[str] = []
    for _entry in range(rng.randint(2, 3)):
        lines.append(f"{_person(rng)} | {_date(rng, 24, 27)}")
        for number in range(1, rng.randint(3, 6)):
            pom = rng.choice(_POMS_TR + _POMS_EN)
            sentences = _SENTENCES_TR if style.language == "tr" else _SENTENCES_EN
            inch = rng.random() < 0.6
            value = _measure(rng, style, inch) + (rng.choice(('"', "")) if inch else " cm")
            lines.append(f"{number}. " + rng.choice(sentences).format(pom=pom, value=value))
    return Page("yorum", _text(rng, style, "Yorumlar", "Comments"), lines=tuple(lines))


def _evaluation(rng: Random, style: Style, inch: bool) -> Page:
    columns = (
        _text(rng, style, "Kod", "Dim"),
        _text(rng, style, "Açıklama", "Description"),
        "Tol (-)",
        "Tol (+)",
        _text(rng, style, "Hedef", "Target"),
        _text(rng, style, "Numune", "Sample"),
        _text(rng, style, "Düzeltilmiş", "Revised"),
    )
    rows = []
    for code, name in _pom_rows(rng, style, rng.randint(6, 14)):
        target = rng.randint(40, 280) if inch else rng.randint(150, 1100)
        tolerance = rng.choice((2, 3, 4)) if inch else rng.choice((5, 10, 15))
        sample = target + rng.choice((-3, -1, 0, 1, 2))
        rows.append(
            (
                code,
                name,
                _measure(rng, style, inch, -tolerance),
                _measure(rng, style, inch, tolerance),
                _measure(rng, style, inch, target),
                _measure(rng, style, inch, sample),
                _measure(rng, style, inch, target) if rng.random() < 0.4 else "",
            )
        )
    return Page(
        "degerlendirme",
        _text(rng, style, "Numune değerlendirme", "Evaluation by sample"),
        table=Table(columns, tuple(rows), wide_column=1),
    )


def _bom(rng: Random, style: Style) -> Page:
    colors = tuple(
        f"{rng.randint(1, 9)}{rng.randint(10, 99)} {rng.choice(_COLORS)}"
        for _ in range(rng.randint(2, 4))
    )
    columns = (
        _text(rng, style, "Malzeme", "Material"),
        _text(rng, style, "Açıklama", "Description"),
        _text(rng, style, "Miktar", "Qty"),
        _text(rng, style, "Birim", "UoM"),
        *colors,
    )
    rows = []
    for _row in range(rng.randint(5, 10)):
        words = [
            rng.choice(_MATERIALS),
            _word(rng, 2),
            f"{rng.randint(80, 400)} gsm",
            _word(rng, 3),
        ]
        words += [
            rng.choice(_MATERIALS),
            f"%{rng.randint(1, 99)} {_word(rng, 2)}",
            _code(rng),
        ]
        rows.append(
            (
                _code(rng),
                " - ".join(words[: rng.randint(2, len(words))]),
                _decimal(rng.uniform(0.01, 3), rng.choice((2, 4)), style),
                rng.choice(_UNITS),
                *(rng.choice(_COLORS) for _ in colors),
            )
        )
    return Page(
        "bom",
        _text(rng, style, "Malzeme listesi", "Bill of materials"),
        table=Table(columns, tuple(rows), wide_column=1),
    )


def _chart(rng: Random, style: Style, inch: bool, increment: bool) -> Page:
    sizes: tuple[str, ...] = rng.choice(SIZE_SETS)
    sizes = sizes[: rng.randint(5, len(sizes))]
    base = rng.randrange(len(sizes))
    columns = (
        _text(rng, style, "Kod", "Dim"),
        _text(rng, style, "Açıklama", "Description"),
        "Tol (-)",
        "Tol (+)",
        *sizes,
    )
    rows: list[tuple[str, ...]] = []
    poms = _pom_rows(rng, style, rng.randint(7, 16))
    label_at = rng.randint(2, len(poms) - 2) if rng.random() < 0.6 else None
    for index, (code, name) in enumerate(poms):
        if index == label_at:
            rows.append((_text(rng, style, "Uzun boy", "Tall"),))
        step = rng.choice((2, 4, 6, 8)) if inch else rng.choice((5, 10, 20))
        middle = rng.randint(60, 280) if inch else rng.randint(200, 1100)
        tolerance = rng.choice((2, 3, 4)) if inch else rng.choice((5, 10))
        if increment:
            values = [0 if i == base else step * (1 if i > base else -1) for i in range(len(sizes))]
        else:
            values = [middle + step * (i - base) for i in range(len(sizes))]
        rows.append(
            (
                code,
                name,
                _measure(rng, style, inch, -tolerance),
                _measure(rng, style, inch, tolerance),
                *(_measure(rng, style, inch, v) for v in values),
            )
        )
    unit = (
        _text(rng, style, "Birim: inç kesir", "Units: Fractions of inches")
        if inch
        else _text(rng, style, "Birim: cm", "Units: cm")
    )
    display = (
        _text(rng, style, "Gösterim: Fark", "Grade Rule Display: Increment")
        if increment
        else _text(rng, style, "Gösterim: Mutlak", "Grade Rule Display: Absolute")
    )
    page_type = "fark" if increment else "olcu"
    title = _text(rng, style, "Ölçü tablosu", "Measurement chart")
    pairs = (
        (_text(rng, style, "Taban beden", "Base size"), sizes[base]),
        (
            _text(rng, style, "Tolerans", "Tolerance"),
            f"{_word(rng, 2).upper()} {rng.randint(1, 3)}",
        ),
        (
            _text(rng, style, "Büyütme kuralı", "Grade rule"),
            f"{_word(rng, 2)} - {rng.randint(2022, 2027)}",
        ),
    )
    return Page(
        page_type,
        title,
        pairs,
        3,
        Table(columns, tuple(rows), wide_column=1, note=f"{unit} · {display}"),
    )


def build_document(rng: Random, number: int, fonts: tuple[str, ...]) -> Document:
    # Biçimler belgeler arasında sırayla dağılır: her kesir yazımı ve yazı tipi sette yer alır,
    # her dört belgeden biri santimetre (ondalık) kullanır. Tek karakter kesir (⅜) yalnız DejaVu'da
    # çizilebilir.
    fraction = ("glyph", "stacked", "plain")[(number - 1) % 3]
    font = "DejaVu" if fraction == "glyph" else fonts[(number - 1) % len(fonts)]
    inch = number % 4 != 2
    style = Style(
        font=font,
        size=rng.choice((7.0, 7.5, 8.0, 8.5)),
        landscape=rng.random() < 0.6,
        ruling=rng.choice(("grid", "rows", "zebra")),
        fraction=fraction,
        minus=rng.choice(("-", "−")),
        decimal=rng.choice((",", ".")),
        language=rng.choice(("tr", "en", "mixed")),
    )
    banner = (
        f"{_word(rng, 2)} {rng.choice(('Apparel', 'Giyim', 'Wear', 'Moda'))}",
        f"{rng.randint(1, 28):02d}.{rng.randint(1, 12):02d}.{rng.randint(2024, 2027)}",
        _code(rng),
        f"{_word(rng, 2)} {rng.choice(('Hoodie', 'Sweatshirt', 'Pantolon', 'Ceket', 'Tişört'))}",
    )
    others = [
        _comments(rng, style),
        _evaluation(rng, style, inch),
        _bom(rng, style),
        _chart(rng, style, inch, increment=False),
        _chart(rng, style, inch, increment=True),
    ]
    rng.shuffle(others)
    pages = (_cover(rng, style, banner), *others)
    return Document(f"syn{number}", banner, style, pages)
