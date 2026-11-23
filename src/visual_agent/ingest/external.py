"""Dış araçların (LibreOffice, Tesseract) yeri ve durumu; işçi açılırken bir kez bulunur.

Araç PATH'ten ya da ayarla verilen yoldan bulunur. Eksik araç yalnız ona ihtiyaç duyan
belgeyi anlaşılır bir mesajla durdurur; diğer belgeler işlenmeye devam eder.
"""

import shutil
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

_LIST_LANGUAGES_TIMEOUT_SECONDS = 30
_CONVERT_TIMEOUT_SECONDS = 180
_EXPECTED_LANGUAGES = {"tur": "Türkçe", "eng": "İngilizce"}


def tesseract_text(
    executable: str, image: Path, language: str, page_mode: str, timeout: float
) -> str:
    """Tesseract'ın bir görseldeki metni (eğiklik düzeltmesiz). Satır sonları `\n` olur."""
    completed = subprocess.run(
        [executable, str(image), "stdout", "-l", language, "--psm", page_mode],
        check=True,
        capture_output=True,
        timeout=timeout,
    )
    return completed.stdout.decode("utf-8", errors="replace").replace("\r\n", "\n")


Which = Callable[[str], str | None]
ListLanguages = Callable[[str], frozenset[str]]

SOFFICE_MISSING = (
    "LibreOffice kurulu değil; Office dosyaları (.docx, .pptx, .doc, .ppt, .odt, .rtf, .xls)"
    " işlenemiyor."
)
TESSERACT_MISSING = (
    "Tesseract kurulu değil; taranmış sayfa ya da fotoğraf içeren belgeler işlenemiyor."
)


class MissingTool(RuntimeError):
    """Belgeyi işlemek için gereken dış araç kurulu değil."""


class ConversionFailed(RuntimeError):
    """LibreOffice dönüştürmesi çıktı dosyası üretmedi; belge eksik işlenmez, işlenemedi olur."""


class ReaderUnavailable(RuntimeError):
    """Taranmış sayfaların okuyucusu ayarlı değil ya da ulaşılamıyor; belge okuyucuyu bekler."""


def find_tool(configured: str | None, names: tuple[str, ...], which: Which) -> str | None:
    """Ayarla verilen yol önce denenir; verilmemişse araç PATH'te aranır."""
    if configured is not None:
        return which(configured)
    return next((found for name in names if (found := which(name)) is not None), None)


def list_tesseract_languages(executable: str) -> frozenset[str]:
    try:
        completed = subprocess.run(
            [executable, "--list-langs"],
            check=True,
            capture_output=True,
            timeout=_LIST_LANGUAGES_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    lines = completed.stdout.decode("utf-8", errors="replace").splitlines()
    return frozenset(line.strip() for line in lines[1:] if line.strip())


@dataclass(frozen=True)
class ExternalTools:
    soffice: str | None
    tesseract: str | None
    tesseract_languages: frozenset[str] = frozenset()

    def require_soffice(self) -> str:
        if self.soffice is None:
            raise MissingTool(SOFFICE_MISSING)
        return self.soffice

    def convert(self, path: Path, work: Path, target: str) -> Path:
        """LibreOffice ile `target` biçimine çevirir; her çağrının kendi geçici profili var.

        LibreOffice çıktı yazmadan 0 koduyla çıkabiliyor (Windows, 26.8; nedeni bilinmiyor,
        docs/acik-notlar.md). Çıktı yoksa belge eksik işlenmez, açıkça işlenemedi olur.
        """
        executable = self.require_soffice()
        profile = Path(tempfile.mkdtemp(prefix="lo-profile-", dir=work))
        command = [
            executable,
            f"-env:UserInstallation={profile.resolve().as_uri()}",
            "--headless",
            "--convert-to",
            target,
            "--outdir",
            str(work),
            str(path),
        ]
        try:
            subprocess.run(
                command, check=True, capture_output=True, timeout=_CONVERT_TIMEOUT_SECONDS
            )
        finally:
            shutil.rmtree(profile, ignore_errors=True)
        output = work / f"{path.stem}.{target}"
        if not output.exists():
            raise ConversionFailed(
                f"LibreOffice {path.name} dosyasını {target.upper()} biçimine çeviremedi;"
                " belge işlenemedi. Yeniden işlemeyi deneyin."
            )
        return output

    def require_tesseract(self, language: str) -> str:
        if self.tesseract is None:
            raise MissingTool(TESSERACT_MISSING)
        missing = [part for part in language.split("+") if part not in self.tesseract_languages]
        if missing:
            raise MissingTool(f"Tesseract'ta '{missing[0]}' dil verisi yok; bu belge okunamıyor.")
        return self.tesseract

    def problems(self) -> list[str]:
        """Açılışta gösterilecek, eksik araçları ve ne yapılacağını anlatan mesajlar."""
        messages = []
        if self.soffice is None:
            messages.append(
                f"{SOFFICE_MISSING} Kurun ya da VA_SOFFICE_PATH ile soffice yolunu verin."
            )
        if self.tesseract is None:
            messages.append(
                f"{TESSERACT_MISSING} Kurun ya da VA_TESSERACT_PATH ile tesseract yolunu verin."
            )
            return messages
        for code, name in _EXPECTED_LANGUAGES.items():
            if code not in self.tesseract_languages:
                messages.append(
                    f"Tesseract'ta {name} dil verisi ({code}.traineddata) yok;"
                    " bu dildeki taranmış belgeler okunamaz."
                )
        return messages


def locate_tools(
    soffice: str | None,
    tesseract: str | None,
    which: Which = shutil.which,
    list_languages: ListLanguages = list_tesseract_languages,
) -> ExternalTools:
    found_soffice = find_tool(soffice, ("soffice", "libreoffice"), which)
    found_tesseract = find_tool(tesseract, ("tesseract",), which)
    languages = list_languages(found_tesseract) if found_tesseract else frozenset()
    return ExternalTools(found_soffice, found_tesseract, languages)
