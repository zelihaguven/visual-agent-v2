import signal
import threading

import pytest

from apps.worker import main as worker_main
from apps.worker.main import run_worker
from visual_agent.settings import Settings


def test_termination_signal_stops_the_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: list[bool] = []

    def fake_run_worker(
        stop: threading.Event, poll_seconds: float, process_next: object = None
    ) -> int:
        signal.raise_signal(signal.SIGTERM)
        observed.append(stop.is_set())
        return 0

    async def fake_open_processor(settings: Settings) -> object:
        return object()

    original = signal.getsignal(signal.SIGTERM), signal.getsignal(signal.SIGINT)
    monkeypatch.setattr(worker_main, "run_worker", fake_run_worker)
    monkeypatch.setattr(worker_main, "_open_processor", fake_open_processor)
    monkeypatch.setattr(worker_main, "Settings", lambda: Settings(_env_file=None))

    try:
        worker_main.main()
    finally:
        signal.signal(signal.SIGTERM, original[0])
        signal.signal(signal.SIGINT, original[1])

    assert observed == [True]


def test_worker_survives_a_failing_job_and_tries_again() -> None:
    stop = threading.Event()
    attempts: list[int] = []

    def process_next() -> bool:
        attempts.append(1)
        if len(attempts) == 1:
            raise ConnectionError("veritabanı kilitli")
        stop.set()
        return True

    run_worker(stop, poll_seconds=0.01, process_next=process_next)

    assert len(attempts) == 2


def test_worker_stops_when_stop_is_requested() -> None:
    stop = threading.Event()
    stop.set()

    assert run_worker(stop, poll_seconds=0.01) == 0


def test_worker_waits_between_polls_until_stopped() -> None:
    stop = threading.Event()
    timer = threading.Timer(0.05, stop.set)
    timer.start()

    try:
        polls = run_worker(stop, poll_seconds=0.01)
    finally:
        timer.cancel()

    assert polls >= 1
