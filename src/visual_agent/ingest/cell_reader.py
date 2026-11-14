"""OCR'lı tablo hücrelerini iki bağımsız okumayla yeniden okur.

Hücre yerel OCR ve bir görüntü modeliyle okunur; ikisi aynı okursa değer kesinleşir. Ayrılırlarsa
ikinci bir görüntü modeli hakemdir: birinci modelle aynı okursa değer kesinleşir. Kesinleşmeyen
hücrenin sayıları cevapta gizlenir. Buluta yalnız hücrenin küçük görüntüsü gider (ZDR); okumalar
görüntünün özetiyle saklanır, yeniden işlemede aynı hücre için yeniden istek atılmaz.
"""

import base64
import hashlib
import io
import logging
import re
import threading
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import httpx
from PIL import Image

logger = logging.getLogger(__name__)

ReadImage = Callable[[Image.Image], str | None]
"""Hücre görüntüsünü okur; okunamazsa None."""

_UNICODE_FRACTIONS = {
    "½": "1/2",
    "⅓": "1/3",
    "⅔": "2/3",
    "¼": "1/4",
    "¾": "3/4",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
}
_SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉⁄", "01234567890123456789/")
_SUPERSCRIPT_AFTER_DIGIT_RE = re.compile(r"(\d)([⁰¹²³⁴⁵⁶⁷⁸⁹])")
_UNREADABLE = {"?", ""}
PROMPT = (
    "The image is one cell of a table. Write exactly what is printed in the cell and nothing "
    "else. Write fractions as numerator/denominator after a space, e.g. 27 1/2 or -3/8. Keep a "
    "minus sign if printed. If you cannot read it with certainty, answer ?"
)
_REQUEST_SECONDS = 60.0
_MAX_ANSWER_TOKENS = 40


def canonical(text: str | None) -> str:
    """Okumanın karşılaştırılabilir yazımı: Unicode kesirler ve üst simgeler düz yazılır."""
    if text is None:
        return ""
    for glyph, plain in _UNICODE_FRACTIONS.items():
        text = text.replace(glyph, f" {plain}")
    # "21³/4": kesrin payı tam sayıya yapışmaz.
    text = _SUPERSCRIPT_AFTER_DIGIT_RE.sub(r"\1 \2", text)
    text = text.translate(_SUPERSCRIPTS).replace("—", "-").replace("–", "-")
    text = " ".join(text.split())
    return "" if text in _UNREADABLE else text


_DIGIT_RE = re.compile(r"\d")
_WHOLE_AND_FRACTION_RE = re.compile(r"^-?\d+ \d+/\d+$")


def single_value(text: str) -> bool:
    """Hücrede tek değer var: "27 1/2", "-3/8", "SL055" tektir; "1 1", "-1/2 1" iki değerdir.

    Komşu iki hücre tek hücre sanılırsa iki okuyucu da iki değeri birlikte okur; böyle bir
    okuma bir sütuna ait tek değer gibi kesinleşmemeli.
    """
    numeric = [token for token in text.split() if _DIGIT_RE.search(token)]
    return len(numeric) <= 1 or bool(_WHOLE_AND_FRACTION_RE.match(" ".join(numeric)))


def same_reading(first: str | None, second: str | None) -> bool:
    a, b = canonical(first), canonical(second)
    return bool(a) and a.replace(" ", "") == b.replace(" ", "")


@dataclass(frozen=True)
class CellRead:
    text: str
    """Kesinleşen değer; kesinleşmediyse boş."""
    confirmed: bool


@dataclass(frozen=True)
class CellReader:
    """Yerel okuma + görüntü modeli; ayrılırlarsa hakem model. Belge başına sınırlıdır."""

    local: ReadImage
    primary: ReadImage
    referee: ReadImage
    max_cells: int
    workers: int = 8

    def read(self, images: Sequence[Image.Image]) -> list[CellRead | None]:
        """Sınırı aşan hücreler okunmaz (None); çağıran onları kesinleşmemiş sayar."""
        allowed = list(images[: self.max_cells])
        if len(images) > len(allowed):
            logger.warning(
                "Hücre okuma sınırı aşıldı: %d hücrenin %d tanesi okunmadı",
                len(images),
                len(images) - len(allowed),
            )
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            reads: list[CellRead | None] = list(pool.map(self._read_one, allowed))
        return [*reads, *[None] * (len(images) - len(allowed))]

    def _read_one(self, image: Image.Image) -> CellRead:
        primary = self.primary(image)
        if (
            canonical(primary)
            and single_value(canonical(primary))
            and (
                same_reading(self.local(image), primary)
                or same_reading(self.referee(image), primary)
            )
        ):
            return CellRead(canonical(primary), confirmed=True)
        return CellRead("", confirmed=False)


def locked(read: ReadImage) -> ReadImage:
    """Aynı anda tek çağrı: yerel OCR motoru iş parçacıkları arasında paylaşılmaz."""
    lock = threading.Lock()

    def guarded(image: Image.Image) -> str | None:
        with lock:
            return read(image)

    return guarded


def _png(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class VisionModelReader:
    """OpenRouter üzerinden ZDR görüntü modeli; okumalar diskte saklanır."""

    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str,
        cache_directory: Path,
        client: httpx.Client | None = None,
    ) -> None:
        self._model = model
        self._headers = {"Authorization": f"Bearer {api_key}"}
        self._url = f"{base_url.rstrip('/')}/chat/completions"
        self._cache = cache_directory
        self._client = client or httpx.Client(timeout=_REQUEST_SECONDS)

    def _cache_path(self, data: bytes) -> Path:
        digest = hashlib.sha256(f"{self._model}\n{PROMPT}\n".encode() + data).hexdigest()
        return self._cache / digest[:2] / f"{digest}.txt"

    def __call__(self, image: Image.Image) -> str | None:
        data = _png(image)
        path = self._cache_path(data)
        if path.exists():
            return path.read_text(encoding="utf-8")
        text = self._request(base64.b64encode(data).decode())
        if text is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return text

    def _request(self, encoded: str) -> str | None:
        body = {
            "model": self._model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{encoded}"},
                        },
                    ],
                }
            ],
            "temperature": 0,
            "max_tokens": _MAX_ANSWER_TOKENS,
            "reasoning": {"enabled": False},
            "provider": {"zdr": True, "data_collection": "deny"},
        }
        try:
            response = self._client.post(self._url, headers=self._headers, json=body)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"].get("content") or ""
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as error:
            logger.warning("Hücre görüntü modeliyle okunamadı (%s): %s", self._model, error)
            return None
        return re.sub(r"\s+", " ", str(content)).strip()
