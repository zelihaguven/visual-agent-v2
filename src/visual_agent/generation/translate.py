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
    "column names, numbers and units exactly as written. When a technical term has more than one "
    "common name in the target language, include those names too, side by side in the same "
    "translation. Reply with a JSON object whose keys are "
    "the language codes ({codes}) and whose values are the translations; nothing else."
)
_MAX_TOKENS = 300


def bm25_text(translations: Mapping[str, str], fallback: str) -> str:
    return " ".join(dict.fromkeys(translations.values())) or fallback


def make_translator(client: JsonModel) -> Translator:
    async def translate(question: str, source: str, targets: Sequence[str]) -> str:
        # Sorunun kendi dili çevrilmez: soru o dilde zaten yazılı, çıktıyı boşuna uzatır.
        others = [target for target in targets if target != source]
        names = ", ".join(_LANGUAGE_NAMES.get(target, target) for target in others)
        system = _PROMPT.format(
            source=_LANGUAGE_NAMES.get(source, source), targets=names, codes=", ".join(others)
        )
        parsed = await client.complete(system, question, _MAX_TOKENS)
        texts = {t: question if t == source else str(parsed.get(t) or "").strip() for t in targets}
        return bm25_text({t: text for t, text in texts.items() if text}, question)

    return translate
