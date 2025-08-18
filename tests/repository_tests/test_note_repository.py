import pytest
from repositories.my_db import MyDB
from repositories.note_repository import NoteRepository


def setup_db(tmp_path):
    db_file = tmp_path / "note.db"
    db = MyDB(db_path=str(db_file))
    db.connect()
    return db


def test_note_crud_and_queries(tmp_path):
    db = setup_db(tmp_path)
    try:
        repo = NoteRepository(db.conn)
        note_id = repo.insert_note("Title", "Content body")
        assert note_id > 0

        # get
        row = repo.get_note(note_id)
        assert row[0] == note_id
        assert row[1] == "Title"
        assert row[2] == "Content body"

        # list
        notes = repo.get_all_notes()
        assert any(n[0] == note_id for n in notes)

        # search
        assert "Title" in repo.get_all_note_names()
        assert any("Content" in c for c in repo.get_all_note_content())
        assert "Title" in repo.search_note_names("Tit")
        assert any("Content" in c for c in repo.search_note_content("Cont"))

        # delete
        deleted = repo.delete_note(note_id)
        assert deleted in (0, 1)
        assert repo.get_note(note_id) is None
    finally:
        db.close()


def test_note_invalid_inputs(tmp_path):
    db = setup_db(tmp_path)
    try:
        repo = NoteRepository(db.conn)
        with pytest.raises(Exception):
            repo.insert_note(" ", "content")
        with pytest.raises(Exception):
            repo.insert_note("title", " ")
        with pytest.raises(Exception):
            repo.get_note(0)
        with pytest.raises(Exception):
            repo.search_note_names(123)
        with pytest.raises(Exception):
            repo.search_note_content(123)
        with pytest.raises(Exception):
            repo.delete_note(-5)
    finally:
        db.close()


def test_note_repo_db_errors(tmp_path, monkeypatch):
    db = setup_db(tmp_path)
    try:
        repo = NoteRepository(db.conn)

        class FailingCursor:
            def execute(self, *args, **kwargs):
                import sqlite3
                raise sqlite3.Error("boom")

        repo.cursor = FailingCursor()

        with pytest.raises(Exception) as exc1:
            repo.get_all_notes()
        assert "Failed to retrieve notes" in str(exc1.value)

        with pytest.raises(Exception) as exc2:
            repo.get_note(1)
        assert "Failed to retrieve note" in str(exc2.value)

        with pytest.raises(Exception) as exc3:
            repo.insert_note("t", "c")
        assert ("Failed to insert note" in str(exc3.value)) or ("violates" in str(exc3.value))

        with pytest.raises(Exception) as exc4:
            repo.delete_note(1)
        assert "Failed to delete note" in str(exc4.value)

        with pytest.raises(Exception):
            repo.get_all_note_names()
        with pytest.raises(Exception):
            repo.get_all_note_content()
        with pytest.raises(Exception):
            repo.search_note_names("x")
        with pytest.raises(Exception):
            repo.search_note_content("x")
    finally:
        db.close()
