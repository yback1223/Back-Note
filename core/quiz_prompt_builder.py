import json
import logging
import traceback
from typing import Dict, Any, List


class QuizPromptBuilder:
    """Handles the creation of prompts for quiz submission to Gemini API"""
    
    @staticmethod
    def create_submit_quiz_prompt(quiz: List[Dict[str, Any]]) -> str:
        """
        Create a structured prompt for quiz submission
        
        Args:
            quiz: List of quiz questions with user answers
            
        Returns:
            JSON string containing the formatted prompt
        """
        try:
            # Input validation
            if not isinstance(quiz, list):
                raise ValueError("Quiz must be a list")
            
            if not quiz:
                raise ValueError("Quiz cannot be empty")
            
            # Validate each quiz item
            QuizPromptBuilder._validate_quiz_items(quiz)
            
            prompt_data = QuizPromptBuilder._build_prompt_structure(quiz)
            return json.dumps(prompt_data, indent=4, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"Error creating submit quiz prompt: {traceback.format_exc()}")
            raise Exception(f"Failed to create submit quiz prompt: {str(e)}")
    
    @staticmethod
    def _validate_quiz_items(quiz: List[Dict[str, Any]]) -> None:
        """Validate each quiz item structure"""
        for i, quiz_item in enumerate(quiz):
            if not isinstance(quiz_item, dict):
                raise ValueError(f"Quiz item {i} must be a dictionary")
            
            required_fields = ["question", "user_answer"]
            for field in required_fields:
                if field not in quiz_item:
                    raise ValueError(f"Quiz item {i} missing required field: {field}")
            
            if not isinstance(quiz_item["question"], str) or not quiz_item["question"].strip():
                raise ValueError(f"Quiz item {i} question cannot be empty")
            
            if not isinstance(quiz_item["user_answer"], str):
                raise ValueError(f"Quiz item {i} user_answer must be a string")
    
    @staticmethod
    def _build_prompt_structure(quiz: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build the complete prompt structure"""
        return {
            "role": "You are a calm, clear, and informative AI Tutor. Your primary function is to provide constructive feedback on my answers to questions.",
            "input_description": "I will provide you with quiz questions with my answers. You will then evaluate my response.",
            "core_tasks": QuizPromptBuilder._get_core_tasks(),
            "example_of_output_format(the result should be a json)": QuizPromptBuilder._get_output_format_example(),
            "user_input": {
                "quiz_with_answers": quiz
            }
        }
    
    @staticmethod
    def _get_core_tasks() -> List[str]:
        """Get the list of core tasks for the AI"""
        return [
            "Score My Answer: Evaluate the correctness and completeness of my answer using one of the following qualitative assessments: 'Correct', 'Partially Correct', or 'Incorrect'.",
            "Provide Corrections (if needed): If my answer is not perfect, gently point out any inaccuracies or omissions. Clearly explain why it's incorrect or could be better, and then provide a well-explained, corrected version of the answer.",
            "Offer Additional Information/Context: Regardless of my answer's correctness, provide some relevant background information, interesting facts, or further explanations related to the topic of the question to help deepen my understanding.",
            "Ensure your feedback is always delivered in a patient, constructive, and easy-to-understand way. Focus on helping me learn.",
            "Return the result as a single JSON object with a top-level key named 'quiz'. The value of 'quiz' should be a list of dictionaries, just like the example.",
            "IMPORTANT: Do not include bracketed source citations in the output.",
            "YOUR OUTPUT SHOULD BE JSON FORMAT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
            "DO NOT SAY ANYTHING ELSE!!!!! JUST RETURN THE JSON FORMAT I ASKED FOR!!!!!!!!!!!!!"
        ]
    
    @staticmethod
    def _get_output_format_example() -> Dict[str, Any]:
        """Get the example output format"""
        return {
            "quiz": [
                {
                    "question": "string",
                    "options": ["array of strings if question_type is multiple_choice otherwise blank array"],
                    "user_answer": "string",
                    "real_answer": "string",
                    "score": "string (e.g., 'Correct', 'Partially Correct', 'Incorrect')",
                    "correction_and_explanation": "string (A detailed explanation...)",
                    "additional_context": "string (Interesting facts...)"
                }
            ]
        }
