import json
import logging
import traceback
from typing import Dict, Any, List


class QuizResultValidator:
    """Handles validation of quiz submission results from Gemini API"""
    
    @staticmethod
    def validate_gemini_response(result: str, expected_quiz_length: int) -> Dict[str, Any]:
        """
        Validate the response from Gemini API
        
        Args:
            result: Raw response string from Gemini
            expected_quiz_length: Expected number of quiz items
            
        Returns:
            Parsed and validated JSON response
            
        Raises:
            Exception: If validation fails
        """
        try:
            # Parse JSON result
            try:
                result_json = json.loads(result)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse JSON result: {str(e)}")
                raise Exception(f"Invalid JSON response from Gemini: {str(e)}")
            
            # Validate basic structure
            QuizResultValidator._validate_basic_structure(result_json)
            
            # Validate quiz structure
            QuizResultValidator._validate_quiz_structure(result_json, expected_quiz_length)
            
            return result_json
            
        except Exception as e:
            logging.error(f"Error validating Gemini response: {traceback.format_exc()}")
            raise Exception(f"Failed to validate Gemini response: {str(e)}")
    
    @staticmethod
    def _validate_basic_structure(result_json: Dict[str, Any]) -> None:
        """Validate the basic structure of the response"""
        if not result_json.get("quiz"):
            raise Exception("Missing 'quiz' in Gemini response")
        
        if not isinstance(result_json["quiz"], list):
            raise Exception("'quiz' must be a list")
    
    @staticmethod
    def _validate_quiz_structure(result_json: Dict[str, Any], expected_length: int) -> None:
        """Validate the quiz structure in the response"""
        quiz_list = result_json.get("quiz", [])
        
        # Check length
        if len(quiz_list) != expected_length:
            raise Exception(f"Expected {expected_length} quiz items, got {len(quiz_list)}")
        
        # Validate each quiz result item
        for i, quiz_result in enumerate(quiz_list):
            if not isinstance(quiz_result, dict):
                raise Exception(f"Quiz result item {i} must be a dictionary")
            
            # Check required fields
            required_fields = ["question", "user_answer", "real_answer", "score", 
                             "correction_and_explanation", "additional_context"]
            for field in required_fields:
                if field not in quiz_result:
                    raise Exception(f"Quiz result item {i} missing required field: {field}")
            
            # Validate score values
            valid_scores = ["Correct", "Partially Correct", "Incorrect"]
            if quiz_result["score"] not in valid_scores:
                raise Exception(f"Quiz result item {i} has invalid score: {quiz_result['score']}")
    
    @staticmethod
    def save_result_to_file(result_json: Dict[str, Any], filename: str = "result_for_quiz.json") -> None:
        """
        Save the validated result to a file
        
        Args:
            result_json: The validated result JSON
            filename: The filename to save to
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result_json, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving result to file: {traceback.format_exc()}")
            # Don't fail the operation if file save fails
            logging.warning(f"Quiz processed but failed to save result file: {str(e)}")
    
    @staticmethod
    def validate_quiz_structure(quiz: List[Dict[str, Any]]) -> bool:
        """
        Validate quiz structure before submission
        
        Args:
            quiz: List of quiz items to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            if not isinstance(quiz, list):
                return False
            
            if not quiz:
                return False
            
            for quiz_item in quiz:
                if not isinstance(quiz_item, dict):
                    return False
                
                if "question" not in quiz_item or "user_answer" not in quiz_item:
                    return False
                
                if not isinstance(quiz_item["question"], str) or not quiz_item["question"].strip():
                    return False
                
                if not isinstance(quiz_item["user_answer"], str):
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Quiz structure validation error: {traceback.format_exc()}")
            return False
