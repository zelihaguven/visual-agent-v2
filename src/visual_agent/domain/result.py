"""Bir sorunun olası sonuçları: her çıkış kendi tipindedir."""

from visual_agent.domain.answer import VerificationStatus
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
    from_figure: bool = False
    code: str | None = None
    problems: tuple[str, ...] = ()


class Answered(FrozenModel):
    status: VerificationStatus
    items: tuple[AnsweredItem, ...]
    has_conflict: bool = False
    problems: tuple[str, ...] = ()


class ClarifyChoice(FrozenModel):
    doc_id: str
    label: str


class Clarify(FrozenModel):
    question: str
    options: tuple[ClarifyChoice, ...] = ()


class NotFound(FrozenModel):
    reason: str = ""
    suggested_doc_ids: tuple[str, ...] = ()


class Failed(FrozenModel):
    reason: str
    citations: tuple[Citation, ...] = ()


AskResult = Answered | Clarify | NotFound | Failed


class AskOutcome(FrozenModel):
    result: AskResult
    hits: tuple[Hit, ...] = ()
    timings: dict[str, float]
    cost_usd: float = 0.0
    provider: str | None = None
