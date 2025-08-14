import sqlite3
from datetime import datetime
import logging
import traceback

class SummaryRepository:
    def __init__(self, conn: sqlite3.Connection):
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Failed to initialize SummaryRepository: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize SummaryRepository: {str(e)}")

    def get_summary_by_id(self, summary_id: int) -> tuple[int, int, str, datetime]:
        try:
            self.cursor.execute("SELECT * FROM summary WHERE summary_id = ?", (summary_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Database error in get_summary_by_id: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve summary: {str(e)}")

    def get_summary_by_note_id(self, note_id: int) -> list[tuple[int, int, str, datetime]]:
        try:
            self.cursor.execute("SELECT * FROM summary WHERE note_id = ?", (note_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error in get_summary_by_note_id: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve summary: {str(e)}")

    def insert_summary(self, note_id: int, summary: str) -> int:
        try:
            if not isinstance(note_id, int) or note_id <= 0:
                raise ValueError("Invalid note ID")
            
            if not isinstance(summary, str) or not summary.strip():
                raise ValueError("Summary cannot be empty")
            
            self.cursor.execute("INSERT INTO summary (note_id, summary) VALUES (?, ?)", (note_id, summary))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logging.error(f"Integrity error in insert_summary: {traceback.format_exc()}")
            raise Exception(f"Summary violates database constraints: {str(e)}")
        except sqlite3.Error as e:
            logging.error(f"Database error in insert_summary: {traceback.format_exc()}")
            raise Exception(f"Failed to insert summary: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in insert_summary: {traceback.format_exc()}")
            raise Exception(f"Unexpected error inserting summary: {str(e)}")