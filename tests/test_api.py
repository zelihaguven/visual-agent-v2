import asyncio
import subprocess
import sys
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


def test_health_reports_service_is_up() -> None:
    client = TestClient(create_app(Settings(_env_file=None)))

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_is_ok_when_every_dependency_answers() -> None:
    response = _client_with({"database": _up, "qdrant": _up}).get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["dependencies"] == {"database": True, "qdrant": True}


def test_health_is_unavailable_when_a_dependency_fails() -> None:
    response = _client_with({"database": _up, "qdrant": _down}).get("/api/health")

    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"
    assert response.json()["dependencies"] == {"database": True, "qdrant": False}


def test_health_does_not_expose_connection_details() -> None:
    response = _client_with({"qdrant": _down}).get("/api/health")

    assert "gizli-baglanti-adresi" not in response.text


def test_health_does_not_wait_for_a_hanging_dependency(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api_main, "_HEALTH_TIMEOUT_SECONDS", 0.01)

    response = _client_with({"database": _hangs}).get("/api/health")

    assert response.status_code == 503
    assert response.json()["dependencies"] == {"database": False}


def _web_build(tmp_path: Path) -> Path:
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<html>arayüz</html>", encoding="utf-8")
    (tmp_path / "assets" / "app-1a2b.js").write_text("console.log(1)", encoding="utf-8")
    return tmp_path


def test_built_web_interface_is_served_from_the_api_port(tmp_path: Path) -> None:
    client = TestClient(
        create_app(Settings(_env_file=None, web_directory=str(_web_build(tmp_path))))
    )

    page = client.get("/")
    asset = client.get("/assets/app-1a2b.js")

    assert page.status_code == 200 and "arayüz" in page.text
    assert page.headers["cache-control"] == "no-cache"
    assert asset.headers["cache-control"].endswith("immutable")
    assert client.get("/api/health").json()["status"] == "ok"


def test_missing_web_build_leaves_only_the_api(tmp_path: Path) -> None:
    client = TestClient(create_app(Settings(_env_file=None, web_directory=str(tmp_path))))

    assert client.get("/").status_code == 404
    assert client.get("/api/health").status_code == 200


def test_api_starts_without_document_processing_packages() -> None:
    """Sunucudaki API imajında openpyxl, Docling ve OCR paketleri yoktur."""
    code = (
        "import sys; import apps.api.services, apps.api.main; "
        "loaded = [m for m in ('visual_agent.ingest.pipeline', 'openpyxl', 'docling') "
        "if m in sys.modules]; print(loaded); sys.exit(1 if loaded else 0)"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
