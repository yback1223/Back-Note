from datetime import datetime
import sqlite3
import logging
import traceback

class QuestionRepository:
    def __init__(self, conn: sqlite3.Connection):
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Failed to initialize QuestionRepository: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize QuestionRepository: {str(e)}")

    def get_all_questions(self, note_id: int) -> list[tuple[int, int, datetime]]:
        try:
            if not isinstance(note_id, int) or note_id <= 0:
                raise ValueError("Invalid note ID")
            
            self.cursor.execute("SELECT * FROM question WHERE note_id = ?", (note_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Database error in get_all_questions: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve questions: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_all_questions: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving questions: {str(e)}")
    
    def get_question_by_id(self, question_id: int) -> tuple[int, int, str, str, str, datetime]:
        try:
            if not isinstance(question_id, int) or question_id <= 0:
                raise ValueError("Invalid question ID")
            
            self.cursor.execute("SELECT * FROM question WHERE question_id = ?", (question_id,))
            result = self.cursor.fetchone()
            
            if not result:
                logging.warning(f"No question found with ID {question_id}")
            
            return result
        except sqlite3.Error as e:
            logging.error(f"Database error in get_question_by_id: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve question: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_question_by_id: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving question: {str(e)}")

    def insert_question(self, note_id: int, question: str, question_type: str, preview_answer: str) -> int:
        try:
            # Input validation
            if not isinstance(note_id, int) or note_id <= 0:
                raise ValueError("Invalid note ID")
            
            if not isinstance(question, str) or not question.strip():
                raise ValueError("Question cannot be empty")
            
            if not isinstance(question_type, str) or not question_type.strip():
                raise ValueError("Question type cannot be empty")
            
            if not isinstance(preview_answer, str) or not preview_answer.strip():
                raise ValueError("Preview answer cannot be empty")
            
            # Validate question_type
            valid_types = ["multiple_choice", "short_answer", "essay"]
            if question_type not in valid_types:
                raise ValueError(f"Invalid question type. Must be one of: {valid_types}")
            
            self.cursor.execute(
                "INSERT INTO question (note_id, question, question_type, preview_answer) VALUES (?, ?, ?, ?)", 
                (note_id, question, question_type, preview_answer)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logging.error(f"Integrity error in insert_question: {traceback.format_exc()}")
            raise Exception(f"Question violates database constraints: {str(e)}")
        except sqlite3.Error as e:
            logging.error(f"Database error in insert_question: {traceback.format_exc()}")
            raise Exception(f"Failed to insert question: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in insert_question: {traceback.format_exc()}")
            raise Exception(f"Unexpected error inserting question: {str(e)}")