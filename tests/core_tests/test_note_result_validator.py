import pytest
import json
import os
from core.note_result_validator import NoteResultValidator


def test_validate_gemini_response_happy_path(tmp_path):
    data = {
        "summary": "s",
        "quiz": [
            {"question_type": "multiple_choice", "question": "Q", "options": ["A", "B"], "answer": "A"}
        ]
    }
    s = json.dumps(data)
    result = NoteResultValidator.validate_gemini_response(s)
    assert result["summary"] == "s"


def test_validate_gemini_response_errors():
    with pytest.raises(Exception):
        NoteResultValidator.validate_gemini_response("not json")
    with pytest.raises(Exception):
        NoteResultValidator.validate_gemini_response(json.dumps({"quiz": []}))
    with pytest.raises(Exception):
        NoteResultValidator.validate_gemini_response(json.dumps({"summary": "s"}))
    with pytest.raises(Exception):
        NoteResultValidator.validate_gemini_response(json.dumps({"summary": "s", "quiz": {}}))


def test_save_result_to_file(tmp_path):
    file_path = tmp_path / "note_result.json"
    NoteResultValidator.save_result_to_file({"a": 1}, str(file_path))
    assert file_path.exists()
