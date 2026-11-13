"""Örnek belgeleri açık uygulamaya normal yükleme yoluyla yükler.

    uv run python -m apps.sample_documents

- Uygulama açık olmalı (baslat.bat); belgeler arayüzdeki yüklemeyle aynı uca gönderilir,
  işleme ve indeksleme uygulamanın kendi işçisinde yapılır.
- Klasörün alt klasörlerindeki dosyalar yüklenir. Kökteki dosyalar (ör. test soruları)
  yüklenmez, indekslenmez.
- Aynı dosya adıyla zaten yüklü olan belge yeniden yüklenmez. Hiçbir belge silinmez.

Örnek belgeler deneme içindir; üretimde kullanılmaz.
"""

import argparse
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from apps.local import local_url
from visual_agent.settings import Settings

DEFAULT_FOLDER = Path("ornek-belgeler")
_TIMEOUT_SECONDS = 120.0
_FAILED = "failed"


@dataclass
class UploadReport:
    uploaded: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed_before: list[str] = field(default_factory=list)
    rejected: dict[str, str] = field(default_factory=dict)


def sample_files(folder: Path) -> list[Path]:
    """Alt klasörlerdeki dosyalar, ada göre sıralı; kökteki dosyalar yüklenmez."""
    return sorted(
        (path for path in folder.rglob("*") if path.is_file() and path.parent != folder),
        key=lambda path: path.relative_to(folder).as_posix(),
    )


def _existing(client: httpx.Client) -> dict[str, str]:
    """Yüklü belgelerin dosya adı ve durumu."""
    response = client.get("/api/documents")
    response.raise_for_status()
    return {item["filename"]: item["status"] for item in response.json()}


def _reason(response: httpx.Response) -> str:
    try:
        return str(response.json().get("detail", response.status_code))
    except ValueError:
        return str(response.status_code)


def upload_samples(
    files: Iterable[Path], client: httpx.Client, progress: Callable[[str], None] = print
) -> UploadReport:
    """Yüklü olmayan dosyaları tek tek yükler; reddedilen dosya diğerlerini durdurmaz."""
    existing = _existing(client)
    report = UploadReport()
    for path in files:
        if path.name in existing:
            report.skipped.append(path.name)
            if existing[path.name] == _FAILED:
                report.failed_before.append(path.name)
            continue
        with path.open("rb") as stream:
            response = client.post("/api/documents", files={"file": (path.name, stream)})
        if response.status_code == httpx.codes.CREATED:
            existing[path.name] = response.json()["status"]
            report.uploaded.append(path.name)
            progress(f"yüklendi: {path.name}")
        else:
            report.rejected[path.name] = _reason(response)
            progress(f"yüklenemedi: {path.name} ({report.rejected[path.name]})")
    return report


def summary(report: UploadReport) -> list[str]:
    lines = [
        f"Yüklenen: {len(report.uploaded)}",
        f"Zaten yüklü olduğu için atlanan: {len(report.skipped)}",
    ]
    if report.failed_before:
        lines.append(
            "Daha önce yüklenip işlenemeyen (arayüzden yeniden işlenebilir): "
            + ", ".join(report.failed_before)
        )
    if report.rejected:
        lines.append(f"Yüklenemeyen: {len(report.rejected)}")
    if report.uploaded:
        lines.append("Belgeler uygulamada sırayla işlenir; durumları belge listesinde görünür.")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Örnek belgeleri açık uygulamaya yükler.")
    parser.add_argument("--folder", type=Path, default=DEFAULT_FOLDER)
    parser.add_argument("--url", help="uygulama adresi (varsayılan: WEB_PORT ya da 8080)")
    arguments = parser.parse_args(argv)
    url = arguments.url or local_url(Settings())
    if not arguments.folder.is_dir():
        print(f"Klasör bulunamadı: {arguments.folder}", file=sys.stderr)
        return 1
    try:
        with httpx.Client(base_url=url, timeout=_TIMEOUT_SECONDS) as client:
            report = upload_samples(sample_files(arguments.folder), client)
    except httpx.TransportError:
        print(f"Uygulamaya ulaşılamadı ({url}). Önce baslat.bat ile açın.", file=sys.stderr)
        return 1
    for line in summary(report):
        print(line)
    return 1 if report.rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
