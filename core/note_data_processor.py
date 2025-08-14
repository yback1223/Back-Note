import logging
import traceback
from typing import Dict, Any, List, Tuple
from datetime import datetime


class NoteDataProcessor:

    def __init__(self, repositories: Dict[str, Any]):
        self.repositories = repositories
    
    def process_api_key(self, api_key: str) -> int:
        try:
            all_api_keys: List[Tuple[int, str, datetime]] = self.repositories["api_key_repository"].get_all_api_keys()
            
            api_key_id = 0
            for existing_api_key_id, api_key_value, last_used_at in all_api_keys:
                if api_key == api_key_value:
                    api_key_id = existing_api_key_id
                    self.repositories["api_key_repository"].update_api_key(api_key_id)
                    break
            else:
                api_key_id = self.repositories["api_key_repository"].insert_api_key(api_key)
            
            return api_key_id
            
        except Exception as e:
            logging.error(f"Error processing API key: {traceback.format_exc()}")
            raise Exception(f"Failed to process API key: {str(e)}")
    
    def process_note(self, note_name: str, note_content: str, note_tags: List[str]) -> int:
        try:
            note_id = self.repositories["note_repository"].insert_note(note_name, note_content)
            
            if note_tags:
                try:
                    self.repositories["note_hashtag_repository"].insert_note_hashtags(note_id, note_tags)
                except Exception as e:
                    logging.error(f"Error inserting note tags: {traceback.format_exc()}")
                    logging.warning(f"Note created but tags failed to insert: {str(e)}")
            
            return note_id
            
        except Exception as e:
            logging.error(f"Error processing note: {traceback.format_exc()}")
            raise Exception(f"Failed to process note: {str(e)}")
    
    def process_summary(self, note_id: int, summary: str) -> None:
        try:
            self.repositories["summary_repository"].insert_summary(note_id, summary)
        except Exception as e:
            logging.error(f"Error processing summary: {traceback.format_exc()}")
            raise Exception(f"Failed to process summary: {str(e)}")

    def process_quiz_questions(self, note_id: int, quiz_data: List[Dict[str, Any]]) -> Dict[str, int]:
        try:
            question_id_with_question: Dict[str, int] = {}
            
            for question in quiz_data:
                try:
                    question_id = self.repositories["question_repository"].insert_question(
                        note_id, 
                        question["question"], 
                        question["question_type"], 
                        question["answer"]
                    )
                    
                    if question.get("options"):
                        self.repositories["option_repository"].insert_options(question_id, question["options"])
                    
                    question_id_with_question[question["question"]] = question_id
                    
                except Exception as e:
                    logging.error(f"Error processing quiz question: {traceback.format_exc()}")
                    # Continue processing other questions
                    continue
            
            return question_id_with_question
            
        except Exception as e:
            logging.error(f"Error processing quiz questions: {traceback.format_exc()}")
            raise Exception(f"Failed to process quiz questions: {str(e)}")
    
    def validate_inputs(self, api_key: str, note_name: str, note_tags: List[str], 
                       note_content: str, quiz_structure: Dict[str, Any], model: str) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        if not note_name or not note_name.strip():
            raise ValueError("Note name cannot be empty")
        
        if not isinstance(note_tags, list):
            raise ValueError("Note tags must be a list")
        
        if not note_content or not note_content.strip():
            raise ValueError("Note content cannot be empty")
        
        if not isinstance(quiz_structure, dict):
            raise ValueError("Quiz structure must be a dictionary")
        
        if not model or not model.strip():
            raise ValueError("Model cannot be empty")
