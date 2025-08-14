import json
import logging
import traceback
from typing import Dict, Any


class NoteResultValidator:

    @staticmethod
    def validate_gemini_response(result: str) -> Dict[str, Any]:

        try:
            # Parse JSON result
            try:
                result_json = json.loads(result)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON result: {str(e)}")
                raise Exception(f"Invalid JSON response from Gemini: {str(e)}")
            
            # Validate basic structure
            NoteResultValidator._validate_basic_structure(result_json)
            
            # Validate quiz structure
            NoteResultValidator._validate_quiz_structure(result_json)
            
            return result_json
            
        except Exception as e:
            logging.error(f"Error validating Gemini response: {traceback.format_exc()}")
            raise Exception(f"Failed to validate Gemini response: {str(e)}")
    
    @staticmethod
    def _validate_basic_structure(result_json: Dict[str, Any]) -> None:

        if not result_json.get("summary"):
            raise Exception("Missing 'summary' in Gemini response")
        
        if not result_json.get("quiz"):
            raise Exception("Missing 'quiz' in Gemini response")
        
        if not isinstance(result_json["quiz"], list):
            raise Exception("'quiz' must be a list")
    
    @staticmethod
    def _validate_quiz_structure(result_json: Dict[str, Any]) -> None:
        quiz_list = result_json.get("quiz", [])
        
        for i, quiz_item in enumerate(quiz_list):
            if not isinstance(quiz_item, dict):
                raise Exception(f"Quiz item {i} must be a dictionary")
            
            # Check required fields
            required_fields = ["question_type", "question", "answer"]
            for field in required_fields:
                if field not in quiz_item:
                    raise Exception(f"Quiz item {i} missing required field: {field}")
            
            # Validate question type
            valid_types = ["multiple_choice", "short_answer", "long_answer"]
            if quiz_item["question_type"] not in valid_types:
                raise Exception(f"Quiz item {i} has invalid question_type: {quiz_item['question_type']}")
            
            # Validate multiple choice questions
            if quiz_item["question_type"] == "multiple_choice":
                if "options" not in quiz_item or not isinstance(quiz_item["options"], list):
                    raise Exception(f"Quiz item {i} missing or invalid options for multiple choice")
                
                if len(quiz_item["options"]) < 2:
                    raise Exception(f"Quiz item {i} must have at least 2 options for multiple choice")
    
    @staticmethod
    def save_result_to_file(result_json: Dict[str, Any], filename: str = "result_for_note.json") -> None:

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result_json, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving result to file: {traceback.format_exc()}")
            # Don't fail the operation if file save fails
            logging.warning(f"Note processed but failed to save result file: {str(e)}")
