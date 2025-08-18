import pytest
import sqlite3
from repositories.my_db import MyDB
from repositories.grading_repository import GradingRepository


def setup_db_with_question(tmp_path):
    db_file = tmp_path / "grading.db"
    db = MyDB(db_path=str(db_file))
    db.connect()
    c = db.cursor
    c.execute("INSERT INTO note (note_name, note_content) VALUES (?, ?)", ("Note", "Content"))
    note_id = c.lastrowid
    c.execute(
        "INSERT INTO question (note_id, question, question_type, preview_answer) VALUES (?, ?, ?, ?)",
        (note_id, "Q?", "multiple_choice", "A")
    )
    question_id = c.lastrowid
    db.conn.commit()
    return db, question_id


def test_grading_crud_and_queries(tmp_path):
    db, qid = setup_db_with_question(tmp_path)
    try:
        repo = GradingRepository(db.conn)
        # Insert grading
        gid = repo.insert_grading(qid, user_answer="B", real_answer="A", score="0/1",
                                  correction_and_explanation="Explain", additional_context="Ctx")
        assert isinstance(gid, int) and gid > 0

        # Get by question id
        row = repo.get_grading_by_question_id(qid)
        assert row is not None
        assert row[0] == gid
        assert row[2] == "B"
        assert row[3] == "A"

        # Get all by list
        rows = repo.get_all_gradings([qid])
        assert len(rows) == 1

        # Update grading
        repo.update_grading(gid, user_answer="A", real_answer="A", score="1/1",
                            correction_and_explanation="OK", additional_context="Updated")
        row2 = repo.get_grading_by_question_id(qid)
        assert row2[2] == "A"
        assert row2[4] == "1/1"
    finally:
        db.close()


def test_grading_invalid_inputs(tmp_path):
    db, qid = setup_db_with_question(tmp_path)
    try:
        repo = GradingRepository(db.conn)
        with pytest.raises(Exception):
            repo.get_all_gradings([qid, -1])
        with pytest.raises(Exception):
            repo.get_grading_by_question_id(0)
        with pytest.raises(Exception):
            repo.insert_grading(0, "A", "A", "1/1", "x", "y")
        with pytest.raises(Exception):
            repo.insert_grading(qid, "A", "", "1/1", "x", "y")
        with pytest.raises(Exception):
            repo.update_grading(0, "A", "A", "1/1", "x", "y")
    finally:
        db.close()


def test_grading_db_errors(tmp_path, monkeypatch):
    db, qid = setup_db_with_question(tmp_path)
    try:
        repo = GradingRepository(db.conn)

        class FailingCursor:
            def execute(self, *args, **kwargs):
                raise sqlite3.Error("boom")

        repo.cursor = FailingCursor()

        with pytest.raises(Exception) as exc1:
            repo.get_all_gradings([qid])
        assert "Failed to retrieve gradings" in str(exc1.value)

        with pytest.raises(Exception) as exc2:
            repo.get_grading_by_question_id(qid)
        assert "Failed to retrieve grading" in str(exc2.value)

        with pytest.raises(Exception) as exc3:
            repo.insert_grading(qid, "A", "A", "1/1", "x", "y")
        assert ("Failed to insert grading" in str(exc3.value)) or ("violates" in str(exc3.value))

        with pytest.raises(Exception) as exc4:
            repo.update_grading(1, "A", "A", "1/1", "x", "y")
        assert "Failed to update grading" in str(exc4.value)
    finally:
        db.close()
