"""OpenRouter istemcisi: yalnız veri saklamayan sağlayıcılar, akış ve sağlayıcı yedeği."""

import json
import logging
import time
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_CONNECT_SECONDS = 10.0
_ERROR_PREVIEW = 200
_FINISH_TRUNCATED = "length"


class ServiceUnavailable(RuntimeError):
    """Cevap servisine ulaşılamadı; yerel modele otomatik düşüş yoktur."""


@dataclass(frozen=True)
class ZdrEntry:
    strict: frozenset[str]
    safety: frozenset[str]


def _provider_slug(endpoint: Mapping[str, Any]) -> str:
    return str(endpoint.get("tag") or endpoint.get("provider_name") or "").split("/")[0]


def parse_zdr_index(endpoints: Iterable[Mapping[str, Any]]) -> dict[str, ZdrEntry]:
    """Saklama alanı açıkça false olmayan ya da bir uç noktası saklayan sağlayıcı ZDR sayılmaz."""
    strict: dict[str, set[str]] = {}
    safety: dict[str, set[str]] = {}
    for endpoint in endpoints:
        model = endpoint.get("model_id")
        if model:
            bucket = strict if endpoint.get("safety_retention") is False else safety
            bucket.setdefault(str(model), set()).add(_provider_slug(endpoint))
    return {
        model: ZdrEntry(
            strict=frozenset(strict.get(model, set()) - safety.get(model, set())),
            safety=frozenset(safety.get(model, set())),
        )
        for model in strict.keys() | safety.keys()
    }


async def fetch_zdr_index(
    http: httpx.AsyncClient, base_url: str, api_key: str
) -> dict[str, ZdrEntry]:
    response = await http.get(
        f"{base_url}/endpoints/zdr", headers={"Authorization": f"Bearer {api_key}"}, timeout=30.0
    )
    response.raise_for_status()
    return parse_zdr_index(response.json().get("data", []))


def select_providers(
    model: str, configured: Sequence[str], index: Mapping[str, ZdrEntry]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Kullanılacak ZDR sağlayıcıları ve dışlanacak saklama yapan sağlayıcılar."""
    entry = index.get(model)
    if entry is None or not entry.strict:
        raise ServiceUnavailable(f"{model}: ZDR uç noktası yok")
    providers = (
        tuple(name for name in configured if name in entry.strict)
        if configured
        else tuple(sorted(entry.strict))
    )
    if not providers:
        raise ServiceUnavailable(f"{model}: yapılandırılan sağlayıcıların hiçbiri ZDR değil")
    return providers, tuple(sorted(entry.safety))


@dataclass(frozen=True)
class AnswerClientOptions:
    model: str
    providers: tuple[str, ...]
    ignored_providers: tuple[str, ...]
    schema: Mapping[str, Any]
    max_tokens: int
    first_token_seconds: float
    runaway_whitespace_limit: int


@dataclass(frozen=True)
class StreamCallbacks:
    on_delta: Callable[[str, float], None] | None = None
    may_retry: Callable[[], bool] | None = None
    on_reset: Callable[[], None] | None = None


@dataclass(frozen=True)
class AttemptRecord:
    provider: str
    error: str
    runaway: bool
    seconds: float


@dataclass(frozen=True)
class StreamResult:
    content: str
    provider: str
    finish: str | None
    first_token_seconds: float | None
    timeline: tuple[tuple[float, int], ...]
    cost_usd: float
    attempts: tuple[AttemptRecord, ...]
    incomplete: bool = False


@dataclass
class _Attempt:
    provider: str
    started: float
    content: str = ""
    error: str = ""
    runaway: bool = False
    finish: str | None = None
    first_token_seconds: float | None = None
    timeline: list[tuple[float, int]] = field(default_factory=list)
    cost_usd: float = 0.0
    whitespace_run: int = 0

    def record(self) -> AttemptRecord:
        return AttemptRecord(
            self.provider, self.error, self.runaway, time.perf_counter() - self.started
        )

    def result(
        self,
        attempts: Sequence[AttemptRecord],
        finish: str | None = None,
        incomplete: bool = False,
    ) -> StreamResult:
        return StreamResult(
            content=self.content,
            provider=self.provider,
            finish=finish if finish is not None else self.finish,
            first_token_seconds=self.first_token_seconds,
            timeline=tuple(self.timeline),
            cost_usd=self.cost_usd,
            attempts=tuple(attempts),
            incomplete=incomplete,
        )


class AnswerClient:
    def __init__(
        self,
        http: httpx.AsyncClient,
        *,
        base_url: str,
        api_key: str,
        options: AnswerClientOptions,
    ) -> None:
        self._http = http
        self._url = f"{base_url}/chat/completions"
        self._headers = {"Authorization": f"Bearer {api_key}"}
        self._options = options

    def _body(self, messages: Sequence[Mapping[str, str]], provider: str) -> dict[str, Any]:
        options = self._options
        constraints: dict[str, Any] = {
            "zdr": True,
            "data_collection": "deny",
            "order": [provider],
            "allow_fallbacks": False,
        }
        if options.ignored_providers:
            constraints["ignore"] = list(options.ignored_providers)
        return {
            "model": options.model,
            "messages": list(messages),
            "temperature": 0,
            "max_tokens": options.max_tokens,
            "stream": True,
            "usage": {"include": True},
            "reasoning": {"enabled": False},
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "cevap", "strict": False, "schema": options.schema},
            },
            "provider": constraints,
        }

    def _append_piece(
        self, attempt: _Attempt, piece: str, seconds: float, callbacks: StreamCallbacks | None
    ) -> None:
        if not attempt.content:
            attempt.first_token_seconds = seconds
        attempt.content += piece
        attempt.timeline.append((round(seconds, 3), len(attempt.content)))
        if callbacks is not None and callbacks.on_delta is not None:
            try:
                callbacks.on_delta(attempt.content, seconds)
            except Exception:
                logger.exception("Akış geri çağrısı başarısız oldu")
        for character in piece:
            attempt.whitespace_run = attempt.whitespace_run + 1 if character.isspace() else 0
        attempt.runaway = attempt.whitespace_run > self._options.runaway_whitespace_limit

    def _apply_event(
        self, event: Mapping[str, Any], attempt: _Attempt, callbacks: StreamCallbacks | None
    ) -> bool:
        """Akışın durması gerekiyorsa True döndürür."""
        if event.get("error"):
            attempt.error = f"akış hatası: {json.dumps(event['error'])[:_ERROR_PREVIEW]}"
            return True
        if event.get("usage"):
            attempt.cost_usd = float(event["usage"].get("cost") or 0.0)
        choice = (event.get("choices") or [{}])[0]
        piece = (choice.get("delta") or {}).get("content") or ""
        seconds = time.perf_counter() - attempt.started
        if not attempt.content and not piece and seconds > self._options.first_token_seconds:
            attempt.error = "ilk token süresinde gelmedi"
            return True
        if piece:
            self._append_piece(attempt, piece, seconds, callbacks)
        if choice.get("finish_reason"):
            attempt.finish = choice["finish_reason"]
        return attempt.runaway

    async def _consume(
        self, response: httpx.Response, attempt: _Attempt, callbacks: StreamCallbacks | None
    ) -> None:
        async for line in response.aiter_lines():
            if not line.startswith("data: ") or line == "data: [DONE]":
                continue
            if self._apply_event(json.loads(line[len("data: ") :]), attempt, callbacks):
                return

    async def _try_provider(
        self,
        messages: Sequence[Mapping[str, str]],
        provider: str,
        callbacks: StreamCallbacks | None,
    ) -> _Attempt:
        attempt = _Attempt(provider=provider, started=time.perf_counter())
        timeout = httpx.Timeout(
            connect=_CONNECT_SECONDS,
            read=self._options.first_token_seconds,
            write=_CONNECT_SECONDS,
            pool=_CONNECT_SECONDS,
        )
        try:
            async with self._http.stream(
                "POST",
                self._url,
                json=self._body(messages, provider),
                headers=self._headers,
                timeout=timeout,
            ) as response:
                if response.status_code != httpx.codes.OK:
                    body = (await response.aread()).decode(errors="replace")
                    attempt.error = f"{response.status_code}: {body[:_ERROR_PREVIEW]}"
                    return attempt
                await self._consume(response, attempt, callbacks)
        except (httpx.HTTPError, json.JSONDecodeError) as error:
            attempt.error = repr(error)[:_ERROR_PREVIEW]
        return attempt

    async def stream(
        self, messages: Sequence[Mapping[str, str]], callbacks: StreamCallbacks | None = None
    ) -> StreamResult:
        """Sağlayıcıları sırayla, her birini en fazla bir kez dener."""
        records: list[AttemptRecord] = []
        for provider in self._options.providers:
            attempt = await self._try_provider(messages, provider, callbacks)
            records.append(attempt.record())
            if not attempt.error and not attempt.runaway:
                return attempt.result(records)
            if attempt.content and callbacks is not None:
                if callbacks.may_retry is not None and not callbacks.may_retry():
                    return attempt.result(records, finish=_FINISH_TRUNCATED, incomplete=True)
                if callbacks.on_reset is not None:
                    callbacks.on_reset()
        if not attempt.error:
            return attempt.result(records, finish=_FINISH_TRUNCATED)
        details = "; ".join(f"{r.provider}: {r.error or 'kaçak'}" for r in records)
        raise ServiceUnavailable(details)
