"""Yüklenen dosyanın gerçek biçimini ve biçimin parçalama kuralı sürümünü belirler.

Ağır paket yüklemez: API, belge işleme paketleri olmadan da bu modülü kullanır.
"""

from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path


class InputFormat(StrEnum):
    PDF = "pdf"
    OFFICE = "office"
    SPREADSHEET = "spreadsheet"
    LEGACY_SPREADSHEET = "legacy_spreadsheet"
    IMAGE = "image"
    SQL = "sql"
    TEXT = "text"
    MARKDOWN = "markdown"


class UnsupportedFormat(ValueError):
    """Dosya desteklenmiyor ya da uzantısıyla içeriği uyuşmuyor."""


_ZIP = (b"PK\x03\x04",)
_OLE = (b"\xd0\xcf\x11\xe0",)
_TYPES: dict[str, tuple[InputFormat, tuple[bytes, ...]]] = {
    ".pdf": (InputFormat.PDF, (b"%PDF",)),
    ".docx": (InputFormat.OFFICE, _ZIP),
    ".pptx": (InputFormat.OFFICE, _ZIP),
    ".odt": (InputFormat.OFFICE, _ZIP),
    ".doc": (InputFormat.OFFICE, _OLE),
    ".ppt": (InputFormat.OFFICE, _OLE),
    ".rtf": (InputFormat.OFFICE, (b"{\\rtf",)),
    ".xlsx": (InputFormat.SPREADSHEET, _ZIP),
    ".xls": (InputFormat.LEGACY_SPREADSHEET, _OLE),
    ".jpg": (InputFormat.IMAGE, (b"\xff\xd8\xff",)),
    ".jpeg": (InputFormat.IMAGE, (b"\xff\xd8\xff",)),
    ".png": (InputFormat.IMAGE, (b"\x89PNG",)),
    ".tif": (InputFormat.IMAGE, (b"II*\x00", b"MM\x00*")),
    ".tiff": (InputFormat.IMAGE, (b"II*\x00", b"MM\x00*")),
    ".sql": (InputFormat.SQL, ()),
    ".txt": (InputFormat.TEXT, ()),
    ".md": (InputFormat.MARKDOWN, ()),
}
_MAGIC_LENGTH = 8

RULES_VERSIONS: dict[InputFormat, int] = {
    # 2: tek büyük harf OCR çöpü sayılmaz, düşen sayfa için uyarı (Office dahil).
    # 3 (PDF, görsel, Office): yeniden işlemede de OCR tur+eng (kayıtlı dile bağlı değil).
    # 4 (PDF, görsel, Office): OCR'lı tablo hücreleri iki okumayla doğrulanır (kesirler okunur).
    # 5 (PDF, görsel, Office): tabloyu kaplayan etiket ve not satırları satırların bölümüne girer.
    # 6 (PDF, görsel, Office): taranmış çizgili tablolar çizgilerinden, hücre hücre okunur.
    # 7 (PDF, görsel, Office): OCR'da eğiklik düzeltme yok; fark filtresi tablo notuna bakar.
    # 8 (PDF, görsel, Office): metin katmanı olmayan sayfalar sayfa okuyucusuyla okunur (0010).
    # 9 (PDF, görsel, Office): OCR'lı sayfalardaki tablolar hücre hücre yeniden okunmaz.
    # 10 (PDF, görsel, Office): sayfa okuyucusunda form gibi tablolar başlıksız, okunduğu gibi.
    # 11 (PDF, görsel, Office): okunduğu gibi yazılan satırda boş hücre yerini korur.
    # 12 (PDF, görsel, Office): boş hücre işareti "(boş)".
    # 13 (PDF, görsel, Office): başlığı ile satırları aynı sayıda hücre taşımayan tablo başlıksız.
    # 14 (PDF, Office): docling tablosunda da aynı iki koruma (ortak yardımcı): tahmin edilen
    #    başlık her veri satırıyla aynı sayıda dolu hücre taşımalı; başlıksız satırda boş sütun
    #    "(boş)". Excel 4, Markdown 3: hiç başlığı olmayan satırda boş hücre "(boş)".
    # 15 (PDF, Office): eski OCR yolu ve gömülü görsellerin ikinci okuması okuyucu kuralıyla
    #    (sayım; harf-rakam eşdeğerliği yok, rakamsız kod denetlenir, virgül ≠ nokta).
    # 16 (PDF, Office; görsel 14): başlıkta ve satır bağlamında belirsiz okunan değer parçanın
    #    belirsiz listesine girer (yalnız OCR'lı sayfalar).
    # 17 (PDF, Office): gömülü görselin öğeleri sayfadaki yerine girer (sona değil).
    # 18 (PDF, Office): docling'in sayfa üst bilgisi de gezilir; kod taşıyan üst bilgi bölüm olur.
    # 19 (PDF, Office; görsel 15): okuyucu yolunda değer taşıyan başlık metin olarak da kalır.
    # 20 (PDF, Office): eski OCR yolundan (gömülü görsel, ocrmypdf) gelen parçalar işaretlenir;
    #    değerleri doğrulanmış gösterilmez (karar 0022). Okuyucu yolunun parçaları değişmedi.
    # 21 (PDF, Office): gömülü görselin iki Tesseract kipi art arda eklenmez; her parça kiplerin
    #    en çok okuduğu sayıyla karşılaştırılır (iki kipin okuduğu değer çift sayılıyordu).
    # 22 (PDF, Office): U+2010/U+2011 tireli kod taşıyan sayfa üst bilgisi de bölüm olur
    #    (karşılaştırma bu tireleri kısa tire okur; docling_parser.page_header_identifies).
    # 23 (PDF, Office; görsel 16): okuyucu yolunda önceki sayfada yapıdan kabul edilen başlık
    #    satırının aynısı başlıktır; içerikten sonra gelen kodsuz ilk başlık kök değildir,
    #    düzeyi bilinmeyen başlıklar kardeştir (bütün yollar; SQL 3, Markdown ve Excel düzeyli).
    InputFormat.PDF: 23,
    InputFormat.OFFICE: 23,
    InputFormat.IMAGE: 16,
    # Excel 5: altında satır olmayan başlık satırı başlık sayılmaz; satırları etiketsiz yazılır.
    # Excel 6: tek sütunlu sayfa başlıksızdır; her hücre ayrı, etiketsiz satır (ürün sahibi kararı).
    InputFormat.SPREADSHEET: 6,
    InputFormat.LEGACY_SPREADSHEET: 6,
    # SQL 3: içerikten sonra gelen kodsuz ilk başlık kök değildir (bölüm yolu ortak kodda).
    InputFormat.SQL: 3,
    InputFormat.TEXT: 2,
    InputFormat.MARKDOWN: 3,
}
"""Biçimin parçalarını üreten kuralların sürümü. Bir biçimin parçalarını ya da konumlarını
değiştiren her değişiklikte o biçimin sürümü artırılır; eski sürümle işlenmiş belge yeniden
işlenene kadar eski parçalarıyla kalır."""
UNRECORDED_RULES = 1
"""Sürüm kaydedilmeden önce işlenen belgeler ilk sürümle işlenmiştir."""


def format_of_name(name: str) -> InputFormat | None:
    """Uzantıya göre biçim; içerik denetlenmez. Desteklenmeyen uzantıda None."""
    known = _TYPES.get(Path(name).suffix.lower())
    return known[0] if known else None


def detect_format(path: Path) -> InputFormat:
    known = _TYPES.get(path.suffix.lower())
    if known is None:
        raise UnsupportedFormat(f"{path.name}: bu dosya türü desteklenmiyor")
    input_format, signatures = known
    if signatures:
        with path.open("rb") as stream:
            start = stream.read(_MAGIC_LENGTH)
        if not start.startswith(signatures):
            raise UnsupportedFormat(f"{path.name}: dosya içeriği uzantısıyla uyuşmuyor")
    return input_format


_CHANGED_PAGE_KINDS = {
    7: ("none", "scanned"),
    8: ("weak", "scanned"),
    9: ("none", "scanned"),
    10: ("none", "scanned"),
    11: ("none", "scanned"),
    12: ("none", "scanned"),
    15: ("none", "weak", "scanned"),
    18: ("none", "scanned"),
    19: ("text", "weak", "scanned"),
    20: ("text",),
    21: ("text",),
    22: ("none", "weak", "scanned", "text"),
}
"""Bu sürümden bir sonrakine geçiş yalnız bu tür sayfası olan belgelerin çıktısını değiştirdi:
7→8 taranmış sayfalar sayfa okuyucusuna gitti ("scanned": OCR katmanlı tarama öyle kaydedilmiş
olabilir); 8→9 eski OCR yolundaki (zayıf ya da taranmış metin katmanlı) sayfaların tabloları;
9→10, 10→11 ve 11→12 sayfa okuyucusundan geçen sayfalardaki form tabloları; 12→13 aynı
sayfalarda başlığı ile satırları aynı sayıda hücre taşımayan tablolar; 19→20 eski OCR yolunun
parçaları (metinli sayfadaki gömülü görsel, zayıf ya da taranmış metin katmanlı sayfa); 20→21
metinli sayfadaki gömülü görsellerin belirsiz değerleri; 21→22 metinli sayfaların üst bilgisi;
22→23 bütün sayfa türleri (bölüm yolu ortak kodda)."""
_PAGE_FORMATS = (InputFormat.PDF, InputFormat.OFFICE, InputFormat.IMAGE)


def is_outdated(report: Mapping[str, object], filename: str) -> bool:
    """Belge, biçiminin bugünkü kuralından eski bir kuralla işlendiyse True (kayıtlı rapordan)."""
    recorded = report.get("input_format")
    input_format = InputFormat(recorded) if isinstance(recorded, str) else format_of_name(filename)
    if input_format is None:
        return False
    version = report.get("rules_version", UNRECORDED_RULES)
    if not isinstance(version, int) or version >= RULES_VERSIONS[input_format]:
        return False
    steps = range(version, RULES_VERSIONS[input_format])
    if input_format not in _PAGE_FORMATS or any(step not in _CHANGED_PAGE_KINDS for step in steps):
        return True
    kinds = report.get("page_kinds")
    changed = {kind for step in steps for kind in _CHANGED_PAGE_KINDS[step]}
    return isinstance(kinds, Mapping) and any(kinds.get(kind) for kind in changed)
