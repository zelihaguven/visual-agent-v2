"""Cevap modelinin tek prompt ve şema dosyası."""

import json
from importlib.resources import files
from typing import Any

_PACKAGE = files(__name__)


def load_answer_prompt() -> str:
    return _PACKAGE.joinpath("answer_v1.md").read_text(encoding="utf-8")


def load_answer_schema() -> dict[str, Any]:
    schema: dict[str, Any] = json.loads(
        _PACKAGE.joinpath("answer_v1.schema.json").read_text(encoding="utf-8")
    )
    return schema
