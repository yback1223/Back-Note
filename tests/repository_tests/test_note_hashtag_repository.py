import pytest
from repositories.my_db import MyDB
from repositories.note_hashtag_repository import NoteHashtagRepository


def setup_db_with_note(tmp_path):
    db_file = tmp_path / "note_hashtag.db"
    db = MyDB(db_path=str(db_file))
    db.connect()
    c = db.cursor
    c.execute("INSERT INTO note (note_name, note_content) VALUES (?, ?)", ("Note", "Content"))
    note_id = c.lastrowid
    db.conn.commit()
    return db, note_id


def test_hashtag_insert_list_delete_search(tmp_path):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = NoteHashtagRepository(db.conn)
        repo.insert_note_hashtags(note_id, ["tag1", "tag2", "", None])

        tags = repo.get_hashtags_by_note_id(note_id)
        assert set(tags) == {"tag1", "tag2"}

        all_tags = repo.get_all_hashtags()
        assert set(all_tags) >= {"tag1", "tag2"}

        suggestions = repo.search_hashtags("tag")
        assert "tag1" in suggestions

        # soft delete tag1
        assert repo.delete_hashtag_from_note(note_id, "tag1") in (True, False)
        tags2 = repo.get_hashtags_by_note_id(note_id)
        assert "tag1" not in tags2
    finally:
        db.close()


def test_hashtag_invalid_inputs(tmp_path):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = NoteHashtagRepository(db.conn)
        with pytest.raises(Exception):
            repo.insert_note_hashtags(0, ["t"]) 
        with pytest.raises(Exception):
            repo.insert_note_hashtags(note_id, "not-a-list")
        with pytest.raises(Exception):
            repo.get_hashtags_by_note_id(0)
        with pytest.raises(Exception):
            repo.search_hashtags(123)
        with pytest.raises(Exception):
            repo.delete_hashtag_from_note(note_id, " ")
    finally:
        db.close()


def test_note_hashtag_db_errors(tmp_path, monkeypatch):
    db, note_id = setup_db_with_note(tmp_path)
    try:
        repo = NoteHashtagRepository(db.conn)

        class FailingCursor:
            def execute(self, *args, **kwargs):
                import sqlite3
                raise sqlite3.Error("boom")

        # insert_note_hashtags swallows per-hashtag DB errors and continues (logs), so it should NOT raise
        original_cursor = repo.cursor
        repo.cursor = FailingCursor()
        repo.insert_note_hashtags(note_id, ["t1"])  # should not raise
        # restore working cursor to verify no data was inserted
        repo.cursor = original_cursor
        assert repo.get_hashtags_by_note_id(note_id) == []

        # For other methods, DB error should bubble up as wrapped Exception
        repo.cursor = FailingCursor()
        with pytest.raises(Exception) as exc2:
            repo.get_hashtags_by_note_id(note_id)
        assert "Failed to retrieve hashtags" in str(exc2.value)

        with pytest.raises(Exception) as exc3:
            repo.get_all_hashtags()
        assert "Failed to retrieve all hashtags" in str(exc3.value)

        with pytest.raises(Exception) as exc4:
            repo.search_hashtags("t")
        assert "Failed to search hashtags" in str(exc4.value)

        with pytest.raises(Exception) as exc5:
            repo.delete_hashtag_from_note(note_id, "t")
        assert "Failed to delete hashtag from note" in str(exc5.value)
    finally:
        db.close()
