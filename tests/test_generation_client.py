import asyncio
import json
from collections.abc import AsyncIterator, Callable
from typing import Any

import httpx
import pytest

from visual_agent.generation.openrouter import (
    AnswerClient,
    AnswerClientOptions,
    ServiceUnavailable,
    StreamCallbacks,
    ZdrEntry,
    fetch_zdr_index,
    parse_zdr_index,
    select_providers,
)

MODEL = "vendor/model"
ZDR_ENDPOINTS = [
    {"model_id": MODEL, "tag": "alpha/global", "safety_retention": False},
    {"model_id": MODEL, "tag": "beta", "safety_retention": False},
    {"model_id": MODEL, "tag": "risky", "safety_retention": True},
    {"model_id": "other/model", "tag": "alpha", "safety_retention": True},
]
MESSAGES = [{"role": "user", "content": "soru"}]


def sse(*pieces: str, finish: str = "stop", cost: float = 0.002) -> bytes:
    events: list[dict[str, Any]] = [
        {"choices": [{"delta": {"content": piece}}]} for piece in pieces
    ]
    events.append({"choices": [{"delta": {}, "finish_reason": finish}], "usage": {"cost": cost}})
    body = "".join(f"data: {json.dumps(event, ensure_ascii=False)}\n\n" for event in events)
    return (body + "data: [DONE]\n\n").encode()


Handler = Callable[[httpx.Request], httpx.Response]


def make_client(
    handler: Handler,
    providers: tuple[str, ...] = ("alpha", "beta"),
    first_token_seconds: float = 2.5,
) -> AnswerClient:
    options = AnswerClientOptions(
        model=MODEL,
        providers=providers,
        ignored_providers=("risky",),
        schema={"type": "object"},
        max_tokens=100,
        first_token_seconds=first_token_seconds,
        runaway_whitespace_limit=5,
    )
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return AnswerClient(http, base_url="https://router.test/api/v1", api_key="k", options=options)


def stream_with(client: AnswerClient, callbacks: StreamCallbacks | None = None):  # type: ignore[no-untyped-def]
    return asyncio.run(client.stream(MESSAGES, callbacks))


def test_zdr_index_excludes_safety_retention_providers() -> None:
    index = parse_zdr_index(ZDR_ENDPOINTS)

    assert index[MODEL].strict == frozenset({"alpha", "beta"})
    assert index[MODEL].safety == frozenset({"risky"})


def test_provider_with_any_safety_retention_endpoint_is_not_strict() -> None:
    endpoints = [
        {"model_id": MODEL, "tag": "alpha", "safety_retention": False},
        {"model_id": MODEL, "tag": "alpha/eu", "safety_retention": True},
    ]

    assert parse_zdr_index(endpoints)[MODEL].strict == frozenset()


def test_endpoint_without_safety_field_is_not_zdr() -> None:
    index = parse_zdr_index([{"model_id": MODEL, "tag": "alpha"}])

    assert index[MODEL].strict == frozenset()


def test_fetch_zdr_index_reads_the_endpoint_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/endpoints/zdr")
        assert request.headers["Authorization"] == "Bearer k"
        return httpx.Response(200, json={"data": ZDR_ENDPOINTS})

    async def run() -> dict[str, ZdrEntry]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
            return await fetch_zdr_index(http, "https://router.test/api/v1", "k")

    assert asyncio.run(run())[MODEL].strict == frozenset({"alpha", "beta"})


def test_select_providers_keeps_configured_order_and_drops_non_zdr() -> None:
    index = parse_zdr_index(ZDR_ENDPOINTS)

    assert select_providers(MODEL, ("beta", "gamma", "alpha"), index) == (
        ("beta", "alpha"),
        ("risky",),
    )


def test_select_providers_uses_all_strict_when_none_configured() -> None:
    providers, _ = select_providers(MODEL, (), parse_zdr_index(ZDR_ENDPOINTS))

    assert providers == ("alpha", "beta")


@pytest.mark.parametrize("model", ["unknown/model", "other/model"])
def test_model_without_zdr_endpoint_is_refused(model: str) -> None:
    with pytest.raises(ServiceUnavailable, match="ZDR"):
        select_providers(model, (), parse_zdr_index(ZDR_ENDPOINTS))


def test_stream_collects_content_and_cost_and_decodes_utf8() -> None:
    client = make_client(lambda _: httpx.Response(200, content=sse('{"a":', '"± ş"}')))

    result = stream_with(client)

    assert result.content == '{"a":"± ş"}'
    assert result.provider == "alpha"
    assert result.finish == "stop"
    assert result.cost_usd == pytest.approx(0.002)
    assert result.first_token_seconds is not None
    assert not result.incomplete


def test_request_always_enforces_zdr_and_single_provider() -> None:
    bodies: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        bodies.append(json.loads(request.content))
        return httpx.Response(200, content=sse("x"))

    stream_with(make_client(handler))

    provider = bodies[0]["provider"]
    assert provider == {
        "zdr": True,
        "data_collection": "deny",
        "order": ["alpha"],
        "allow_fallbacks": False,
        "ignore": ["risky"],
    }
    assert bodies[0]["stream"] is True


def _by_provider(responses: dict[str, httpx.Response]) -> Handler:
    def handler(request: httpx.Request) -> httpx.Response:
        return responses[json.loads(request.content)["provider"]["order"][0]]

    return handler


def test_http_error_moves_to_the_next_provider() -> None:
    client = make_client(
        _by_provider(
            {"alpha": httpx.Response(503), "beta": httpx.Response(200, content=sse("tamam"))}
        )
    )

    result = stream_with(client)

    assert result.provider == "beta"
    assert [attempt.provider for attempt in result.attempts] == ["alpha", "beta"]


def test_connection_error_moves_to_the_next_provider() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if json.loads(request.content)["provider"]["order"][0] == "alpha":
            raise httpx.ReadTimeout("yavaş")
        return httpx.Response(200, content=sse("tamam"))

    assert stream_with(make_client(handler)).provider == "beta"


def test_stream_error_event_moves_to_the_next_provider() -> None:
    error_stream = b'data: {"error": {"message": "kota"}}\n\n'
    client = make_client(
        _by_provider(
            {
                "alpha": httpx.Response(200, content=error_stream),
                "beta": httpx.Response(200, content=sse("tamam")),
            }
        )
    )

    assert stream_with(client).content == "tamam"


def test_whitespace_runaway_moves_to_the_next_provider() -> None:
    client = make_client(
        _by_provider(
            {
                "alpha": httpx.Response(200, content=sse("x", " " * 20)),
                "beta": httpx.Response(200, content=sse("tamam")),
            }
        )
    )

    assert stream_with(client).provider == "beta"


def test_runaway_on_last_provider_returns_truncated_content() -> None:
    client = make_client(
        lambda _: httpx.Response(200, content=sse("x", " " * 20)), providers=("alpha",)
    )

    result = stream_with(client)

    assert result.finish == "length"
    assert result.content.startswith("x")


def test_all_providers_failing_raises_service_unavailable() -> None:
    with pytest.raises(ServiceUnavailable, match="alpha"):
        stream_with(make_client(lambda _: httpx.Response(500)))


def test_no_retry_after_verified_content_was_shown() -> None:
    client = make_client(
        _by_provider(
            {
                "alpha": httpx.Response(200, content=sse("x", " " * 20)),
                "beta": httpx.Response(200, content=sse("asla")),
            }
        )
    )

    result = stream_with(client, StreamCallbacks(may_retry=lambda: False))

    assert result.incomplete
    assert [attempt.provider for attempt in result.attempts] == ["alpha"]


def test_partial_stream_is_reset_before_retrying() -> None:
    resets: list[bool] = []
    client = make_client(
        _by_provider(
            {
                "alpha": httpx.Response(200, content=sse("x", " " * 20)),
                "beta": httpx.Response(200, content=sse("tamam")),
            }
        )
    )

    stream_with(client, StreamCallbacks(on_reset=lambda: resets.append(True)))

    assert resets == [True]


def test_delta_callback_receives_accumulated_text() -> None:
    seen: list[str] = []
    client = make_client(lambda _: httpx.Response(200, content=sse("ab", "cd")))

    stream_with(client, StreamCallbacks(on_delta=lambda text, _: seen.append(text)))

    assert seen == ["ab", "abcd"]


def test_failing_ui_callback_does_not_break_the_stream() -> None:
    def explode(_text: str, _seconds: float) -> None:
        raise RuntimeError("arayüz")

    client = make_client(lambda _: httpx.Response(200, content=sse("tamam")))

    assert stream_with(client, StreamCallbacks(on_delta=explode)).content == "tamam"


def test_failed_attempts_travel_with_service_unavailable() -> None:
    with pytest.raises(ServiceUnavailable) as raised:
        stream_with(make_client(lambda _: httpx.Response(500)))

    assert [attempt.provider for attempt in raised.value.attempts] == ["alpha", "beta"]
    assert all(attempt.seconds >= 0 for attempt in raised.value.attempts)


async def _slow_events(*steps: tuple[float, str]) -> AsyncIterator[bytes]:
    """Her parçadan önce verilen süre beklenir; parça boşsa yalnız bitiş olayı gelir."""
    for wait, piece in steps:
        await asyncio.sleep(wait)
        event: dict[str, Any]
        if piece:
            event = {"choices": [{"delta": {"content": piece}}]}
        else:
            event = {"choices": [{"delta": {}, "finish_reason": "stop"}], "usage": {"cost": 0}}
        yield f"data: {json.dumps(event)}\n\n".encode()
    yield b"data: [DONE]\n\n"


def test_pause_after_first_token_does_not_drop_the_answer() -> None:
    read_timeouts: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        read_timeouts.append(request.extensions["timeout"]["read"])
        return httpx.Response(200, content=_slow_events((0, "ilk "), (0.2, "son"), (0, "")))

    result = stream_with(make_client(handler, providers=("alpha",), first_token_seconds=0.05))

    assert result.content == "ilk son"
    assert [attempt.error for attempt in result.attempts] == [""]
    # Gerçek bağlantıda okuma sınırı her okumaya uygulanır; ilk token sınırı olamaz.
    assert read_timeouts[0] > 0.2


def test_missing_first_token_moves_to_the_next_provider() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if json.loads(request.content)["provider"]["order"][0] == "alpha":
            return httpx.Response(200, content=_slow_events((0.2, "geç"), (0, "")))
        return httpx.Response(200, content=sse("tamam"))

    result = stream_with(make_client(handler, first_token_seconds=0.05))

    assert result.provider == "beta"
    assert result.attempts[0].error == "ilk token süresinde gelmedi"
