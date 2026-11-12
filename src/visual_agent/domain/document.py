"""Belgelerin biçimden bağımsız temsili."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class ChunkKind(StrEnum):
    TEXT = "text"
    TABLE_ROW = "table_row"
    CODE = "code"
    FIGURE = "figure"


class Box(FrozenModel):
    """Sayfa üzerinde sol-üst orijinli konum (point)."""

    page: int
    left: float
    top: float
    right: float
    bottom: float
    page_width: float
    page_height: float


class SourceLocation(FrozenModel):
    """PDF'te sayfa ve kutular, Excel'de sayfa adı ve satır; sayfasız metinde bölüm yolu."""

    page: int | None = None
    boxes: tuple[Box, ...] = ()
    sheet: str | None = None
    row: int | None = None
    section: str | None = None


class DocumentMeta(FrozenModel):
    doc_id: str
    title: str
    language: str = "tr"
    access: tuple[str, ...] = ("all",)


class Chunk(FrozenModel):
    chunk_id: str
    doc_id: str
    kind: ChunkKind
    text: str
    title: str
    section: str = ""
    location: SourceLocation
    generated: str = ""
    """Kullanılmıyor, hep boş; kayıtlı parçalar ve indeks değişmesin diye duruyor."""
    ocr_uncertain: tuple[str, ...] = ()
    from_ocr: bool = False

    @property
    def embed_text(self) -> str:
        heading = f"{self.title} | {self.section}" if self.section else self.title
        return f"{heading}\n{self.text}"
