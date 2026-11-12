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
    InputFormat.PDF: 1,
    InputFormat.OFFICE: 1,
    InputFormat.IMAGE: 1,
    InputFormat.SPREADSHEET: 2,
    InputFormat.LEGACY_SPREADSHEET: 2,
    InputFormat.SQL: 2,
    InputFormat.TEXT: 2,
    InputFormat.MARKDOWN: 2,
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


def is_outdated(report: Mapping[str, object], filename: str) -> bool:
    """Belge, biçiminin bugünkü kuralından eski bir kuralla işlendiyse True (kayıtlı rapordan)."""
    recorded = report.get("input_format")
    input_format = InputFormat(recorded) if isinstance(recorded, str) else format_of_name(filename)
    if input_format is None:
        return False
    version = report.get("rules_version", UNRECORDED_RULES)
    return isinstance(version, int) and version < RULES_VERSIONS[input_format]
