"""Sohbetin sonraki tura taşıdığı bağlam."""

from pydantic import Field

from visual_agent.domain.document import FrozenModel

MAX_QUESTION_CHARS = 2000
_MAX_CONTEXT_DOCUMENTS = 20


class ConversationContext(FrozenModel):
    """Bağlam yalnız sorudur; önceki cevabın değerleri bilerek taşınmaz."""

    question: str = Field(min_length=1, max_length=MAX_QUESTION_CHARS)
    doc_ids: tuple[str, ...] = Field(default=(), max_length=_MAX_CONTEXT_DOCUMENTS)
    titles: tuple[str, ...] = Field(default=(), max_length=_MAX_CONTEXT_DOCUMENTS)
