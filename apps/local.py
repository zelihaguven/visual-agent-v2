"""Yerel başlatma (Docker'sız, tek süreç): python -m apps.local, ya da baslat.bat.

Arayüz eskiyse derlenir, eksik araçlar bildirilir, API ve içindeki işçi yalnız bu
bilgisayardan erişilebilen adreste açılır.
"""

import argparse
import logging
import os
import shutil
import subprocess
import threading
import time
import urllib.request
import webbrowser
from collections.abc import Callable, Iterable, MutableMapping
from pathlib import Path

from visual_agent.ingest.external import ExternalTools, locate_tools
from visual_agent.settings import Settings

logger = logging.getLogger("visual_agent.local")

LOCAL_HOST = "127.0.0.1"
LOCAL_QDRANT_PATH = "data/qdrant"
WEB_SOURCES = ("src", "index.html", "package.json", "package-lock.json", "vite.config.ts")
_BROWSER_WAIT_SECONDS = 120.0
_BROWSER_POLL_SECONDS = 1.0


def _newest_change(paths: Iterable[Path]) -> float:
    newest = 0.0
    for path in paths:
        if path.is_dir():
            newest = max([newest, *(item.stat().st_mtime for item in path.rglob("*"))])
        elif path.exists():
            newest = max(newest, path.stat().st_mtime)
    return newest


def web_is_stale(web: Path) -> bool:
    """Derlenmiş arayüz yoksa ya da kaynaklardan eskiyse yeniden derlenmelidir."""
    built = web / "dist" / "index.html"
    if not built.exists():
        return True
    return _newest_change(web / name for name in WEB_SOURCES) > built.stat().st_mtime


def use_embedded_qdrant(settings: Settings, environ: MutableMapping[str, str]) -> bool:
    """Qdrant için hiçbir şey ayarlanmamışsa yerelde gömülü klasör kullanılır."""
    if settings.qdrant_path is not None or "qdrant_url" in settings.model_fields_set:
        return False
    environ["VA_QDRANT_PATH"] = LOCAL_QDRANT_PATH
    return True


def local_url(settings: Settings) -> str:
    return f"http://{LOCAL_HOST}:{settings.web_port}/"


def api_key_missing(settings: Settings) -> bool:
    """Boş ya da yalnız boşluk bırakılmış `VA_OPENROUTER_API_KEY=` satırı da anahtar yok sayılır."""
    key = settings.openrouter_api_key
    return key is None or not key.get_secret_value().strip()


def tool_report(tools: ExternalTools) -> list[str]:
    found = [
        f"LibreOffice: {tools.soffice or 'yok'}",
        f"Tesseract: {tools.tesseract or 'yok'}"
        + (f" ({', '.join(sorted(tools.tesseract_languages))})" if tools.tesseract else ""),
    ]
    return [*found, *tools.problems()]


def build_web(web: Path, npm: str | None, run: Callable[..., object] = subprocess.run) -> bool:
    """Derleme başarılıysa ya da gerekmiyorsa True; Node yoksa eski derleme kullanılır."""
    if not web_is_stale(web):
        return True
    if npm is None:
        logger.warning(
            "Arayüz derlenmemiş ya da eski, Node (npm) bulunamadı. README: Yerel kurulum"
        )
        return (web / "dist" / "index.html").exists()
    logger.info("Arayüz derleniyor (npm ci, npm run build)")
    try:
        run([npm, "ci"], cwd=web, check=True)
        run([npm, "run", "build"], cwd=web, check=True)
    except (OSError, subprocess.CalledProcessError):
        logger.exception("Arayüz derlenemedi; varsa önceki derleme kullanılacak")
        return (web / "dist" / "index.html").exists()
    return True


def _open_browser_when_ready(url: str) -> None:
    deadline = time.monotonic() + _BROWSER_WAIT_SECONDS
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{url}api/health", timeout=2):  # noqa: S310
                webbrowser.open(url)
                return
        except OSError:
            time.sleep(_BROWSER_POLL_SECONDS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Visual Agent'ı bu bilgisayarda başlatır.")
    parser.add_argument("--port", type=int, help="varsayılan: .env içindeki WEB_PORT ya da 8080")
    parser.add_argument("--no-browser", action="store_true", help="tarayıcıyı açma")
    arguments = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    settings = Settings()
    if use_embedded_qdrant(settings, os.environ):
        settings = Settings()
    if arguments.port is not None:
        settings = Settings(web_port=arguments.port)  # doğrulanır: geçersiz port açılışta durur
    if api_key_missing(settings):
        logger.warning(".env içinde VA_OPENROUTER_API_KEY yok; sorular cevaplanamaz.")
    for line in tool_report(locate_tools(settings.soffice_path, settings.tesseract_path)):
        logger.info(line)
    build_web(Path("apps/web"), shutil.which("npm"))

    url = local_url(settings)
    logger.info("Arayüz: %s (kapatmak için Ctrl+C)", url)
    if not arguments.no_browser:
        threading.Thread(target=_open_browser_when_ready, args=(url,), daemon=True).start()
    import uvicorn

    uvicorn.run("apps.api.main:create_app", factory=True, host=LOCAL_HOST, port=settings.web_port)


if __name__ == "__main__":
    main()
