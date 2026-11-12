import json
from pathlib import Path

import httpx
import pytest

from apps.sample_documents import main, sample_files, summary, upload_samples


def _folder(tmp_path: Path) -> Path:
    root = tmp_path / "ornek"
    (root / "a").mkdir(parents=True)
    (root / "b" / "c").mkdir(parents=True)
    (root / "sorular.md").write_text("soru", encoding="utf-8")
    (root / "a" / "bir.md").write_text("bir", encoding="utf-8")
    (root / "b" / "iki.pdf").write_bytes(b"%PDF")
    (root / "b" / "c" / "uc.txt").write_text("uc", encoding="utf-8")
    return root


class _App:
    """Uygulamanın belge uçlarını taklit eder; yüklenenleri kaydeder."""

    def __init__(self, existing: dict[str, str], reject: set[str] | None = None) -> None:
        self.documents = dict(existing)
        self.reject = reject or set()
        self.posted: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            rows = [{"filename": name, "status": s} for name, s in self.documents.items()]
            return httpx.Response(200, json=rows)
        name = request.content.split(b'filename="')[1].split(b'"')[0].decode()
        self.posted.append(name)
        if name in self.reject:
            return httpx.Response(415, json={"detail": "Desteklenmeyen dosya türü."})
        self.documents[name] = "queued"
        return httpx.Response(201, json={"filename": name, "status": "queued"})


def _client(app: _App) -> httpx.Client:
    return httpx.Client(base_url="http://test", transport=httpx.MockTransport(app))


def test_only_files_in_subfolders_are_samples(tmp_path: Path) -> None:
    root = _folder(tmp_path)

    assert [p.name for p in sample_files(root)] == ["bir.md", "uc.txt", "iki.pdf"]


def test_uploads_missing_files_and_skips_loaded_ones(tmp_path: Path) -> None:
    app = _App({"bir.md": "ready", "uc.txt": "failed"})
    messages: list[str] = []

    report = upload_samples(sample_files(_folder(tmp_path)), _client(app), messages.append)

    assert app.posted == ["iki.pdf"]
    assert report.uploaded == ["iki.pdf"]
    assert report.skipped == ["bir.md", "uc.txt"]
    assert report.failed_before == ["uc.txt"]
    assert messages == ["yüklendi: iki.pdf"]


def test_second_run_uploads_nothing(tmp_path: Path) -> None:
    app = _App({})
    files = sample_files(_folder(tmp_path))
    upload_samples(files, _client(app), lambda _: None)

    again = upload_samples(files, _client(app), lambda _: None)

    assert again.uploaded == []
    assert len(app.posted) == 3


def test_rejected_file_does_not_stop_the_rest(tmp_path: Path) -> None:
    app = _App({}, reject={"bir.md"})

    report = upload_samples(sample_files(_folder(tmp_path)), _client(app), lambda _: None)

    assert report.rejected == {"bir.md": "Desteklenmeyen dosya türü."}
    assert report.uploaded == ["uc.txt", "iki.pdf"]
    assert "Yüklenemeyen: 1" in summary(report)


def test_summary_mentions_failed_documents() -> None:
    from apps.sample_documents import UploadReport

    lines = summary(UploadReport(skipped=["x.md"], failed_before=["x.md"]))

    assert lines[1] == "Zaten yüklü olduğu için atlanan: 1"
    assert "x.md" in lines[2]


def test_main_reports_missing_folder(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--folder", str(tmp_path / "yok")]) == 1
    assert "Klasör bulunamadı" in capsys.readouterr().err


def test_main_reports_closed_app(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--folder", str(_folder(tmp_path)), "--url", "http://127.0.0.1:9"])

    assert code == 1
    assert "baslat.bat" in capsys.readouterr().err


def test_main_uploads_through_the_app(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    app = _App({})
    real_client = httpx.Client

    def client(**kwargs: object) -> httpx.Client:
        return real_client(base_url="http://test", transport=httpx.MockTransport(app))

    monkeypatch.setattr("apps.sample_documents.httpx.Client", client)

    assert main(["--folder", str(_folder(tmp_path))]) == 0
    assert "Yüklenen: 3" in capsys.readouterr().out
    assert json.dumps(sorted(app.posted)) == json.dumps(["bir.md", "iki.pdf", "uc.txt"])
