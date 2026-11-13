"""Bir sorunun olası sonuçları: her çıkış kendi tipindedir."""

from visual_agent.domain.answer import VerificationStatus
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.document import Chunk, FrozenModel, SourceLocation


class Hit(FrozenModel):
    chunk: Chunk
    score: float


class Citation(FrozenModel):
    chunk_id: str
    doc_id: str
    title: str
    location: SourceLocation


class AnsweredItem(FrozenModel):
    text: str
    citations: tuple[Citation, ...]
    verified: bool
    from_ocr: bool = False
    code: str | None = None
    problems: tuple[str, ...] = ()
    source_quote: str | None = None
    """Cümle yalnız birim yüzünden gizlendiyse yerine gösterilen kaynak alıntısı."""


class Answered(FrozenModel):
    status: VerificationStatus
    items: tuple[AnsweredItem, ...]
    has_conflict: bool = False
    problems: tuple[str, ...] = ()


class ClarifyChoice(FrozenModel):
    """Kullanıcının tek tıkla o belgede yeniden sorabileceği belge."""

    doc_id: str
    label: str


class Clarify(FrozenModel):
    question: str
    options: tuple[ClarifyChoice, ...] = ()


class NotFound(FrozenModel):
    reason: str = ""
    suggestions: tuple[ClarifyChoice, ...] = ()
    """Sorulan kodu içeren, kapsam dışındaki belgeler; arayüz bunları düğme olarak gösterir."""


class Failed(FrozenModel):
    reason: str
    citations: tuple[Citation, ...] = ()


class InventoryDocument(FrozenModel):
    doc_id: str
    title: str
    codes: tuple[str, ...] = ()
    code_count: int = 0


class Inventory(FrozenModel):
    """Sayılar kayıtlardan gelir; liste uzunsa kesilir, sayı yine doğrudur."""

    documents: tuple[InventoryDocument, ...]
    document_count: int
    code_count: int


class SmallTalk(FrozenModel):
    """Selamlaşmaya verilen sabit cevap; model metni içermez."""

    text: str


AskResult = Answered | Clarify | NotFound | Failed | Inventory | SmallTalk


class AskOutcome(FrozenModel):
    result: AskResult
    hits: tuple[Hit, ...] = ()
    timings: dict[str, float]
    cost_usd: float = 0.0
    provider: str | None = None
    first_verified_seconds: float | None = None
    provider_attempts: int = 0
    provider_seconds: float = 0.0
    question: str = ""
    context: ConversationContext | None = None
    scope_inherited: bool = False
