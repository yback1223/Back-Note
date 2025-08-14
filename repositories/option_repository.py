import sqlite3
from datetime import datetime
import logging
import traceback

class OptionRepository:
    def __init__(self, conn: sqlite3.Connection):
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Failed to initialize OptionRepository: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize OptionRepository: {str(e)}")

    def get_all_options(self, question_ids: list[int]) -> list[tuple[int, int, str, datetime]]:
        try:
            if not question_ids:
                return []
            
            if not all(isinstance(qid, int) and qid > 0 for qid in question_ids):
                raise ValueError("All question IDs must be positive integers")
            
            placeholders = ','.join('?' * len(question_ids))
            self.cursor.execute(f"SELECT * FROM option WHERE question_id IN ({placeholders})", question_ids)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error in get_all_options: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve options: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_all_options: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving options: {str(e)}")
    
    def get_options_by_question_id(self, question_id: int) -> list[tuple[int, int, str, datetime]]:
        """Get options for a specific question"""
        try:
            if not isinstance(question_id, int) or question_id <= 0:
                raise ValueError("Invalid question ID")
            
            self.cursor.execute("SELECT * FROM option WHERE question_id = ?", (question_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error in get_options_by_question_id: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve options for question: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_options_by_question_id: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving options for question: {str(e)}")
    
    def insert_options(self, question_id: int, options: list[str]) -> None:
        try:
            # Input validation
            if not isinstance(question_id, int) or question_id <= 0:
                raise ValueError("Invalid question ID")
            
            if not isinstance(options, list):
                raise ValueError("Options must be a list")
            
            if not options:
                logging.info(f"No options to insert for question ID {question_id}")
                return
            
            # Validate each option
            valid_options = []
            for option in options:
                if isinstance(option, str) and option.strip():
                    valid_options.append(option.strip())
                else:
                    logging.warning(f"Skipping invalid option: {option}")
            
            if not valid_options:
                logging.warning(f"No valid options to insert for question ID {question_id}")
                return
            
            self.cursor.executemany(
                "INSERT INTO option (question_id, option) VALUES (?, ?)", 
                [(question_id, option) for option in valid_options]
            )
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            logging.error(f"Integrity error in insert_options: {traceback.format_exc()}")
            raise Exception(f"Options violate database constraints: {str(e)}")
        except sqlite3.Error as e:
            logging.error(f"Database error in insert_options: {traceback.format_exc()}")
            raise Exception(f"Failed to insert options: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in insert_options: {traceback.format_exc()}")
            raise Exception(f"Unexpected error inserting options: {str(e)}")