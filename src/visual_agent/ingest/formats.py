"""Yüklenen dosyanın gerçek biçimini belirler."""

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
    ".md": (InputFormat.TEXT, ()),
}
_MAGIC_LENGTH = 8


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
