import pytest
from repositories.my_db import MyDB
from repositories.option_repository import OptionRepository


def setup_db_with_question(tmp_path):
    db_file = tmp_path / "option.db"
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


def test_option_insert_and_get(tmp_path):
    db, qid = setup_db_with_question(tmp_path)
    try:
        repo = OptionRepository(db.conn)
        repo.insert_options(qid, ["A", "B", " ", None])
        opts = repo.get_options_by_question_id(qid)
        assert len(opts) == 2

        all_opts = repo.get_all_options([qid])
        assert len(all_opts) == 2

        assert repo.get_all_options([]) == []
    finally:
        db.close()


def test_option_invalid_inputs(tmp_path):
    db, qid = setup_db_with_question(tmp_path)
    try:
        repo = OptionRepository(db.conn)
        with pytest.raises(Exception):
            repo.get_options_by_question_id(0)
        with pytest.raises(Exception):
            repo.get_all_options([qid, -1])
        with pytest.raises(Exception):
            repo.insert_options(0, ["A"])  # invalid question id
        with pytest.raises(Exception):
            repo.insert_options(qid, "not-a-list")
    finally:
        db.close()


def test_option_repo_db_errors(tmp_path, monkeypatch):
    db, qid = setup_db_with_question(tmp_path)
    try:
        repo = OptionRepository(db.conn)

        class FailingCursor:
            def execute(self, *args, **kwargs):
                import sqlite3
                raise sqlite3.Error("boom")
            def executemany(self, *args, **kwargs):
                import sqlite3
                raise sqlite3.Error("boom")

        repo.cursor = FailingCursor()

        with pytest.raises(Exception) as exc1:
            repo.get_all_options([qid])
        assert "Failed to retrieve options" in str(exc1.value)

        with pytest.raises(Exception) as exc2:
            repo.get_options_by_question_id(qid)
        assert "Failed to retrieve options for question" in str(exc2.value)

        with pytest.raises(Exception) as exc3:
            repo.insert_options(qid, ["A", "B"]) 
        assert ("Failed to insert options" in str(exc3.value)) or ("violates" in str(exc3.value))
    finally:
        db.close()
