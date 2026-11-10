from typing import Any

import pytest
from pydantic import ValidationError

from visual_agent.settings import Settings


def make_settings(**overrides: Any) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_login_is_off_by_default() -> None:
    assert make_settings().auth_enabled is False


def test_enabling_login_before_it_exists_fails_at_startup() -> None:
    with pytest.raises(ValidationError, match="giriş henüz uygulanmadı"):
        make_settings(auth_enabled=True)


def test_values_are_read_from_prefixed_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VA_QDRANT_URL", "http://qdrant:6333")

    assert str(make_settings().qdrant_url) == "http://qdrant:6333/"


def test_invalid_qdrant_url_is_rejected() -> None:
    with pytest.raises(ValidationError):
        make_settings(qdrant_url="qdrant olmayan adres")


def test_worker_poll_interval_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        make_settings(worker_poll_seconds=0)


def test_settings_cannot_be_changed_after_creation() -> None:
    settings = make_settings()

    with pytest.raises(ValidationError):
        settings.worker_poll_seconds = 1.0  # type: ignore[misc]


def test_qdrant_server_is_used_when_no_folder_is_given() -> None:
    assert make_settings().qdrant_path is None
    assert make_settings(qdrant_path="  ").qdrant_path is None


def test_qdrant_folder_is_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VA_QDRANT_PATH", "data/qdrant")

    assert make_settings().qdrant_path == "data/qdrant"
