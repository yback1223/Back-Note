import pytest
from repositories.my_db import MyDB
from repositories.summary_repository import SummaryRepository


def setup_db_with_note(tmp_path):
    db_file = tmp_path / "summary.db"
    db = MyDB(db_path=str(db_file))
    db.connect()
    c = db.cursor
    c.execute("INSERT INTO note (note_name, note_content) VALUES (?, ?)", ("Note", "Content"))
    note_id = c.lastrowid
    db.conn.commit()
    return db, note_id


def test_summary_insert_and_get(tmp_path):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = SummaryRepository(db.conn)
        sid = repo.insert_summary(note_id, "This is a summary")
        assert sid > 0

        by_id = repo.get_summary_by_id(sid)
        assert by_id is not None
        assert by_id[0] == sid

        by_note = repo.get_summary_by_note_id(note_id)
        assert any(row[0] == sid for row in by_note)
    finally:
        db.close()


def test_summary_invalid_inputs(tmp_path):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = SummaryRepository(db.conn)
        with pytest.raises(Exception):
            repo.insert_summary(0, "abc")
        with pytest.raises(Exception):
            repo.insert_summary(note_id, " ")
    finally:
        db.close()


def test_summary_repo_db_errors(tmp_path, monkeypatch):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = SummaryRepository(db.conn)

        class FailingCursor:
            def execute(self, *args, **kwargs):
                import sqlite3
                raise sqlite3.Error("boom")

        repo.cursor = FailingCursor()

        with pytest.raises(Exception) as exc1:
            repo.get_summary_by_id(1)
        assert "Failed to retrieve summary" in str(exc1.value)

        with pytest.raises(Exception) as exc2:
            repo.get_summary_by_note_id(note_id)
        assert "Failed to retrieve summary" in str(exc2.value)

        with pytest.raises(Exception) as exc3:
            repo.insert_summary(note_id, "s")
        assert ("Failed to insert summary" in str(exc3.value)) or ("violates" in str(exc3.value))
    finally:
        db.close()
