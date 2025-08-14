import sqlite3
from datetime import datetime
import logging
import traceback

class GradingRepository:
    def __init__(self, conn: sqlite3.Connection):
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Failed to initialize GradingRepository: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize GradingRepository: {str(e)}")

    def get_all_gradings(self, question_ids: list[int]) -> list[tuple[int, int, str, str, str, str, datetime]]:
        try:
            if not question_ids:
                return []
            
            if not all(isinstance(qid, int) and qid > 0 for qid in question_ids):
                raise ValueError("All question IDs must be positive integers")
            
            placeholders = ','.join('?' * len(question_ids))
            self.cursor.execute(f"SELECT * FROM grading WHERE question_id IN ({placeholders})", question_ids)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error in get_all_gradings: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve gradings: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_all_gradings: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving gradings: {str(e)}")
    
    def get_grading_by_question_id(self, question_id: int) -> tuple[int, int, str, str, str, str, datetime]:
        try:
            if not isinstance(question_id, int) or question_id <= 0:
                raise ValueError("Invalid question ID")
            
            self.cursor.execute("SELECT * FROM grading WHERE question_id = ?", (question_id,))
            result = self.cursor.fetchone()
            
            if not result:
                logging.warning(f"No grading found for question ID {question_id}")
            
            return result
        except sqlite3.Error as e:
            logging.error(f"Database error in get_grading_by_question_id: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve grading: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_grading_by_question_id: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving grading: {str(e)}")

    def insert_grading(self, question_id: int, user_answer: str, real_answer: str, score: str, correction_and_explanation: str, additional_context: str) -> int:
        try:
            # Input validation
            if not isinstance(question_id, int) or question_id <= 0:
                raise ValueError("Invalid question ID")
            
            if not real_answer or not real_answer.strip():
                raise ValueError("Real answer cannot be empty")
            
            if not score or not score.strip():
                raise ValueError("Score cannot be empty")
            
            if not correction_and_explanation or not correction_and_explanation.strip():
                raise ValueError("Correction and explanation cannot be empty")
            
            if not additional_context or not additional_context.strip():
                raise ValueError("Additional context cannot be empty")
            
            self.cursor.execute(
                "INSERT INTO grading (question_id, user_answer, real_answer, score, correction_and_explanation, additional_context) VALUES (?, ?, ?, ?, ?, ?)", 
                (question_id, user_answer, real_answer, score, correction_and_explanation, additional_context)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logging.error(f"Integrity error in insert_grading: {traceback.format_exc()}")
            raise Exception(f"Grading violates database constraints: {str(e)}")
        except sqlite3.Error as e:
            logging.error(f"Database error in insert_grading: {traceback.format_exc()}")
            raise Exception(f"Failed to insert grading: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in insert_grading: {traceback.format_exc()}")
            raise Exception(f"Unexpected error inserting grading: {str(e)}")
    
    def update_grading(self, grading_id: int, user_answer: str, real_answer: str, score: str, correction_and_explanation: str, additional_context: str):
        try:
            # Input validation
            if not isinstance(grading_id, int) or grading_id <= 0:
                raise ValueError("Invalid grading ID")
            
            if not real_answer or not real_answer.strip():
                raise ValueError("Real answer cannot be empty")
            
            if not score or not score.strip():
                raise ValueError("Score cannot be empty")
            
            if not correction_and_explanation or not correction_and_explanation.strip():
                raise ValueError("Correction and explanation cannot be empty")
            
            if not additional_context or not additional_context.strip():
                raise ValueError("Additional context cannot be empty")
            
            self.cursor.execute(
                "UPDATE grading SET user_answer = ?, real_answer = ?, score = ?, correction_and_explanation = ?, additional_context = ? WHERE grading_id = ?", 
                (user_answer, real_answer, score, correction_and_explanation, additional_context, grading_id)
            )
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                logging.warning(f"No grading found with ID {grading_id} for update")
        except sqlite3.Error as e:
            logging.error(f"Database error in update_grading: {traceback.format_exc()}")
            raise Exception(f"Failed to update grading: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in update_grading: {traceback.format_exc()}")
            raise Exception(f"Unexpected error updating grading: {str(e)}")