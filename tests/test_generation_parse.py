import json

import pytest

from visual_agent.domain.answer import AnswerKind, ModelAnswer
from visual_agent.generation.parse import ParseFailure, ParseFailureReason, parse_answer

VALID = {
    "tur": "cevap",
    "cevap": [{"alintilar": [{"kaynak_no": 1, "metin": "M: 76,5"}], "metin": "76,5 cm."}],
    "celiski_var": False,
}


def _parsed(content: str, finish: str | None = "stop") -> ModelAnswer:
    result = parse_answer(content, finish)
    assert isinstance(result, ModelAnswer), result
    return result


def _failure(content: str, finish: str | None = "stop") -> ParseFailureReason:
    result = parse_answer(content, finish)
    assert isinstance(result, ParseFailure), result
    return result.reason


def test_valid_answer_is_parsed() -> None:
    answer = _parsed(json.dumps(VALID))

    assert answer.kind is AnswerKind.ANSWER
    assert answer.items[0].quotes[0].source_no == 1


def test_thinking_prefix_is_removed() -> None:
    assert _parsed("<think>düşünce</think>" + json.dumps(VALID)).kind is AnswerKind.ANSWER


def test_unescaped_tab_inside_string_is_tolerated() -> None:
    assert "\t" in _parsed(json.dumps(VALID).replace("76,5 cm.", "76,5\tcm.")).items[0].text


def test_empty_output_is_reported() -> None:
    assert _failure("") is ParseFailureReason.EMPTY


def test_truncated_output_is_reported_as_truncated() -> None:
    assert _failure(json.dumps(VALID)[:-30], "length") is ParseFailureReason.TRUNCATED


def test_broken_json_is_reported_as_invalid() -> None:
    assert _failure(json.dumps(VALID)[:-30], "stop") is ParseFailureReason.INVALID_JSON


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"tur": "cevap", "cevap": "düz metin"}, id="cevap-metin"),
        pytest.param({"tur": "cevap", "cevap": ["düz metin"]}, id="oge-metin"),
        pytest.param({"tur": "cevap", "cevap": [{"metin": "alıntısız"}]}, id="alintisiz"),
        pytest.param(
            {"tur": "cevap", "cevap": [{"alintilar": "x", "metin": "y"}]}, id="alinti-tip"
        ),
        pytest.param(
            {"tur": "cevap", "cevap": [{"alintilar": [1], "metin": "y"}]}, id="alinti-oge"
        ),
        pytest.param({"tur": "bilinmeyen", "cevap": []}, id="tur-gecersiz"),
        pytest.param({"cevap": []}, id="tur-yok"),
        pytest.param({"tur": "netlestirme", "cevap": []}, id="netlestirme-yok"),
        pytest.param(
            {
                "tur": "netlestirme",
                "netlestirme": {"soru": "?", "secenekler": [{"kaynak_no": 1}, {"kaynak_no": 2}]},
                "cevap": [{"alintilar": [{"kaynak_no": 1, "metin": "x"}], "metin": "y"}],
            },
            id="hem-soru-hem-cevap",
        ),
        pytest.param(
            {
                "tur": "bulunamadi",
                "cevap": [{"alintilar": [{"kaynak_no": 1, "metin": "x"}], "metin": "y"}],
            },
            id="bulunamadi-dolu",
        ),
        pytest.param([1, 2, 3], id="liste"),
    ],
)
def test_output_outside_the_schema_never_raises(payload: object) -> None:
    assert _failure(json.dumps(payload, ensure_ascii=False)) is not None


def test_code_reference_can_replace_quotes() -> None:
    payload = {"tur": "cevap", "cevap": [{"alintilar": [], "kod_kaynak_no": 3, "metin": "Komut."}]}

    assert _parsed(json.dumps(payload)).items[0].code_source_no == 3
