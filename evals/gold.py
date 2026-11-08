"""Doğru cevapları baştan bilinen test setinin veri modeli."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Carrier(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    SCAN = "scan"
    PHOTO = "photo"
    SCREENSHOT = "screenshot"
    SQL_TEXT = "sql_text"


class Mess(StrEnum):
    MERGED_CELLS = "merged_cells"
    MULTI_SHEET = "multi_sheet"
    NEAR_DUPLICATE_VERSION = "near_duplicate_version"
    INCONSISTENT_HEADERS = "inconsistent_headers"
    MIXED_LANGUAGE = "mixed_language"
    SKEWED = "skewed"
    BLURRED = "blurred"


class Split(StrEnum):
    DEVELOPMENT = "development"
    HOLDOUT = "holdout"


class QuestionKind(StrEnum):
    DIRECT = "direct"
    TABLE_LOOKUP = "table_lookup"
    CLARIFY = "clarify"
    NOT_IN_DOCUMENT = "not_in_document"
    IN_IMAGE = "in_image"
    CONFIRM_WRONG = "confirm_wrong"
    FOLLOW_UP = "follow_up"


class Outcome(StrEnum):
    ANSWERED = "answered"
    CLARIFY = "clarify"
    NOT_FOUND = "not_found"
    FAILED = "failed"


class Badge(StrEnum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    FAILED = "failed"
    NONE = "none"


class GoldModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class GoldSource(GoldModel):
    """Word ve düz metinde yalnız belge bilinir; sayfa ya da satır üretim anında kesinleşmez."""

    doc_id: str
    page: int | None = None
    sheet: str | None = None
    row: int | None = None


class GoldDocument(GoldModel):
    doc_id: str
    filename: str
    domain: str
    split: Split = Split.DEVELOPMENT
    carrier: Carrier
    mess: tuple[Mess, ...] = ()


class GoldQuestion(GoldModel):
    question_id: str
    text: str
    kind: QuestionKind
    domain: str
    split: Split = Split.DEVELOPMENT
    outcome: Outcome
    expected_values: tuple[str, ...] = ()
    evidence: str = ""
    sources: tuple[GoldSource, ...] = ()
    differing_values: tuple[str, ...] = ()
    absent_term: str | None = None
    conversation_id: str | None = None
    turn: int | None = None


class GoldSet(GoldModel):
    seed: int
    documents: tuple[GoldDocument, ...]
    questions: tuple[GoldQuestion, ...]
    document_texts: dict[str, str]
