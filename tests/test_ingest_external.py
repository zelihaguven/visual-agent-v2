import subprocess
import sys
from pathlib import Path

import pytest

from visual_agent.ingest.external import (
    SOFFICE_MISSING,
    TESSERACT_MISSING,
    ConversionFailed,
    ExternalTools,
    MissingTool,
    find_tool,
    list_tesseract_languages,
    locate_tools,
)

INSTALLED = {"soffice": "/opt/lo/soffice", "tesseract": "/opt/tess/tesseract"}


def _which(name: str) -> str | None:
    return INSTALLED.get(name) or (name if name.startswith("C:/Araclar/") else None)


def test_tools_are_found_on_path() -> None:
    tools = locate_tools(None, None, _which, lambda _: frozenset({"tur", "eng"}))

    assert tools == ExternalTools(
        "/opt/lo/soffice", "/opt/tess/tesseract", frozenset({"tur", "eng"})
    )
    assert tools.problems() == []


def test_configured_path_wins_over_path() -> None:
    found = find_tool("C:/Araclar/LibreOffice/program/soffice.exe", ("soffice",), _which)

    assert found == "C:/Araclar/LibreOffice/program/soffice.exe"


def test_missing_configured_path_is_not_replaced_by_another_install() -> None:
    assert find_tool("D:/yok/soffice.exe", ("soffice",), _which) is None


def test_missing_tools_are_explained_at_startup() -> None:
    tools = locate_tools(None, None, lambda _: None, lambda _: frozenset())

    problems = tools.problems()

    assert len(problems) == 2
    assert "LibreOffice kurulu değil" in problems[0] and "VA_SOFFICE_PATH" in problems[0]
    assert "Tesseract kurulu değil" in problems[1] and "VA_TESSERACT_PATH" in problems[1]


def test_missing_language_data_is_explained_at_startup() -> None:
    tools = ExternalTools(None, "/opt/tess/tesseract", frozenset({"eng", "osd"}))

    problems = tools.problems()

    assert any("Türkçe" in problem and "tur.traineddata" in problem for problem in problems)
    assert not any("İngilizce" in problem for problem in problems)


def _fake_soffice(monkeypatch: pytest.MonkeyPatch, writes_output: bool) -> list[list[str]]:
    """LibreOffice yerine geçer: çağrıları kaydeder, istenirse dönüştürmenin çıktısını yazar."""
    calls: list[list[str]] = []

    def run(command: list[str], **_: object) -> subprocess.CompletedProcess[bytes]:
        calls.append(command)
        if writes_output and "--convert-to" in command:
            source = Path(command[-1])
            outdir = Path(command[command.index("--outdir") + 1])
            (outdir / f"{source.stem}.{command[command.index('--convert-to') + 1]}").write_bytes(
                b"x"
            )
        return subprocess.CompletedProcess(command, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", run)
    return calls


def test_conversion_uses_its_own_profile_and_returns_the_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = _fake_soffice(monkeypatch, writes_output=True)
    source = tmp_path / "föy.docx"

    output = ExternalTools("soffice", None).convert(source, tmp_path, "pdf")

    assert output == tmp_path / "föy.pdf"
    [command] = calls
    assert command[1].startswith("-env:UserInstallation=file:")
    assert not list(tmp_path.glob("lo-profile-*"))


def test_conversion_without_output_fails_instead_of_continuing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _fake_soffice(monkeypatch, writes_output=False)

    with pytest.raises(ConversionFailed, match="föy.docx dosyasını PDF biçimine çeviremedi"):
        ExternalTools("soffice", None).convert(tmp_path / "föy.docx", tmp_path, "pdf")

    assert not list(tmp_path.glob("lo-profile-*"))


def test_office_documents_fail_with_a_clear_message_without_libreoffice() -> None:
    with pytest.raises(MissingTool, match="LibreOffice kurulu değil") as raised:
        ExternalTools(None, None).require_soffice()

    assert str(raised.value) == SOFFICE_MISSING


def test_ocr_fails_with_a_clear_message_without_tesseract_or_language() -> None:
    with pytest.raises(MissingTool) as missing:
        ExternalTools("/opt/lo/soffice", None).require_tesseract("tur")
    with pytest.raises(MissingTool, match="'tur' dil verisi yok"):
        ExternalTools(None, "/opt/tess/tesseract", frozenset({"eng"})).require_tesseract("tur")

    assert str(missing.value) == TESSERACT_MISSING
    assert ExternalTools(None, "/t/tesseract", frozenset({"tur"})).require_tesseract("tur") == (
        "/t/tesseract"
    )


def test_language_list_is_read_from_tesseract(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        output = b'List of available languages in "C:/tessdata/" (3):\r\neng\r\nosd\r\ntur\r\n'
        return subprocess.CompletedProcess(command, 0, stdout=output)

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert list_tesseract_languages("tesseract") == frozenset({"eng", "osd", "tur"})


def test_unrunnable_tesseract_has_no_languages() -> None:
    assert list_tesseract_languages(str(Path(sys.executable).parent / "yok.exe")) == frozenset()


def test_combined_ocr_language_needs_every_part() -> None:
    both = ExternalTools(None, "/t/tesseract", frozenset({"tur", "eng"}))
    assert both.require_tesseract("tur+eng") == "/t/tesseract"
    with pytest.raises(MissingTool, match="'eng' dil verisi yok"):
        ExternalTools(None, "/t/tesseract", frozenset({"tur"})).require_tesseract("tur+eng")
