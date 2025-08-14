import json
import logging
import traceback
from typing import Any, Tuple, Dict, List
from .gemini_work import GeminiWork
from .quiz_prompt_builder import QuizPromptBuilder
from .quiz_result_validator import QuizResultValidator
from .text_cleaner import TextCleaner
from .api_retry_handler import APIRetryHandler


class SubmitQuiz:
    
    def __init__(self, repositories: Dict[str, Any]):
        try:
            if not repositories:
                raise ValueError("Repositories dictionary cannot be empty")
            
            self.repositories = repositories
            
        except Exception as e:
            logging.error(f"Failed to initialize SubmitQuiz: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize SubmitQuiz: {str(e)}")

    def submit_quiz(self, api_key: str, quiz: List[Dict[str, Any]], model: str = "gemini-2.5-pro") -> Tuple[Dict[str, Any], Dict[str, Any]]:

        try:
            self._validate_inputs(api_key, quiz, model)
            
            if not GeminiWork.validate_api_key(api_key):
                raise ValueError("Invalid API key format")
            
            full_prompt_for_quiz = QuizPromptBuilder.create_submit_quiz_prompt(quiz)
            full_prompt_json_for_quiz = json.loads(full_prompt_for_quiz)
            
            result = APIRetryHandler.call_gemini_with_retry(
                api_key=api_key,
                prompt=full_prompt_for_quiz,
                model=model
            )
            
            result_json = QuizResultValidator.validate_gemini_response(result, len(quiz))
            
            result_json = TextCleaner.clean_quiz_result(result_json)
            
            QuizResultValidator.save_result_to_file(result_json)
            
            return full_prompt_json_for_quiz, result_json
            
        except Exception as e:
            logging.error(f"Error in submit_quiz: {traceback.format_exc()}")
            raise Exception(f"Failed to submit quiz: {str(e)}")
    
    def _validate_inputs(self, api_key: str, quiz: List[Dict[str, Any]], model: str) -> None:

        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        
        if not isinstance(quiz, list):
            raise ValueError("Quiz must be a list")
        
        if not quiz:
            raise ValueError("Quiz cannot be empty")
        
        if not model or not model.strip():
            raise ValueError("Model cannot be empty")
    
    def validate_quiz_structure(self, quiz: List[Dict[str, Any]]) -> bool:

        return QuizResultValidator.validate_quiz_structure(quiz)
    