"""Soru hattının girdisi ve dış bağımlılıkları."""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Protocol, Self

from visual_agent.ask.streaming import EventSink
from visual_agent.catalog.identifiers import IdentifierIndex
from visual_agent.catalog.memory import DocumentCatalog
from visual_agent.domain.conversation import ConversationContext
from visual_agent.domain.result import Hit
from visual_agent.generation.intent import IntentClassifier
from visual_agent.generation.openrouter import StreamCallbacks, StreamResult
from visual_agent.generation.rewrite import Rewriter
from visual_agent.generation.translate import Translator

DEFAULT_TOP_K = 8
DEFAULT_TRANSLATION_LIMIT_SECONDS = 1.2
DEFAULT_REWRITE_LIMIT_SECONDS = 4.0
DEFAULT_INTENT_LIMIT_SECONDS = 1.5


class Retriever(Protocol):
    async def search(
        self,
        query: str,
        bm25_query: str,
        doc_ids: Sequence[str] | None,
        top_k: int,
        access: Sequence[str] | None = None,
    ) -> list[Hit]: ...


class AnswerStreamer(Protocol):
    async def stream(
        self, messages: Sequence[dict[str, str]], callbacks: StreamCallbacks | None = None
    ) -> StreamResult: ...


@dataclass(frozen=True)
class AskRequest:
    question: str
    doc_ids: tuple[str, ...] | None = None
    access: tuple[str, ...] | None = None
    on_event: EventSink | None = None
    context: ConversationContext | None = None


@dataclass(frozen=True)
class AskDeps:
    catalog: DocumentCatalog
    identifiers: IdentifierIndex
    retriever: Retriever
    answer_client: AnswerStreamer
    system_prompt: str
    translator: Translator | None = None
    top_k: int = DEFAULT_TOP_K
    translation_limit_seconds: float = DEFAULT_TRANSLATION_LIMIT_SECONDS
    rewriter: Rewriter | None = None
    rewrite_limit_seconds: float = DEFAULT_REWRITE_LIMIT_SECONDS
    intent_classifier: IntentClassifier | None = None
    intent_limit_seconds: float = DEFAULT_INTENT_LIMIT_SECONDS

    def with_translation_limit(self, seconds: float) -> Self:
        return replace(self, translation_limit_seconds=seconds)
