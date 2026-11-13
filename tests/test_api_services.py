import asyncio
from pathlib import Path

import pytest

from apps.api.services import open_services
from apps.worker import main as worker_main
from visual_agent.ask.deps import AskRequest
from visual_agent.domain.result import Failed
from visual_agent.settings import Settings


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        database_path=str(tmp_path / "veri" / "katalog.db"),
        qdrant_path=str(tmp_path / "qdrant"),
        storage_directory=str(tmp_path / "belgeler"),
        worker_poll_seconds=0.01,
        openrouter_api_key=None,
    )


def test_services_start_the_worker_and_stop_it_on_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    started = asyncio.Event()
    polls: list[int] = []

    def fake_ingest(settings: Settings) -> object:
        started.set()
        return object()

    async def fake_loop(step: object, stop: asyncio.Event, poll_seconds: float) -> None:
        while not stop.is_set():
            polls.append(1)
            await asyncio.sleep(poll_seconds)

    monkeypatch.setattr(worker_main, "default_ingest", fake_ingest)
    monkeypatch.setattr(worker_main, "process_until_stopped", fake_loop)

    async def run() -> tuple[object, list[str]]:
        async with open_services(_settings(tmp_path)) as services:
            await asyncio.wait_for(started.wait(), 5)
            outcome = await services.ask(AskRequest("Bel kaç?"))
            for check in services.health_checks.values():
                await check()  # hata vermeden döner
        return outcome.result, sorted(services.health_checks)

    result, checks = asyncio.run(run())

    assert isinstance(result, Failed)  # anahtar yok: model çağrılmadan açıklayan hata
    assert checks == ["database", "qdrant"]
    assert (tmp_path / "belgeler").is_dir()
    assert polls  # işçi döngüsü çalıştı ve çıkışta durduruldu


def test_services_without_in_process_worker_do_not_load_ingest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(settings: Settings) -> object:
        raise AssertionError("işçi API sürecinde başlamamalı")

    monkeypatch.setattr(worker_main, "default_ingest", fail)
    settings = _settings(tmp_path).model_copy(update={"worker_in_process": False})

    async def run() -> None:
        async with open_services(settings):
            await asyncio.sleep(0.05)

    asyncio.run(run())
