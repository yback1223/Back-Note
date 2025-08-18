import pytest
import json
from core.note_prompt_builder import NotePromptBuilder


def test_create_submit_note_prompt_happy_path():
    note = "Hello"
    quiz_structure = {"multiple_choice": 2, "short_answer": 1, "long_answer": 0}
    s = NotePromptBuilder.create_submit_note_prompt(note, quiz_structure)
    data = json.loads(s)
    assert "role" in data
    assert "core_tasks" in data
    assert data["user_input"]["note_transcript"] == note


def test_create_submit_note_prompt_validation_errors():
    with pytest.raises(Exception):
        NotePromptBuilder.create_submit_note_prompt(" ", {"multiple_choice": 1, "short_answer": 1, "long_answer": 1})
    with pytest.raises(Exception):
        NotePromptBuilder.create_submit_note_prompt("x", "not-dict")
    with pytest.raises(Exception):
        NotePromptBuilder.create_submit_note_prompt("x", {"multiple_choice": -1, "short_answer": 0, "long_answer": 0})
    with pytest.raises(Exception):
        NotePromptBuilder.create_submit_note_prompt("x", {"short_answer": 0, "long_answer": 0})
