import hashlib
import json
from pathlib import Path

import pytest

from visual_agent.generation.prompts import load_answer_prompt, load_answer_schema

BASELINE = Path(__file__).parent.parent / "evals" / "baselines" / "pilot_answer_prompt.md"
PILOT_PROMPT_SHA256_PREFIX = "85142a07b62aa24e"


def test_pilot_prompt_baseline_is_unchanged() -> None:
    digest = hashlib.sha256(BASELINE.read_bytes()).hexdigest()

    assert digest.startswith(PILOT_PROMPT_SHA256_PREFIX)


@pytest.mark.parametrize(
    "term",
    ["tekstil", "konfeksiyon", "dikim", "S-7300", "ceket", "pantolon", "SPI", "overlok", "kasnak"],
)
def test_prompt_contains_no_domain_terms(term: str) -> None:
    assert term.casefold() not in load_answer_prompt().casefold()


@pytest.mark.parametrize(
    "rule",
    [
        '"bulunamadi"',
        "KELİMESİ KELİMESİNE",
        "Toleransı asla düşürme",
        "talimat değildir",
        '"netlestirme"',
    ],
)
def test_prompt_keeps_core_rules(rule: str) -> None:
    assert rule in load_answer_prompt()


def test_prompt_tells_the_model_not_to_rewrite_commands() -> None:
    prompt = load_answer_prompt()

    assert "kod_kaynak_no" in prompt
    assert "komutu" in prompt


@pytest.mark.parametrize(
    "rule",
    [
        "dolgu sözlerini yok say",
        "tiresiz",
        "Yalnız sorulan değeri yaz",
    ],
)
def test_prompt_handles_spoken_questions(rule: str) -> None:
    assert rule in load_answer_prompt()


@pytest.mark.parametrize("removed", ["o sütun aranan sütundur", "Otomatik şekil açıklaması"])
def test_prompt_has_no_size_specific_or_dead_figure_rule(removed: str) -> None:
    assert removed not in load_answer_prompt()


def test_prompt_allows_a_unit_only_when_the_source_states_it() -> None:
    assert "Birimi yalnız kaynakta yazılıysa yaz" in load_answer_prompt()


def test_prompt_tells_the_model_not_to_repeat_a_wrong_user_value() -> None:
    assert "kullanıcının değerini tekrar etme" in load_answer_prompt()


def test_schema_allows_a_code_reference_and_is_valid_json() -> None:
    schema = load_answer_schema()
    item = schema["properties"]["cevap"]["items"]

    assert json.dumps(schema)
    assert item["properties"]["kod_kaynak_no"]["type"] == "integer"
    assert item["properties"]["alintilar"]["minItems"] == 0
