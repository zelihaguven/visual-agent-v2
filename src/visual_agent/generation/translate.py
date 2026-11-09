"""BM25 kolu için sorgu çevirisi. Buluta yalnız soru metni gider."""

from collections.abc import Awaitable, Callable, Mapping, Sequence

from visual_agent.generation.json_model import JsonModel

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
_MAX_TOKENS = 300


def bm25_text(translations: Mapping[str, str], fallback: str) -> str:
    return " ".join(dict.fromkeys(translations.values())) or fallback


def make_translator(client: JsonModel) -> Translator:
    async def translate(question: str, source: str, targets: Sequence[str]) -> str:
        names = ", ".join(_LANGUAGE_NAMES.get(target, target) for target in targets)
        system = _PROMPT.format(
            source=_LANGUAGE_NAMES.get(source, source), targets=names, codes=", ".join(targets)
        )
        parsed = await client.complete(system, question, _MAX_TOKENS)
        translations = {t: str(parsed[t]).strip() for t in targets if parsed.get(t)}
        return bm25_text(translations, question)

    return translate
