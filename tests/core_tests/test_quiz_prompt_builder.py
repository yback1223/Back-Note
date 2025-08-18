import pytest
import json
from core.quiz_prompt_builder import QuizPromptBuilder


def test_create_submit_quiz_prompt_happy_path():
    quiz = [{"question": "Q1", "user_answer": "A"}]
    s = QuizPromptBuilder.create_submit_quiz_prompt(quiz)
    data = json.loads(s)
    assert "role" in data
    assert "user_input" in data and "quiz_with_answers" in data["user_input"]


def test_create_submit_quiz_prompt_validation_errors():
    with pytest.raises(Exception):
        QuizPromptBuilder.create_submit_quiz_prompt("not-list")
    with pytest.raises(Exception):
        QuizPromptBuilder.create_submit_quiz_prompt([])
    with pytest.raises(Exception):
        QuizPromptBuilder.create_submit_quiz_prompt(["not-dict"])
    with pytest.raises(Exception):
        QuizPromptBuilder.create_submit_quiz_prompt([{ "user_answer": "A" }])
    with pytest.raises(Exception):
        QuizPromptBuilder.create_submit_quiz_prompt([{ "question": "Q1", "user_answer": 123 }])
