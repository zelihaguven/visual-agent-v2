"""Yalnız ölçüm için OpenRouter cevap önbelleği. Uygulama bu modülü hiç kullanmaz.

Model isteği gövdesinin özetiyle diske yazılır; aynı istek yeniden gönderilmez. Önbellekten
gelen cevabın süresi ve maliyeti gerçek değildir: çağıran, soru başına kaç isteğin
önbellekten geldiğini sayar ve bu soruları süre ve maliyet özetine katmaz.
"""

import base64
import hashlib
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

import httpx

_CACHED_PATH_SUFFIX = "/chat/completions"
_OK = 200


@dataclass
class CacheCounts:
    hits: int = 0
    misses: int = 0

    def since(self, earlier: "CacheCounts") -> "CacheCounts":
        return CacheCounts(self.hits - earlier.hits, self.misses - earlier.misses)

    def snapshot(self) -> "CacheCounts":
        return CacheCounts(self.hits, self.misses)


def request_key(request: httpx.Request) -> str:
    digest = hashlib.sha256()
    digest.update(str(request.url).encode("utf-8"))
    digest.update(b"\0")
    digest.update(request.content)
    return digest.hexdigest()


def _cacheable(request: httpx.Request) -> bool:
    return request.method == "POST" and request.url.path.endswith(_CACHED_PATH_SUFFIX)


class _RecordingStream(httpx.AsyncByteStream):
    """Akış istemciye parça parça geçer; sonuna kadar okunursa diske yazılır."""

    def __init__(self, response: httpx.Response, target: Path) -> None:
        self._response = response
        self._target = target
        self._parts: list[bytes] = []
        self._complete = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        async for part in self._response.stream:  # type: ignore[union-attr]
            self._parts.append(part)
            yield part
        self._complete = True

    async def aclose(self) -> None:
        await self._response.aclose()
        if self._complete:
            _write_entry(self._target, self._response, b"".join(self._parts))


def _write_entry(target: Path, response: httpx.Response, body: bytes) -> None:
    entry = {
        "status": response.status_code,
        "headers": [[name, value] for name, value in response.headers.multi_items()],
        "body": base64.b64encode(body).decode("ascii"),
    }
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(entry), encoding="utf-8")
    temporary.replace(target)


def _read_entry(path: Path, request: httpx.Request) -> httpx.Response:
    entry = json.loads(path.read_text(encoding="utf-8"))
    return httpx.Response(
        status_code=entry["status"],
        headers=[(name, value) for name, value in entry["headers"]],
        stream=httpx.ByteStream(base64.b64decode(entry["body"])),
        request=request,
    )


class CachingTransport(httpx.AsyncBaseTransport):
    """Yalnız başarılı ve sonuna kadar okunmuş model cevapları saklanır."""

    def __init__(
        self, inner: httpx.AsyncBaseTransport, directory: Path, refresh: bool = False
    ) -> None:
        self._inner = inner
        self._directory = directory
        self._refresh = refresh
        self.counts = CacheCounts()
        directory.mkdir(parents=True, exist_ok=True)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if not _cacheable(request):
            return await self._inner.handle_async_request(request)
        await request.aread()
        target = self._directory / f"{request_key(request)}.json"
        if target.exists() and not self._refresh:
            self.counts.hits += 1
            return _read_entry(target, request)
        self.counts.misses += 1
        response = await self._inner.handle_async_request(request)
        if response.status_code != _OK:
            return response
        return httpx.Response(
            status_code=response.status_code,
            headers=response.headers,
            stream=_RecordingStream(response, target),
            request=request,
            extensions=response.extensions,
        )

    async def aclose(self) -> None:
        await self._inner.aclose()
