from datetime import datetime
import sqlite3
import logging
import traceback

class NoteRepository:
    def __init__(self, conn: sqlite3.Connection):
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Failed to initialize NoteRepository: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize NoteRepository: {str(e)}")

    def get_all_notes(self) -> list[tuple[int, int, str, str, datetime]]:
        try:
            self.cursor.execute("SELECT note_id, note_name, created_at FROM note")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error in get_all_notes: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve notes: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_all_notes: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving notes: {str(e)}")
    
    def get_all_note_names(self) -> list[str]:
        """Get all note names for autocomplete"""
        try:
            self.cursor.execute("SELECT note_name FROM note")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Database error in get_all_note_names: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve note names: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_all_note_names: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving note names: {str(e)}")
    
    def get_all_note_content(self) -> list[str]:
        """Get all note content for autocomplete"""
        try:
            self.cursor.execute("SELECT note_content FROM note")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Database error in get_all_note_content: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve note content: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_all_note_content: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving note content: {str(e)}")
    
    def search_note_names(self, search_term: str) -> list[str]:
        """Search note names by partial match for autocomplete"""
        try:
            if not isinstance(search_term, str):
                raise ValueError("Search term must be a string")
            
            if not search_term.strip():
                return []
            
            self.cursor.execute("SELECT note_name FROM note WHERE note_name LIKE ? LIMIT 10", (f"%{search_term}%",))
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Database error in search_note_names: {traceback.format_exc()}")
            raise Exception(f"Failed to search note names: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in search_note_names: {traceback.format_exc()}")
            raise Exception(f"Unexpected error searching note names: {str(e)}")
    
    def search_note_content(self, search_term: str) -> list[str]:
        """Search note content by partial match for autocomplete"""
        try:
            if not isinstance(search_term, str):
                raise ValueError("Search term must be a string")
            
            if not search_term.strip():
                return []
            
            self.cursor.execute("SELECT note_content FROM note WHERE note_content LIKE ? LIMIT 10", (f"%{search_term}%",))
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Database error in search_note_content: {traceback.format_exc()}")
            raise Exception(f"Failed to search note content: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in search_note_content: {traceback.format_exc()}")
            raise Exception(f"Unexpected error searching note content: {str(e)}")
    
    def get_note(self, note_id: int) -> tuple[int, int, str, str, datetime]:
        try:
            if not isinstance(note_id, int) or note_id <= 0:
                raise ValueError("Invalid note ID")
            
            self.cursor.execute("""
                SELECT note_id, note_name, note_content, created_at FROM note WHERE note_id = ?
            """, (note_id,))
            result = self.cursor.fetchone()
            
            if not result:
                logging.warning(f"No note found with ID {note_id}")
            
            return result
        except sqlite3.Error as e:
            logging.error(f"Database error in get_note: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve note: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_note: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving note: {str(e)}")

    def insert_note(self, note_name: str, note_content: str) -> int:
        try:
            # Input validation
            if not isinstance(note_name, str) or not note_name.strip():
                raise ValueError("Note name cannot be empty")
            
            if not isinstance(note_content, str) or not note_content.strip():
                raise ValueError("Note content cannot be empty")
            
            self.cursor.execute("INSERT INTO note (note_name, note_content) VALUES (?, ?)", (note_name, note_content))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logging.error(f"Integrity error in insert_note: {traceback.format_exc()}")
            raise Exception(f"Note violates database constraints: {str(e)}")
        except sqlite3.Error as e:
            logging.error(f"Database error in insert_note: {traceback.format_exc()}")
            raise Exception(f"Failed to insert note: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in insert_note: {traceback.format_exc()}")
            raise Exception(f"Unexpected error inserting note: {str(e)}")
    
    def delete_note(self, note_id: int) -> int:
        try:
            if not isinstance(note_id, int) or note_id <= 0:
                raise ValueError("Invalid note ID")
            
            self.cursor.execute("DELETE FROM note WHERE note_id = ?", (note_id,))
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                logging.warning(f"No note found with ID {note_id} for deletion")
            
            return self.cursor.rowcount
        except sqlite3.Error as e:
            logging.error(f"Database error in delete_note: {traceback.format_exc()}")
            raise Exception(f"Failed to delete note: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in delete_note: {traceback.format_exc()}")
            raise Exception(f"Unexpected error deleting note: {str(e)}")