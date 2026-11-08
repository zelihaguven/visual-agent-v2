"""Model çıktısını güvenli biçimde tipli cevaba çevirir; hiçbir çıktı istisna fırlatmaz."""

import json
import re
from dataclasses import dataclass
from enum import StrEnum

from pydantic import ValidationError

from visual_agent.domain.answer import ModelAnswer

_THOUGHT_RE = re.compile(
    r"^\s*(?:<think>.*?</think>|<thought>.*?</thought>|"
    r"<\|?channel\|?>[^{]*?<\|?channel\|?>|<\|?channel\|?>thought[^{]*)\s*",
    re.DOTALL,
)
_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)
_LENGTH_FINISH = "length"


class ParseFailureReason(StrEnum):
    EMPTY = "empty"
    TRUNCATED = "truncated"
    INVALID_JSON = "invalid_json"
    SCHEMA = "schema"


@dataclass(frozen=True)
class ParseFailure:
    reason: ParseFailureReason
    detail: str = ""


def parse_answer(content: str, finish: str | None) -> ModelAnswer | ParseFailure:
    text = _THOUGHT_RE.sub("", content or "", count=1).strip()
    if not text:
        return ParseFailure(ParseFailureReason.EMPTY)
    match = _OBJECT_RE.search(text)
    try:
        payload = json.loads(match.group(0) if match else text, strict=False)
    except json.JSONDecodeError as error:
        reason = (
            ParseFailureReason.TRUNCATED
            if finish == _LENGTH_FINISH
            else ParseFailureReason.INVALID_JSON
        )
        return ParseFailure(reason, f"{error.msg} (konum {error.pos})")
    try:
        return ModelAnswer.model_validate(payload)
    except ValidationError as error:
        return ParseFailure(ParseFailureReason.SCHEMA, str(error.errors()[0]["msg"]))
