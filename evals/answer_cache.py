"""Yalnız ölçüm için OpenRouter cevap önbelleği. Uygulama bu modülü hiç kullanmaz.

Model isteği gövdesinin özetiyle diske yazılır; aynı istek yeniden gönderilmez. Önbellekten
gelen cevabın süresi ve maliyeti gerçek değildir: çağıran, soru başına kaç isteğin
önbellekten geldiğini sayar ve bu soruları süre ve maliyet özetine katmaz.
"""

import base64
import gzip
import hashlib
import json
import zlib
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


@dataclass
class Usage:
    """Model isteklerinin token ve maliyeti; önbellekten gelen cevapta kayıttan okunur."""

    requests: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0

    def add(self, other: "Usage") -> None:
        self.requests += other.requests
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.cost_usd += other.cost_usd

    def snapshot(self) -> "Usage":
        return Usage(self.requests, self.prompt_tokens, self.completion_tokens, self.cost_usd)

    def since(self, earlier: "Usage") -> "Usage":
        return Usage(
            self.requests - earlier.requests,
            self.prompt_tokens - earlier.prompt_tokens,
            self.completion_tokens - earlier.completion_tokens,
            self.cost_usd - earlier.cost_usd,
        )


def _decoded(body: bytes, encoding: str | None) -> str:
    if encoding == "gzip":
        body = gzip.decompress(body)
    elif encoding == "deflate":
        body = zlib.decompress(body)
    return body.decode("utf-8", errors="replace")


def _usage_objects(text: str) -> list[dict[str, object]]:
    """Akışlı cevapta kullanım son olaylardan birindedir; düz cevapta gövdenin içindedir."""
    stripped = text.lstrip()
    if stripped.startswith("{"):
        try:
            usage = json.loads(stripped).get("usage")
        except json.JSONDecodeError:
            return []
        return [usage] if isinstance(usage, dict) else []
    found = []
    for line in text.splitlines():
        if line.startswith("data: ") and '"usage"' in line:
            try:
                usage = json.loads(line[6:]).get("usage")
            except json.JSONDecodeError:
                continue
            if isinstance(usage, dict):
                found.append(usage)
    return found[-1:]


def usage_from_body(body: bytes, encoding: str | None) -> Usage:
    try:
        objects = _usage_objects(_decoded(body, encoding))
    except (OSError, zlib.error):
        return Usage(requests=1)
    usage = Usage(requests=1)
    for item in objects:
        usage.prompt_tokens += int(str(item.get("prompt_tokens") or 0))
        usage.completion_tokens += int(str(item.get("completion_tokens") or 0))
        usage.cost_usd += float(str(item.get("cost") or 0.0))
    return usage


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

    def __init__(self, response: httpx.Response, target: Path, usage: Usage) -> None:
        self._response = response
        self._target = target
        self._usage = usage
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
            body = b"".join(self._parts)
            _write_entry(self._target, self._response, body)
            encoding = self._response.headers.get("content-encoding")
            self._usage.add(usage_from_body(body, encoding))


def _write_entry(target: Path, response: httpx.Response, body: bytes) -> None:
    entry = {
        "status": response.status_code,
        "headers": [[name, value] for name, value in response.headers.multi_items()],
        "body": base64.b64encode(body).decode("ascii"),
    }
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(entry), encoding="utf-8")
    temporary.replace(target)


def _read_entry(path: Path, request: httpx.Request) -> tuple[httpx.Response, Usage]:
    entry = json.loads(path.read_text(encoding="utf-8"))
    body = base64.b64decode(entry["body"])
    headers = [(name, value) for name, value in entry["headers"]]
    encoding = next((v for k, v in headers if k.lower() == "content-encoding"), None)
    response = httpx.Response(
        status_code=entry["status"],
        headers=headers,
        stream=httpx.ByteStream(body),
        request=request,
    )
    return response, usage_from_body(body, encoding)


class OfflineMiss(httpx.ConnectError):
    """Çevrimdışı değerlendirmede önbellekte olmayan model isteği gönderilmez."""


class CachingTransport(httpx.AsyncBaseTransport):
    """Yalnız başarılı ve sonuna kadar okunmuş model cevapları saklanır.

    offline: önbellekte olmayan model isteği ağa gitmez, OfflineMiss olur ve ıska sayılır;
    istemci bunu sağlayıcı hatası gibi karşılar. Model dışı istekler (ZDR listesi) gider.
    """

    def __init__(
        self,
        inner: httpx.AsyncBaseTransport,
        directory: Path,
        refresh: bool = False,
        offline: bool = False,
    ) -> None:
        self._inner = inner
        self._directory = directory
        self._refresh = refresh
        self._offline = offline
        self.counts = CacheCounts()
        self.usage = Usage()
        directory.mkdir(parents=True, exist_ok=True)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if not _cacheable(request):
            return await self._inner.handle_async_request(request)
        await request.aread()
        target = self._directory / f"{request_key(request)}.json"
        if target.exists() and not self._refresh:
            self.counts.hits += 1
            response, usage = _read_entry(target, request)
            self.usage.add(usage)
            return response
        self.counts.misses += 1
        if self._offline:
            raise OfflineMiss("önbellekte yok; çevrimdışı değerlendirme", request=request)
        response = await self._inner.handle_async_request(request)
        if response.status_code != _OK:
            return response
        return httpx.Response(
            status_code=response.status_code,
            headers=response.headers,
            stream=_RecordingStream(response, target, self.usage),
            request=request,
            extensions=response.extensions,
        )

    async def aclose(self) -> None:
        await self._inner.aclose()
