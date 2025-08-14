import sqlite3
import logging
import traceback
import os

class MyDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use data directory if it exists, otherwise use current directory
            data_dir = "data"
            if os.path.exists(data_dir) or os.getenv('DOCKER_ENV'):
                self.db_path = os.path.join(data_dir, "my_app_database.db")
            else:
                self.db_path = "my_app_database.db"
        else:
            self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON;")
            self._initialize_schema()
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {traceback.format_exc()}")
            raise Exception(f"Failed to connect to database: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during database connection: {traceback.format_exc()}")
            raise Exception(f"Unexpected error during database connection: {str(e)}")

    def _initialize_schema(self):
        try:
            # Create api_key table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_key (
                    api_key_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key TEXT NOT NULL,
                    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create note table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS note (
                    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_name TEXT NOT NULL,
                    note_content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create note_hashtag table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS note_hashtag (
                    note_hashtag_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hashtag TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create note_note_hashtags junction table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS note_note_hashtags (
                    note_id INTEGER NOT NULL,
                    note_hashtag_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP DEFAULT NULL,
                    FOREIGN KEY (note_id) REFERENCES note (note_id) ON DELETE CASCADE,
                    FOREIGN KEY (note_hashtag_id) REFERENCES note_hashtag (note_hashtag_id) ON DELETE CASCADE,
                    PRIMARY KEY (note_id, note_hashtag_id)
                )
            """)
            
            # Create summary table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS summary (
                    summary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    summary TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES note (note_id) ON DELETE CASCADE
                )
            """)

            # Create question table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS question (
                    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    question_type TEXT NOT NULL,
                    preview_answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (note_id) REFERENCES note (note_id) ON DELETE CASCADE
                )
            """)

            # Create option table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS option (
                    option_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    option TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES question (question_id) ON DELETE CASCADE
                )
            """)

            # Create grading table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS grading (
                    grading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_id INTEGER NOT NULL,
                    user_answer TEXT,
                    real_answer TEXT NOT NULL,
                    score TEXT NOT NULL,
                    correction_and_explanation TEXT NOT NULL,
                    additional_context TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES question (question_id) ON DELETE CASCADE
                )
            """)
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            logging.error(f"Database schema initialization error: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize database schema: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error during schema initialization: {traceback.format_exc()}")
            raise Exception(f"Unexpected error during schema initialization: {str(e)}")

    def close(self):
        try:
            if self.conn:
                self.conn.close()
                print("데이터베이스 연결이 종료되었습니다.")
        except Exception as e:
            logging.error(f"Error closing database connection: {traceback.format_exc()}")
            print(f"Warning: Error closing database connection: {str(e)}")

    def __enter__(self):
        try:
            self.connect()
            return self
        except Exception as e:
            logging.error(f"Error in database context manager enter: {traceback.format_exc()}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except Exception as e:
            logging.error(f"Error in database context manager exit: {traceback.format_exc()}")
            # Don't raise in __exit__ to avoid masking the original exception