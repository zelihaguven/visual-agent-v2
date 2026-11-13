@echo off
rem Visual Agent: bu bilgisayarda Docker ve yonetici yetkisi olmadan baslatir (cift tikla).
rem Arayuz: http://127.0.0.1:8080  Kapatmak: bu pencerede Ctrl+C ya da pencereyi kapat.
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set PYTHONUTF8=1

rem Kullanici klasorune kurulan araclar (README: Yerel kurulum) PATH listesine eklenir.
for %%D in ("%LOCALAPPDATA%\Programs\nodejs" "%LOCALAPPDATA%\Programs\Tesseract-OCR" "%LOCALAPPDATA%\Programs\LibreOffice\program") do (
    if exist "%%~D" set "PATH=%%~D;!PATH!"
)

where uv >nul 2>nul
if errorlevel 1 (
    echo uv bulunamadi. Kurulum icin README.md: "Yerel kurulum".
    pause
    exit /b 1
)
if not exist ".env" (
    echo .env dosyasi yok. .env.example dosyasini .env olarak kopyalayip VA_OPENROUTER_API_KEY degerini doldurun.
    pause
    exit /b 1
)

rem Gelistirme paketleri (pytest, mypy, ruff...) kurulmaz; uv run ortami yeniden esitlemez.
uv sync --frozen --no-dev --extra retrieval --extra ingest
if errorlevel 1 (
    echo Python paketleri kurulamadi.
    pause
    exit /b 1
)
uv run --no-sync python -m apps.local %*
pause
