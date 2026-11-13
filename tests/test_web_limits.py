"""Web'deki kopya sabitler API'dekilerle aynı kalır (apps/web/src/limits.ts)."""

import re
from pathlib import Path

from apps.api.main import MAX_UPLOAD_BYTES
from visual_agent.domain.conversation import MAX_QUESTION_CHARS
from visual_agent.ingest import formats

LIMITS = (Path(__file__).parent.parent / "apps" / "web" / "src" / "limits.ts").read_text(
    encoding="utf-8"
)


def _value(name: str) -> str:
    match = re.search(rf"export const {name} =\s*([^;]+);", LIMITS)
    assert match is not None, name
    return match.group(1).strip()


def test_question_limit_matches_the_api() -> None:
    assert int(_value("MAX_QUESTION_CHARS")) == MAX_QUESTION_CHARS


def test_upload_limit_matches_the_api() -> None:
    factors = [int(part) for part in _value("MAX_UPLOAD_BYTES").split("*")]
    product = 1
    for factor in factors:
        product *= factor
    assert product == MAX_UPLOAD_BYTES


def test_accepted_types_match_the_supported_formats() -> None:
    accepted = _value("ACCEPTED_TYPES").strip('"').split(",")
    assert sorted(accepted) == sorted(formats._TYPES)
