import pytest
import json
import os
from core.quiz_result_validator import QuizResultValidator


def test_validate_gemini_response_happy_path():
    data = {
        "quiz": [
            {
                "question": "Q",
                "user_answer": "A",
                "real_answer": "A",
                "score": "Correct",
                "correction_and_explanation": "x",
                "additional_context": "y",
            }
        ]
    }
    s = json.dumps(data)
    result = QuizResultValidator.validate_gemini_response(s, expected_quiz_length=1)
    assert result["quiz"][0]["score"] == "Correct"


def test_validate_gemini_response_errors():
    with pytest.raises(Exception):
        QuizResultValidator.validate_gemini_response("not json", expected_quiz_length=1)
    with pytest.raises(Exception):
        QuizResultValidator.validate_gemini_response(json.dumps({}), expected_quiz_length=0)
    with pytest.raises(Exception):
        QuizResultValidator.validate_gemini_response(json.dumps({"quiz": {}}), expected_quiz_length=0)
    with pytest.raises(Exception):
        QuizResultValidator.validate_gemini_response(json.dumps({"quiz": []}), expected_quiz_length=1)


def test_validate_quiz_structure_helper():
    assert QuizResultValidator.validate_quiz_structure([{ "question": "Q", "user_answer": "A" }]) is True
    assert QuizResultValidator.validate_quiz_structure("not list") is False
    assert QuizResultValidator.validate_quiz_structure([]) is False
    assert QuizResultValidator.validate_quiz_structure(["x"]) is False
    assert QuizResultValidator.validate_quiz_structure([{ "user_answer": "A" }]) is False
    assert QuizResultValidator.validate_quiz_structure([{ "question": "", "user_answer": "A" }]) is False
    assert QuizResultValidator.validate_quiz_structure([{ "question": "Q", "user_answer": 1 }]) is False


def test_save_result_to_file(tmp_path):
    file_path = tmp_path / "quiz_result.json"
    QuizResultValidator.save_result_to_file({"a": 1}, str(file_path))
    assert file_path.exists()
