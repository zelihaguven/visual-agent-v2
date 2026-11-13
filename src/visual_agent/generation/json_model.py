"""Kısa, JSON dönen yardımcı model çağrıları. ZDR her çağrıda zorunludur.

Süre sınırını çağıran koyar (`asyncio.wait_for`). Paylaşılan httpx istemcisinin varsayılan
5 sn sınırı da geçerlidir: `wait_for` daha uzunsa önce httpx keser.
"""

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import httpx

_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(frozen=True)
class JsonModel:
    http: httpx.AsyncClient
    base_url: str
    api_key: str
    model: str
    providers: Sequence[str]
    ignored_providers: Sequence[str]

    def _constraints(self) -> dict[str, object]:
        constraints: dict[str, object] = {
            "zdr": True,
            "data_collection": "deny",
            "order": list(self.providers),
            "only": list(self.providers),
            "allow_fallbacks": True,
        }
        if self.ignored_providers:
            constraints["ignore"] = list(self.ignored_providers)
        return constraints

    async def complete(self, system: str, user: str, max_tokens: int) -> dict[str, Any]:
        """Modelin döndürdüğü JSON nesnesi; nesne yoksa boş sözlük."""
        response = await self.http.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0,
                "max_tokens": max_tokens,
                "reasoning": {"enabled": False},
                "response_format": {"type": "json_object"},
                "provider": self._constraints(),
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"] or ""
        match = _OBJECT_RE.search(content)
        parsed: dict[str, Any] = json.loads(match.group(0)) if match else {}
        return parsed
