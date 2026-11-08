"""Model akışını güvenli olaylara çevirir: değerler doğrulanana kadar ekrana çıkmaz."""

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from pydantic import ValidationError

from visual_agent.domain.answer import ItemCheck, ModelItem, PromptSource
from visual_agent.verification.answer import verify_item
from visual_agent.verification.text import identifier_spans

Event = dict[str, object]
EventSink = Callable[[Event], None]

UNVERIFIED_MESSAGE = "Değer doğrulanamadı, kaynağa bakın."
INCOMPLETE_MESSAGE = "Cevap tamamlanamadı, kaynağa bakın."
_HIDDEN = "▒▒▒"
_ANSWER_KEY = '"cevap"'
_TEXT_KEY = "metin"
_MAX_ESCAPE_TAIL = 7
_NUMBER_WORDS = {
    "tr": "bir iki üç dört beş altı yedi sekiz dokuz on onbir oniki",
    "en": "one two three four five six seven eight nine ten eleven twelve",
}
_UNITS = [
    "mm",
    "cm",
    "m",
    "km",
    "in",
    "inch",
    "inches",
    "inç",
    "″",
    '"',
    "ft",
    "µm",
    "g",
    "kg",
    "mg",
    "lb",
    "oz",
    "n",
    "nm",
    "v",
    "kv",
    "a",
    "ma",
    "w",
    "kw",
    "hz",
    "khz",
    "rpm",
    "dk",
    "dakika",
    "sn",
    "saniye",
    "s",
    "sec",
    "min",
    "h",
    "saat",
    "gün",
    "°c",
    "°f",
    "°",
    "%",
    "bar",
    "psi",
    "pa",
    "kpa",
    "mpa",
    "l",
    "ml",
    "cc",
    "tl",
]
_UNIT_PATTERN = "|".join(sorted((re.escape(unit) for unit in _UNITS), key=len, reverse=True))
_DIGIT_LIKE = r"\d±①-⓿❶-➓¼-¾⅐-⅟²³¹"
_NUMBER_TOKEN_RE = re.compile(
    rf"[^\s]*[{_DIGIT_LIKE}][^\s]*(?:\s+(?:{_UNIT_PATTERN})(?!\w))?", re.IGNORECASE
)
_VISIBLE_WORD_RE = re.compile(r"[^\W\d_]{2,}")


def _number_word_re(language: str) -> re.Pattern[str]:
    words = _NUMBER_WORDS.get(language, _NUMBER_WORDS["tr"]).split()
    return re.compile(r"(?<!\w)(" + "|".join(words) + r")(?!\w)", re.IGNORECASE)


def _hidden_spans(text: str, language: str) -> list[tuple[int, int]]:
    spans = sorted(
        [
            *(match.span() for match in _NUMBER_TOKEN_RE.finditer(text)),
            *(match.span() for match in _number_word_re(language).finditer(text)),
            *identifier_spans(text),
        ]
    )
    merged: list[tuple[int, int]] = []
    for start, end in spans:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def mask_values(text: str, language: str) -> str:
    """Sayı, kod ve teknik adları gizler; kalan metin hemen gösterilebilir."""
    parts: list[str] = []
    last = 0
    for start, end in _hidden_spans(text, language):
        parts += [text[last:start], _HIDDEN]
        last = end
    return "".join([*parts, text[last:]])


def _string_end(content: str, start: int) -> int:
    """Açılış tırnağından sonra kapanış tırnağının konumu; yoksa metnin sonu."""
    escaped = False
    for position in range(start, len(content)):
        character = content[position]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == '"':
            return position
    return len(content)


def _answer_array_start(content: str) -> int:
    key = content.find(_ANSWER_KEY)
    return content.find("[", key) if key >= 0 else -1


@dataclass
class _TextScanner:
    """Yarım JSON içinde öğe düzeyindeki "metin" alanlarını izler."""

    stack: list[str] = field(default_factory=lambda: ["["])
    last_key: str = ""
    expect_value: bool = False
    spans: list[tuple[int, int]] = field(default_factory=list)

    def read_string(self, content: str, position: int) -> int:
        end = _string_end(content, position + 1)
        if self.expect_value:
            at_item_level = len(self.stack) == 2 and self.stack[-1] == "{"
            if at_item_level and self.last_key == _TEXT_KEY:
                self.spans.append((position + 1, end))
            self.expect_value = False
        elif content[end + 1 : end + 4].lstrip().startswith(":"):
            self.last_key = content[position + 1 : end]
        return end + 1

    def read_structure(self, character: str) -> None:
        if character == ":":
            self.expect_value = True
            return
        if character in "{[":
            self.stack.append(character)
        elif character in "}]":
            self.stack.pop()
        if character in "{[}],":
            self.expect_value = False


def item_text_spans(content: str) -> list[tuple[int, int]]:
    """Öğelerin kendi "metin" değerlerinin konumları; alıntıların metni hariç."""
    array = _answer_array_start(content)
    if array < 0:
        return []
    scanner = _TextScanner()
    position = array + 1
    while position < len(content) and scanner.stack:
        if content[position] == '"':
            position = scanner.read_string(content, position)
        else:
            scanner.read_structure(content[position])
            position += 1
    return scanner.spans


def closed_item_bounds(content: str) -> list[tuple[int, int]]:
    array = _answer_array_start(content)
    if array < 0:
        return []
    bounds: list[tuple[int, int]] = []
    depth = 0
    start = 0
    position = array + 1
    while position < len(content):
        character = content[position]
        if character == '"':
            position = _string_end(content, position + 1)
        elif character == "{":
            start = position if depth == 0 else start
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                bounds.append((start, position + 1))
        elif character == "]" and depth == 0:
            break
        position += 1
    return bounds


def _decode_partial(raw: str) -> str:
    """Yarım kaçış dizisiyle bitebilen JSON dizesini çözer."""
    for cut in range(_MAX_ESCAPE_TAIL):
        try:
            decoded: str = json.loads(f'"{raw[: len(raw) - cut]}"', strict=False)
            return decoded
        except ValueError:
            continue
    return ""


def _complete_words(text: str, is_open: bool) -> str:
    if not is_open:
        return text
    last_space = text.rfind(" ")
    return text[:last_space] if last_space >= 0 else ""


class StreamAssembler:
    """Metin hemen akar; öğeler sırayla ve yalnız doğrulandıktan sonra açılır."""

    def __init__(self, sources: Mapping[int, PromptSource], language: str, emit: EventSink) -> None:
        self._sources = sources
        self._language = language
        self._emit = emit
        self.first_verified_seconds: float | None = None
        self._clear()

    def _clear(self) -> None:
        self._shown: dict[int, str] = {}
        self._checked: list[tuple[ModelItem | None, ItemCheck | None]] = []
        self._cursor = 0
        self.verified: list[tuple[ModelItem, ItemCheck]] = []

    def feed(self, content: str, seconds: float) -> None:
        self._stream_text(content)
        self._check_closed_items(content)
        self._reveal(seconds)

    def _stream_text(self, content: str) -> None:
        closed = len(closed_item_bounds(content))
        for index, (start, end) in enumerate(item_text_spans(content)):
            if index < self._cursor:
                continue
            is_open = index >= closed and end >= len(content)
            text = _complete_words(_decode_partial(content[start:end]), is_open)
            masked = mask_values(text, self._language)
            if masked and masked != self._shown.get(index):
                self._shown[index] = masked
                self._emit({"type": "item_stream", "index": index, "text": masked})

    def _parse_item(self, raw: str) -> ModelItem | None:
        try:
            return ModelItem.model_validate(json.loads(raw, strict=False))
        except (ValueError, ValidationError):
            return None

    def _check_closed_items(self, content: str) -> None:
        bounds = closed_item_bounds(content)
        while len(self._checked) < len(bounds):
            start, end = bounds[len(self._checked)]
            item = self._parse_item(content[start:end])
            check = verify_item(item, self._sources) if item is not None else None
            self._checked.append((item, check))

    def _reveal(self, seconds: float) -> None:
        while self._cursor < len(self._checked):
            index = self._cursor
            item, check = self._checked[index]
            if item is not None and check is not None and check.ok:
                self.verified.append((item, check))
                if self.first_verified_seconds is None:
                    self.first_verified_seconds = seconds
                self._emit(
                    {
                        "type": "item_verified",
                        "index": index,
                        "text": item.text,
                        "source_numbers": list(check.source_numbers),
                        "from_figure": check.from_figure,
                    }
                )
            else:
                numbers = list(check.source_numbers) if check is not None else []
                self._emit(
                    {
                        "type": "item_unverified",
                        "index": index,
                        "message": UNVERIFIED_MESSAGE,
                        "source_numbers": numbers,
                    }
                )
            self._cursor += 1

    def may_retry(self) -> bool:
        """Doğrulanmış içerik gösterildiyse başka sağlayıcıya geçilmez."""
        return not self.verified

    def reset(self) -> None:
        self._clear()
        self._emit({"type": "reset"})

    def interrupted(self) -> None:
        self._emit({"type": "incomplete", "message": INCOMPLETE_MESSAGE})
