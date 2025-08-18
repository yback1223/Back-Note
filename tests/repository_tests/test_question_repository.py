import pytest
from repositories.my_db import MyDB
from repositories.question_repository import QuestionRepository


def setup_db_with_note(tmp_path):
    db_file = tmp_path / "question.db"
    db = MyDB(db_path=str(db_file))
    db.connect()
    c = db.cursor
    c.execute("INSERT INTO note (note_name, note_content) VALUES (?, ?)", ("Note", "Content"))
    note_id = c.lastrowid
    db.conn.commit()
    return db, note_id


def test_question_insert_and_get(tmp_path):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = QuestionRepository(db.conn)
        qid = repo.insert_question(note_id, "What?", "multiple_choice", "A")
        assert qid > 0

        row = repo.get_question_by_id(qid)
        assert row is not None
        assert row[0] == qid

        qs = repo.get_all_questions(note_id)
        assert any(r[0] == qid for r in qs)
    finally:
        db.close()


def test_question_invalid_inputs(tmp_path):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = QuestionRepository(db.conn)
        with pytest.raises(Exception):
            repo.insert_question(0, "What?", "multiple_choice", "A")
        with pytest.raises(Exception):
            repo.insert_question(note_id, " ", "multiple_choice", "A")
        with pytest.raises(Exception):
            repo.insert_question(note_id, "What?", " ", "A")
        with pytest.raises(Exception):
            repo.insert_question(note_id, "What?", "bad_type", "A")
        with pytest.raises(Exception):
            repo.get_all_questions(0)
        with pytest.raises(Exception):
            repo.get_question_by_id(0)
    finally:
        db.close()


def test_question_repo_db_errors(tmp_path, monkeypatch):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = QuestionRepository(db.conn)

        class FailingCursor:
            def execute(self, *args, **kwargs):
                import sqlite3
                raise sqlite3.Error("boom")

        repo.cursor = FailingCursor()

        with pytest.raises(Exception) as exc1:
            repo.get_all_questions(note_id)
        assert "Failed to retrieve questions" in str(exc1.value)

        with pytest.raises(Exception) as exc2:
            repo.get_question_by_id(1)
        assert "Failed to retrieve question" in str(exc2.value)

        with pytest.raises(Exception) as exc3:
            repo.insert_question(note_id, "Q", "multiple_choice", "A")
        assert ("Failed to insert question" in str(exc3.value)) or ("violates" in str(exc3.value))
    finally:
        db.close()
