"""BM25 kolu için sorgu çevirisi. Buluta yalnız soru metni gider."""

import json
import re
from collections.abc import Awaitable, Callable, Mapping, Sequence

import httpx

Translator = Callable[[str, str, Sequence[str]], Awaitable[str]]

_LANGUAGE_NAMES = {
    "en": "English",
    "tr": "Turkish",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
}
_PROMPT = (
    "You translate search queries for a document search engine. Translate the user's question "
    "from {source} into: {targets}. Keep product codes, model numbers, error codes, table and "
    "column names, numbers and units exactly as written. Reply with a JSON object whose keys are "
    "the language codes ({codes}) and whose values are the translations; nothing else."
)
_TIMEOUT_SECONDS = 15.0
_MAX_TOKENS = 300
_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def bm25_text(translations: Mapping[str, str], fallback: str) -> str:
    return " ".join(dict.fromkeys(translations.values())) or fallback


def make_translator(
    http: httpx.AsyncClient,
    *,
    base_url: str,
    api_key: str,
    model: str,
    providers: Sequence[str],
    ignored_providers: Sequence[str],
) -> Translator:
    constraints: dict[str, object] = {
        "zdr": True,
        "data_collection": "deny",
        "order": list(providers),
        "only": list(providers),
        "allow_fallbacks": True,
    }
    if ignored_providers:
        constraints["ignore"] = list(ignored_providers)

    async def translate(question: str, source: str, targets: Sequence[str]) -> str:
        names = ", ".join(_LANGUAGE_NAMES.get(target, target) for target in targets)
        system = _PROMPT.format(
            source=_LANGUAGE_NAMES.get(source, source), targets=names, codes=", ".join(targets)
        )
        response = await http.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=_TIMEOUT_SECONDS,
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": question},
                ],
                "temperature": 0,
                "max_tokens": _MAX_TOKENS,
                "reasoning": {"enabled": False},
                "response_format": {"type": "json_object"},
                "provider": constraints,
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"] or ""
        match = _OBJECT_RE.search(content)
        parsed = json.loads(match.group(0)) if match else {}
        translations = {t: str(parsed[t]).strip() for t in targets if parsed.get(t)}
        return bm25_text(translations, question)

    return translate
