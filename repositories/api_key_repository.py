from datetime import datetime
import sqlite3
import logging
import traceback

class ApiKeyRepository:
    def __init__(self, conn: sqlite3.Connection):
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Failed to initialize ApiKeyRepository: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize ApiKeyRepository: {str(e)}")

    def get_all_api_keys(self) -> list[tuple[int, str, datetime]]:
        try:
            self.cursor.execute("SELECT api_key_id, api_key, last_used_at FROM api_key ORDER BY last_used_at DESC")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error in get_all_api_keys: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve API keys: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_all_api_keys: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving API keys: {str(e)}")
    
    def insert_api_key(self, api_key: str, last_used_at: datetime = datetime.now()):
        try:
            if not api_key or not api_key.strip():
                raise ValueError("API key cannot be empty")
            
            self.cursor.execute("INSERT INTO api_key (api_key, last_used_at) VALUES (?, ?)", (api_key, last_used_at))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logging.error(f"Integrity error in insert_api_key: {traceback.format_exc()}")
            raise Exception(f"API key already exists or violates constraints: {str(e)}")
        except sqlite3.Error as e:
            logging.error(f"Database error in insert_api_key: {traceback.format_exc()}")
            raise Exception(f"Failed to insert API key: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in insert_api_key: {traceback.format_exc()}")
            raise Exception(f"Unexpected error inserting API key: {str(e)}")
    
    def update_api_key(self, api_key_id: int, last_used_at: datetime = datetime.now()):
        try:
            if not isinstance(api_key_id, int) or api_key_id <= 0:
                raise ValueError("Invalid API key ID")
            
            self.cursor.execute("UPDATE api_key SET last_used_at = ? WHERE api_key_id = ?", (last_used_at, api_key_id))
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                logging.warning(f"No API key found with ID {api_key_id} for update")
        except sqlite3.Error as e:
            logging.error(f"Database error in update_api_key: {traceback.format_exc()}")
            raise Exception(f"Failed to update API key: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in update_api_key: {traceback.format_exc()}")
            raise Exception(f"Unexpected error updating API key: {str(e)}")
    
    def delete_api_key(self, api_key_id: int):
        try:
            if not isinstance(api_key_id, int) or api_key_id <= 0:
                raise ValueError("Invalid API key ID")
            
            self.cursor.execute("DELETE FROM api_key WHERE api_key_id = ?", (api_key_id,))
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                logging.warning(f"No API key found with ID {api_key_id} for deletion")
            
            return self.cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"Database error in delete_api_key: {traceback.format_exc()}")
            raise Exception(f"Failed to delete API key: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in delete_api_key: {traceback.format_exc()}")
            raise Exception(f"Unexpected error deleting API key: {str(e)}")