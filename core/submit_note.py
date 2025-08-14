import json
import logging
import traceback
from typing import Any, Tuple, Dict
from .gemini_work import GeminiWork
from .note_prompt_builder import NotePromptBuilder
from .note_result_validator import NoteResultValidator
from .note_data_processor import NoteDataProcessor
from .api_retry_handler import APIRetryHandler
from .text_cleaner import TextCleaner


class SubmitNote:
    
    def __init__(self, repositories: Dict[str, Any]):

        try:
            if not repositories:
                raise ValueError("Repositories dictionary cannot be empty")
            
            required_repos = ["api_key_repository", "note_repository", "note_hashtag_repository", 
                            "question_repository", "option_repository", "summary_repository"]
            
            for repo_name in required_repos:
                if repo_name not in repositories:
                    raise ValueError(f"Required repository '{repo_name}' not found")
            
            self.repositories = repositories
            self.data_processor = NoteDataProcessor(repositories)
            
        except Exception as e:
            logging.error(f"Failed to initialize SubmitNote: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize SubmitNote: {str(e)}")

    def submit_note(self, api_key: str, note_name: str, note_tags: list[str], 
                   note_content: str, quiz_structure: dict, model: str = "gemini-2.5-pro") -> Tuple[dict, dict, Dict[str, int]]:

        try:
            self.data_processor.validate_inputs(api_key, note_name, note_tags, note_content, quiz_structure, model)
            
            if not GeminiWork.validate_api_key(api_key):
                raise ValueError("Invalid API key format")
            
            self.data_processor.process_api_key(api_key)
            
            note_id = self.data_processor.process_note(note_name, note_content, note_tags)
            
            full_prompt = NotePromptBuilder.create_submit_note_prompt(note_content, quiz_structure)
            full_prompt_json = json.loads(full_prompt)
            
            result = APIRetryHandler.call_gemini_with_retry(
                api_key=api_key,
                prompt=full_prompt,
                model=model
            )
            
            result_json = NoteResultValidator.validate_gemini_response(result)
            
            result_json = TextCleaner.clean_quiz_result(result_json)
            
            NoteResultValidator.save_result_to_file(result_json)
            
            self.data_processor.process_summary(note_id, result_json.get("summary", ""))
            
            question_id_with_question = self.data_processor.process_quiz_questions(
                note_id, result_json.get("quiz", [])
            )
            
            return full_prompt_json, result_json, question_id_with_question
            
        except Exception as e:
            logging.error(f"Error in submit_note: {traceback.format_exc()}")
            raise Exception(f"Failed to submit note: {str(e)}")