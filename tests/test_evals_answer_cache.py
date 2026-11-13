import argparse
import asyncio
import gzip
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest

from evals.answer_cache import CacheCounts, CachingTransport, Usage, usage_from_body
from evals.gold import GoldQuestion, GoldSet, Outcome, QuestionKind
from evals.run_questions import (
    DEFAULT_CACHE_DIR,
    NO_CACHE_NOTE,
    _full_run,
    cache_label,
    check_cache_arguments,
    select_questions,
)
from tests.test_ask_pipeline import FakeClient, make_deps

URL = "https://openrouter.ai/api/v1/chat/completions"


class Upstream:
    def __init__(self, status: int = 200) -> None:
        self.calls = 0
        self.status = status

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1
        return httpx.Response(self.status, content=b"data: parca-" + str(self.calls).encode())


def _client(upstream: Upstream, directory: Path, refresh: bool = False) -> httpx.AsyncClient:
    transport = CachingTransport(httpx.MockTransport(upstream.handle), directory, refresh)
    return httpx.AsyncClient(transport=transport)


async def _ask(client: httpx.AsyncClient, body: dict[str, object]) -> str:
    async with client.stream("POST", URL, json=body) as response:
        return "".join([line async for line in response.aiter_lines()])


def _counts(client: httpx.AsyncClient) -> CacheCounts:
    transport = client._transport
    assert isinstance(transport, CachingTransport)
    return transport.counts


def test_same_request_is_answered_from_disk(tmp_path: Path) -> None:
    upstream = Upstream()

    async def run() -> tuple[str, str, CacheCounts]:
        async with _client(upstream, tmp_path) as client:
            first = await _ask(client, {"soru": "bel"})
        async with _client(upstream, tmp_path) as client:
            second = await _ask(client, {"soru": "bel"})
            return first, second, _counts(client)

    first, second, counts = asyncio.run(run())

    assert first == second == "data: parca-1"
    assert upstream.calls == 1
    assert counts == CacheCounts(hits=1, misses=0)


def test_different_request_body_is_sent_again(tmp_path: Path) -> None:
    upstream = Upstream()

    async def run() -> CacheCounts:
        async with _client(upstream, tmp_path) as client:
            await _ask(client, {"soru": "bel"})
            await _ask(client, {"soru": "basen"})
            return _counts(client)

    assert asyncio.run(run()) == CacheCounts(hits=0, misses=2)
    assert upstream.calls == 2


def test_refresh_flag_sends_and_overwrites(tmp_path: Path) -> None:
    upstream = Upstream()

    async def run() -> list[str]:
        async with _client(upstream, tmp_path) as client:
            answers = [await _ask(client, {"soru": "bel"})]
        async with _client(upstream, tmp_path, refresh=True) as client:
            answers.append(await _ask(client, {"soru": "bel"}))
        async with _client(upstream, tmp_path) as client:
            answers.append(await _ask(client, {"soru": "bel"}))
        return answers

    assert asyncio.run(run()) == ["data: parca-1", "data: parca-2", "data: parca-2"]


def test_failed_answers_are_not_kept(tmp_path: Path) -> None:
    upstream = Upstream(status=503)

    async def run() -> None:
        async with _client(upstream, tmp_path) as client:
            await _ask(client, {"soru": "bel"})
            await _ask(client, {"soru": "bel"})

    asyncio.run(run())

    assert upstream.calls == 2
    assert list(tmp_path.iterdir()) == []


def test_answer_abandoned_midway_is_not_kept(tmp_path: Path) -> None:
    upstream = Upstream()

    async def run() -> None:
        async with (
            _client(upstream, tmp_path) as client,
            client.stream("POST", URL, json={"soru": "bel"}),
        ):
            pass

    asyncio.run(run())

    assert list(tmp_path.glob("*.json")) == []


def test_other_requests_are_never_cached(tmp_path: Path) -> None:
    upstream = Upstream()

    async def run() -> CacheCounts:
        async with _client(upstream, tmp_path) as client:
            await client.get("https://openrouter.ai/api/v1/endpoints/zdr")
            await client.get("https://openrouter.ai/api/v1/endpoints/zdr")
            return _counts(client)

    assert asyncio.run(run()) == CacheCounts()
    assert upstream.calls == 2


def test_counts_are_taken_per_question() -> None:
    counts = CacheCounts(hits=5, misses=2)
    before = counts.snapshot()
    counts.hits += 2

    assert counts.since(before) == CacheCounts(hits=2, misses=0)


def test_question_is_live_only_without_any_cached_request() -> None:
    assert cache_label(CacheCounts(hits=0, misses=3)) == "live"
    assert cache_label(CacheCounts(hits=0, misses=0)) == "live"
    assert cache_label(CacheCounts(hits=2, misses=0)) == "cached"
    assert cache_label(CacheCounts(hits=1, misses=1)) == "partial"


def test_offline_miss_is_never_counted_as_live() -> None:
    assert cache_label(CacheCounts(hits=0, misses=2), offline=True) == "miss"
    assert cache_label(CacheCounts(hits=3, misses=1), offline=True) == "miss"
    assert cache_label(CacheCounts(hits=3, misses=0), offline=True) == "cached"


def _gold_with_conversation() -> GoldSet:
    def question(question_id: str, conversation: str | None, turn: int | None) -> GoldQuestion:
        return GoldQuestion(
            question_id=question_id,
            text=question_id,
            kind=QuestionKind.FOLLOW_UP if conversation else QuestionKind.DIRECT,
            domain="dikim",
            outcome=Outcome.ANSWERED,
            conversation_id=conversation,
            turn=turn,
        )

    return GoldSet(
        seed=7,
        documents=(),
        questions=(
            question("tek", None, None),
            question("s-t1", "s", 1),
            question("s-t2", "s", 2),
            question("s-t3", "s", 3),
            question("diger", None, None),
        ),
        document_texts={},
    )


def test_follow_up_is_asked_with_the_earlier_turns_of_its_conversation() -> None:
    picked = select_questions(_gold_with_conversation(), ["s-t2", "diger"])

    assert [q.question_id for q in picked] == ["s-t1", "s-t2", "diger"]


def test_without_a_selection_every_question_is_asked() -> None:
    assert len(select_questions(_gold_with_conversation(), None)) == 5


def test_unknown_question_is_refused() -> None:
    with pytest.raises(ValueError, match="yok-boyle"):
        select_questions(_gold_with_conversation(), ["yok-boyle"])


def _arguments(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "repeat": 1,
        "refresh_cache": False,
        "no_cache": False,
        "cache_dir": None,
        "offline": False,
    }
    return argparse.Namespace(**{**values, **overrides})


def test_repeated_runs_never_read_or_write_the_cache() -> None:
    arguments = _arguments(repeat=5)

    assert check_cache_arguments(arguments) is None
    assert arguments.no_cache is True


def test_single_run_uses_the_default_cache() -> None:
    arguments = _arguments()

    assert check_cache_arguments(arguments) is None
    assert arguments.no_cache is False
    assert arguments.cache_dir == DEFAULT_CACHE_DIR


@pytest.mark.parametrize(
    "overrides",
    [{"refresh_cache": True}, {"cache_dir": Path("evals/output/baska")}],
)
def test_repeating_with_a_cache_option_is_refused(overrides: dict[str, object]) -> None:
    problem = check_cache_arguments(_arguments(repeat=3, **overrides))

    assert problem is not None and "önbelleksiz" in problem


def test_repeat_must_be_positive() -> None:
    assert check_cache_arguments(_arguments(repeat=0)) is not None


def test_repeat_report_says_the_cache_was_not_used() -> None:
    assert NO_CACHE_NOTE == "önbellek kullanılmadı"


SSE_WITH_USAGE = (
    b'data: {"choices":[{"delta":{"content":"x"}}]}\n\n'
    b'data: {"choices":[],"usage":{"prompt_tokens":120,"completion_tokens":30,"cost":0.0004}}\n\n'
    b"data: [DONE]\n\n"
)


def test_usage_is_read_from_a_streamed_answer() -> None:
    usage = usage_from_body(SSE_WITH_USAGE, None)

    assert (usage.requests, usage.prompt_tokens, usage.completion_tokens) == (1, 120, 30)
    assert usage.cost_usd == 0.0004


def test_usage_is_read_from_a_compressed_json_answer() -> None:
    body = gzip.compress(
        b'{"choices":[],"usage":{"prompt_tokens":50,"completion_tokens":5,"cost":0.00002}}'
    )

    usage = usage_from_body(body, "gzip")

    assert (usage.prompt_tokens, usage.completion_tokens, usage.cost_usd) == (50, 5, 0.00002)


def test_answer_without_usage_still_counts_as_a_request() -> None:
    assert usage_from_body(b"bozuk", "gzip") == Usage(requests=1)
    assert usage_from_body(b'{"choices":[]}', None) == Usage(requests=1)


def test_usage_is_counted_for_live_and_cached_answers(tmp_path: Path) -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=SSE_WITH_USAGE)

    async def run() -> list[Usage]:
        seen = []
        for _ in range(2):
            transport = CachingTransport(httpx.MockTransport(handle), tmp_path)
            async with httpx.AsyncClient(transport=transport) as client:
                await _ask(client, {"soru": "bel"})
            seen.append(transport.usage)
        return seen

    live, cached = asyncio.run(run())

    assert live == cached == Usage(1, 120, 30, 0.0004)


def test_usage_difference_is_taken_per_question() -> None:
    usage = Usage(2, 100, 10, 0.001)
    before = usage.snapshot()
    usage.add(Usage(1, 40, 4, 0.0005))

    assert usage.since(before) == Usage(1, 40, 4, 0.0005)


@pytest.mark.parametrize(
    "overrides",
    [{"repeat": 3}, {"refresh_cache": True}, {"no_cache": True}],
)
def test_offline_run_reads_the_cache_only(overrides: dict[str, object]) -> None:
    assert check_cache_arguments(_arguments(offline=True, **overrides)) is not None


def test_offline_run_uses_the_default_cache() -> None:
    arguments = _arguments(offline=True)

    assert check_cache_arguments(arguments) is None
    assert arguments.cache_dir == DEFAULT_CACHE_DIR


def test_offline_misses_are_kept_out_of_the_score(tmp_path: Path) -> None:
    """Iskalanan istek netleştirmeye düşebilir; o soru geçen sayısına girmemeli."""
    counts = CacheCounts()

    @dataclass
    class MissingClient(FakeClient):
        async def stream(self, messages: Any, callbacks: Any = None) -> Any:
            counts.misses += 1
            return await super().stream(messages, callbacks)

    clarify = {
        "tur": "netlestirme",
        "cevap": [],
        "celiski_var": False,
        "netlestirme": {"soru": "Hangisi?", "secenekler": [{"kaynak_no": 1}]},
    }
    question = GoldQuestion(
        question_id="netlestir",
        text="iç paça kaç?",
        kind=QuestionKind.CLARIFY,
        domain="dikim",
        outcome=Outcome.CLARIFY,
    )
    gold = GoldSet(seed=7, documents=(), questions=(question,), document_texts={})
    deps = make_deps(MissingClient(clarify))

    summary = asyncio.run(
        _full_run([question], gold, deps, tmp_path / "answers.json", counts, offline=True)
    )

    assert summary["questions_missed_offline"] == ["netlestir"]
    assert summary["total"] == 0
    assert summary["passed"] == 0
