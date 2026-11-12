"""Dış araçların (LibreOffice, Tesseract) yeri ve durumu; işçi açılırken bir kez bulunur.

Araç PATH'ten ya da ayarla verilen yoldan bulunur. Eksik araç yalnız ona ihtiyaç duyan
belgeyi anlaşılır bir mesajla durdurur; diğer belgeler işlenmeye devam eder.
"""

import os
import shutil
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from visual_agent.domain.document import UNDETECTED_LANGUAGE

_LIST_LANGUAGES_TIMEOUT_SECONDS = 30
_EXPECTED_LANGUAGES = {"tur": "Türkçe", "eng": "İngilizce"}
_TESSERACT_LANGUAGES = {
    UNDETECTED_LANGUAGE: "tur+eng",
    "tr": "tur",
    "en": "eng",
    "fr": "fra",
    "es": "spa",
    "de": "deu",
}
_FALLBACK_TESSERACT_LANGUAGE = "eng"


def tesseract_language(language: str) -> str:
    """Belge dilinin Tesseract karşılığı.

    Dil henüz bilinmiyorsa (ilk yükleme) Türkçe ve İngilizce birlikte okunur: 8 okumalık
    ölçümde tek başına Türkçe, İngilizce sayfada bir değeri değiştirdi, birlikte okuma
    değiştirmedi (docs/kararlar.md, OCR).
    """
    return _TESSERACT_LANGUAGES.get(language, _FALLBACK_TESSERACT_LANGUAGE)


Which = Callable[[str], str | None]
ListLanguages = Callable[[str], frozenset[str]]

SOFFICE_MISSING = (
    "LibreOffice kurulu değil; Office dosyaları (.docx, .pptx, .doc, .ppt, .odt, .rtf, .xls)"
    " işlenemiyor."
)
TESSERACT_MISSING = (
    "Tesseract kurulu değil; taranmış sayfa, fotoğraf ya da görsel içeren belgeler işlenemiyor."
)


class MissingTool(RuntimeError):
    """Belgeyi işlemek için gereken dış araç kurulu değil."""


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

    def require_tesseract(self, language: str) -> str:
        if self.tesseract is None:
            raise MissingTool(TESSERACT_MISSING)
        missing = [part for part in language.split("+") if part not in self.tesseract_languages]
        if missing:
            raise MissingTool(f"Tesseract'ta '{missing[0]}' dil verisi yok; bu belge okunamıyor.")
        return self.tesseract

    def subprocess_environment(self, base: Mapping[str, str] | None = None) -> dict[str, str]:
        """OCRmyPDF Tesseract'ı PATH'te arar; bulunan Tesseract'ın klasörü öne eklenir."""
        environment = dict(os.environ if base is None else base)
        if self.tesseract is not None:
            folder = str(Path(self.tesseract).parent)
            current = environment.get("PATH", "")
            environment["PATH"] = folder + os.pathsep + current if current else folder
        return environment

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
