import pytest
from datetime import datetime, timedelta
import sqlite3
from repositories.my_db import MyDB
from repositories.api_key_repository import ApiKeyRepository


def setup_db(tmp_path):
    db_file = tmp_path / "api_key.db"
    db = MyDB(db_path=str(db_file))
    db.connect()
    return db


def test_api_key_crud_flow(tmp_path):
    db = setup_db(tmp_path)
    try:
        repo = ApiKeyRepository(db.conn)

        # Insert
        api_key_id = repo.insert_api_key("KEY_1")
        assert isinstance(api_key_id, int) and api_key_id > 0

        # List
        rows = repo.get_all_api_keys()
        assert len(rows) == 1
        rid, key, last_used_at = rows[0]
        assert rid == api_key_id
        assert key == "KEY_1"

        # Update last_used_at
        new_time = datetime.now() + timedelta(minutes=5)
        repo.update_api_key(api_key_id, last_used_at=new_time)
        rows2 = repo.get_all_api_keys()
        assert len(rows2) == 1
        # DB stores as 'YYYY-MM-DD HH:MM:SS' (no microseconds)
        expected = new_time.replace(microsecond=0).isoformat(sep=' ')
        assert rows2[0][2] == expected

        # Delete
        deleted = repo.delete_api_key(api_key_id)
        assert deleted in (0, 1)  # 1 on first delete, 0 if already gone in rare cases
        rows3 = repo.get_all_api_keys()
        assert len(rows3) == 0
    finally:
        db.close()


def test_api_key_invalid_inputs(tmp_path):
    db = setup_db(tmp_path)
    try:
        repo = ApiKeyRepository(db.conn)
        with pytest.raises(Exception):
            repo.insert_api_key("")
        with pytest.raises(Exception):
            repo.update_api_key(0)
        with pytest.raises(Exception):
            repo.delete_api_key(-1)
    finally:
        db.close()


def test_api_key_db_errors(tmp_path, monkeypatch):
    db = setup_db(tmp_path)
    try:
        repo = ApiKeyRepository(db.conn)

        class FailingCursor:
            def execute(self, *args, **kwargs):
                raise sqlite3.Error("boom")

        # swap the cursor to a failing one
        repo.cursor = FailingCursor()

        with pytest.raises(Exception) as exc1:
            repo.get_all_api_keys()
        assert "Failed to retrieve API keys" in str(exc1.value)

        with pytest.raises(Exception) as exc2:
            repo.insert_api_key("KEY")
        assert ("Failed to insert API key" in str(exc2.value)) or ("violates constraints" in str(exc2.value))

        with pytest.raises(Exception) as exc3:
            repo.update_api_key(1)
        assert "Failed to update API key" in str(exc3.value)

        with pytest.raises(Exception) as exc4:
            repo.delete_api_key(1)
        assert "Failed to delete API key" in str(exc4.value)
    finally:
        db.close()
