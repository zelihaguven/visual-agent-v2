import os
import subprocess
from pathlib import Path

import pytest

from apps.local import (
    api_key_missing,
    build_web,
    local_url,
    prepare_offline_models,
    tool_report,
    use_embedded_qdrant,
    web_is_stale,
)
from visual_agent.ingest.external import ExternalTools
from visual_agent.settings import Settings


def _web(tmp_path: Path, built: bool = True) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "App.tsx").write_text("x", encoding="utf-8")
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    if built:
        (tmp_path / "dist").mkdir()
        (tmp_path / "dist" / "index.html").write_text("<html>", encoding="utf-8")
    return tmp_path


def _age(path: Path, seconds: float) -> None:
    stamp = path.stat().st_mtime - seconds
    os.utime(path, (stamp, stamp))


def test_missing_build_is_stale(tmp_path: Path) -> None:
    assert web_is_stale(_web(tmp_path, built=False))


def test_build_newer_than_sources_is_fresh(tmp_path: Path) -> None:
    web = _web(tmp_path)
    _age(web / "src" / "App.tsx", 60)
    _age(web / "package.json", 60)

    assert not web_is_stale(web)


def test_changed_source_makes_the_build_stale(tmp_path: Path) -> None:
    web = _web(tmp_path)
    _age(web / "dist" / "index.html", 60)

    assert web_is_stale(web)


def test_fresh_build_is_not_rebuilt(tmp_path: Path) -> None:
    web = _web(tmp_path)
    _age(web / "src" / "App.tsx", 60)
    _age(web / "package.json", 60)
    calls: list[object] = []

    assert build_web(web, "npm", lambda *args, **kwargs: calls.append(args))
    assert calls == []


def test_stale_build_runs_npm_ci_and_build(tmp_path: Path) -> None:
    web = _web(tmp_path, built=False)
    calls: list[list[str]] = []

    assert build_web(web, "npm", lambda command, **kwargs: calls.append(command))
    assert calls == [["npm", "ci"], ["npm", "run", "build"]]


def test_without_node_an_old_build_is_still_used(tmp_path: Path) -> None:
    web = _web(tmp_path)
    _age(web / "dist" / "index.html", 60)

    assert build_web(web, None)
    assert not build_web(_web(tmp_path / "bos", built=False), None)


def test_failed_build_falls_back_to_the_previous_one(tmp_path: Path) -> None:
    def fail(command: list[str], **kwargs: object) -> None:
        raise subprocess.CalledProcessError(1, command)

    web = _web(tmp_path)
    _age(web / "dist" / "index.html", 60)

    assert build_web(web, "npm", fail)
    assert not build_web(_web(tmp_path / "bos", built=False), "npm", fail)


def test_embedded_qdrant_is_used_when_nothing_is_configured() -> None:
    environ: dict[str, str] = {}

    assert use_embedded_qdrant(Settings(_env_file=None), environ)
    assert environ == {"VA_QDRANT_PATH": "data/qdrant"}


def test_configured_qdrant_is_left_alone() -> None:
    environ: dict[str, str] = {}

    assert not use_embedded_qdrant(
        Settings(_env_file=None, qdrant_url="http://127.0.0.1:6333"), environ
    )
    assert not use_embedded_qdrant(Settings(_env_file=None, qdrant_path="baska"), environ)
    assert environ == {}


def test_qdrant_server_from_environment_is_left_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VA_QDRANT_URL", "http://127.0.0.1:6333")
    environ: dict[str, str] = {}

    assert not use_embedded_qdrant(Settings(_env_file=None), environ)


def test_tool_report_names_found_tools_and_problems() -> None:
    report = tool_report(ExternalTools(None, "C:/T/tesseract.exe", frozenset({"eng", "tur"})))

    assert report[:2] == ["LibreOffice: yok", "Tesseract: C:/T/tesseract.exe (eng, tur)"]
    assert any("LibreOffice kurulu değil" in line for line in report[2:])


def test_web_port_is_read_from_the_env_file(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("WEB_PORT=9090\n", encoding="utf-8")

    settings = Settings(_env_file=env)

    assert settings.web_port == 9090
    assert local_url(settings) == "http://127.0.0.1:9090/"


def test_empty_api_key_line_counts_as_missing() -> None:
    assert api_key_missing(Settings(_env_file=None, openrouter_api_key=""))
    assert api_key_missing(Settings(_env_file=None, openrouter_api_key="   "))
    assert api_key_missing(Settings(_env_file=None, openrouter_api_key=None))
    assert not api_key_missing(Settings(_env_file=None, openrouter_api_key="anahtar"))


def test_offline_models_set_the_hub_variables_and_report_missing_models() -> None:
    environ: dict[str, str] = {}
    present = {
        "BAAI/bge-m3",
        "docling-project/docling-layout-heron",
        "docling-project/docling-models",
    }

    missing = prepare_offline_models(environ, lambda repo_id, cache_dir: repo_id in present)

    assert environ == {"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}
    assert missing == ["Qdrant/bm25"]


def test_bm25_model_is_looked_up_in_its_own_cache_folder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FASTEMBED_CACHE_PATH", raising=False)
    looked_up: dict[str, str | None] = {}

    def cached(repo_id: str, cache_dir: str | None) -> bool:
        looked_up[repo_id] = cache_dir
        return True

    assert prepare_offline_models({}, cached) == []
    assert looked_up["Qdrant/bm25"] == "data/models/fastembed"
    assert looked_up["BAAI/bge-m3"] is None  # Hugging Face'in kendi önbelleği


def test_offline_models_are_off_by_default() -> None:
    assert Settings(_env_file=None).models_offline is False


def test_a_model_counts_as_cached_when_a_snapshot_folder_exists(tmp_path: Path) -> None:
    from apps.local import _in_model_cache

    snapshot = tmp_path / "models--Qdrant--bm25" / "snapshots" / "abc123"
    assert not _in_model_cache("Qdrant/bm25", str(tmp_path))

    snapshot.mkdir(parents=True)

    assert _in_model_cache("Qdrant/bm25", str(tmp_path))


def test_an_empty_snapshot_folder_is_not_a_cached_model(tmp_path: Path) -> None:
    from apps.local import _in_model_cache

    (tmp_path / "models--Qdrant--bm25" / "snapshots").mkdir(parents=True)

    assert not _in_model_cache("Qdrant/bm25", str(tmp_path))


def test_fastembed_cache_variable_wins_over_the_default(monkeypatch: pytest.MonkeyPatch) -> None:
    from visual_agent.retrieval.encoders import bm25_cache_directory

    monkeypatch.setenv("FASTEMBED_CACHE_PATH", "/home/appuser/.cache/fastembed")

    assert bm25_cache_directory() == "/home/appuser/.cache/fastembed"


def test_docling_model_names_match_the_installed_docling() -> None:
    specs = pytest.importorskip("docling.datamodel.stage_model_specs")
    table = pytest.importorskip("docling.models.stages.table_structure.table_structure_model")
    from apps.local import _DOCLING_MODELS

    layout = specs.OBJECT_DETECTION_LAYOUT_HERON.model_spec.repo_id
    tables = table.TableStructureModel._model_repo_folder.replace("--", "/")
    assert set(_DOCLING_MODELS) == {layout, tables}
