import asyncio
import signal

import pytest

from apps.worker import main as worker_main
from visual_agent.settings import Settings


def test_termination_signal_stops_the_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: list[bool] = []

    async def fake_loop(process_next: object, stop: asyncio.Event, poll_seconds: float) -> int:
        signal.raise_signal(signal.SIGTERM)
        await asyncio.wait_for(stop.wait(), 5)
        observed.append(stop.is_set())
        return 0

    async def fake_open_processor(settings: Settings) -> object:
        class Processor:
            async def process_next(self) -> bool:
                return False

        return Processor()

    original = signal.getsignal(signal.SIGTERM), signal.getsignal(signal.SIGINT)
    monkeypatch.setattr(worker_main, "process_until_stopped", fake_loop)
    monkeypatch.setattr(worker_main, "_open_processor", fake_open_processor)
    monkeypatch.setattr(worker_main, "Settings", lambda: Settings(_env_file=None))

    try:
        worker_main.main()
    finally:
        signal.signal(signal.SIGTERM, original[0])
        signal.signal(signal.SIGINT, original[1])

    assert observed == [True]


def test_separate_worker_refuses_the_embedded_qdrant_folder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        worker_main, "Settings", lambda: Settings(_env_file=None, qdrant_path="data/qdrant")
    )

    with pytest.raises(SystemExit, match="tek sürece kilitlenir"):
        worker_main.main()
