import os
import sqlite3
import pytest
from typing import List
from repositories.my_db import MyDB


def _get_table_names(cursor: sqlite3.Cursor) -> List[str]:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    return [row[0] for row in cursor.fetchall()]


def _count_rows(cursor: sqlite3.Cursor, table: str) -> int:
    cursor.execute(f"SELECT COUNT(*) FROM {table};")
    return cursor.fetchone()[0]


class TestMyDBPathResolution:
    def test_default_path_without_data_dir_and_without_docker_env(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("DOCKER_ENV", raising=False)
        db = MyDB()
        assert db.db_path == "my_app_database.db"

    def test_path_uses_data_dir_when_exists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "data").mkdir(parents=True, exist_ok=True)
        monkeypatch.delenv("DOCKER_ENV", raising=False)
        db = MyDB()
        assert os.path.normpath(db.db_path) == os.path.normpath(os.path.join("data", "my_app_database.db"))

    def test_path_uses_data_dir_when_docker_env_set(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("DOCKER_ENV", "true")
        db = MyDB()
        assert os.path.normpath(db.db_path) == os.path.normpath(os.path.join("data", "my_app_database.db"))


class TestMyDBSchema:
    def test_connect_creates_all_tables(self, tmp_path):
        db_file = tmp_path / "test_schema.db"
        db = MyDB(db_path=str(db_file))
        db.connect()
        try:
            tables = _get_table_names(db.cursor)
            expected = [
                "api_key",
                "grading",
                "note",
                "note_hashtag",
                "note_note_hashtags",
                "option",
                "question",
                "summary",
            ]
            for table in expected:
                assert table in tables, f"Missing table: {table}"
        finally:
            db.close()

    def test_foreign_keys_cascade_on_delete(self, tmp_path):
        db_file = tmp_path / "test_fk.db"
        db = MyDB(db_path=str(db_file))
        db.connect()
        try:
            c = db.cursor
            # Insert a note
            c.execute("INSERT INTO note (note_name, note_content) VALUES (?, ?)", ("Note 1", "Content"))
            note_id = c.lastrowid

            # Insert hashtag and link
            c.execute("INSERT INTO note_hashtag (hashtag) VALUES (?)", ("tag1",))
            hashtag_id = c.lastrowid
            c.execute(
                "INSERT INTO note_note_hashtags (note_id, note_hashtag_id) VALUES (?, ?)",
                (note_id, hashtag_id),
            )

            # Insert question -> option & grading
            c.execute(
                "INSERT INTO question (note_id, question, question_type, preview_answer) VALUES (?, ?, ?, ?)",
                (note_id, "Q?", "multiple_choice", "A"),
            )
            question_id = c.lastrowid

            c.execute(
                "INSERT INTO option (question_id, option) VALUES (?, ?)",
                (question_id, "Option A"),
            )
            c.execute(
                """
                INSERT INTO grading (question_id, user_answer, real_answer, score, correction_and_explanation, additional_context)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (question_id, "A", "A", "1/1", "OK", "ctx"),
            )
            db.conn.commit()

            # Sanity counts before delete
            assert _count_rows(c, "note") == 1
            assert _count_rows(c, "note_note_hashtags") == 1
            assert _count_rows(c, "question") == 1
            assert _count_rows(c, "option") == 1
            assert _count_rows(c, "grading") == 1

            # Delete the note and ensure cascades remove dependents
            c.execute("DELETE FROM note WHERE note_id = ?", (note_id,))
            db.conn.commit()

            assert _count_rows(c, "note") == 0
            assert _count_rows(c, "note_note_hashtags") == 0
            assert _count_rows(c, "question") == 0
            assert _count_rows(c, "option") == 0
            assert _count_rows(c, "grading") == 0
        finally:
            db.close()


class TestMyDBContextManagerAndErrors:
    def test_context_manager_closes_connection_and_prints_message(self, tmp_path, capsys):
        db_file = tmp_path / "ctx.db"
        with MyDB(db_path=str(db_file)) as db:
            assert db.conn is not None
            assert db.cursor is not None
        captured = capsys.readouterr()
        assert "데이터베이스 연결이 종료되었습니다." in captured.out

    def test_connect_sqlite_error_raises_exception(self, tmp_path, monkeypatch):
        db_file = tmp_path / "err.db"

        def _raise_error(*args, **kwargs):
            raise sqlite3.Error("boom")

        monkeypatch.setattr(sqlite3, "connect", _raise_error)
        db = MyDB(db_path=str(db_file))
        with pytest.raises(Exception) as exc:
            db.connect()
        assert "Failed to connect to database" in str(exc.value)

    def test_initialize_schema_error_raises_exception(self, tmp_path):
        db_file = tmp_path / "schema_err.db"
        db = MyDB(db_path=str(db_file))
        # Create a real connection, then swap in a failing cursor
        db.conn = sqlite3.connect(str(db_file))
        class FailingCursor:
            def execute(self, *args, **kwargs):
                raise sqlite3.Error("schema fail")
        db.cursor = FailingCursor()
        with pytest.raises(Exception) as exc:
            db._initialize_schema()
        assert "Failed to initialize database schema" in str(exc.value)
        # Clean up
        try:
            db.conn.close()
        except Exception:
            pass
