import asyncio
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient

from apps.api import main as api_main
from apps.api.main import ApiServices, Repository, create_app
from visual_agent.ask.deps import AskRequest
from visual_agent.domain.result import AskOutcome
from visual_agent.settings import Settings

Check = Callable[[], Awaitable[object]]


async def _ask_is_not_called(request: AskRequest) -> AskOutcome:
    raise AssertionError("health soru hattına gitmemeli")


async def _up() -> object:
    return 1


async def _down() -> object:
    raise ConnectionError("gizli-baglanti-adresi")


async def _hangs() -> object:
    await asyncio.sleep(30)
    return 1


def _client_with(checks: Mapping[str, Check]) -> TestClient:
    services = ApiServices(
        repository=cast(Repository, object()),
        ask=_ask_is_not_called,
        storage_directory=Path("."),
        health_checks=checks,
    )
    return TestClient(create_app(Settings(_env_file=None), services))


def test_health_reports_service_is_up_and_login_is_off() -> None:
    client = TestClient(create_app(Settings(_env_file=None)))

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "auth_enabled": False}


def test_health_is_ok_when_every_dependency_answers() -> None:
    response = _client_with({"postgres": _up, "qdrant": _up}).get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["dependencies"] == {"postgres": True, "qdrant": True}


def test_health_is_unavailable_when_a_dependency_fails() -> None:
    response = _client_with({"postgres": _up, "qdrant": _down}).get("/api/health")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["dependencies"] == {"postgres": True, "qdrant": False}


def test_health_does_not_expose_connection_details() -> None:
    response = _client_with({"qdrant": _down}).get("/api/health")

    assert "gizli-baglanti-adresi" not in response.text


def test_health_does_not_wait_for_a_hanging_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_main, "_HEALTH_TIMEOUT_SECONDS", 0.01)

    response = _client_with({"postgres": _hangs}).get("/api/health")

    assert response.status_code == 503
    assert response.json()["dependencies"] == {"postgres": False}
