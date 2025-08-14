import copy
import json
import time
from .gemini_work import GeminiWork
from typing import Any
import logging
import traceback

class SubmitQuiz:
    def __init__(self, repositories: dict[str, Any]):
        try:
            if not repositories:
                raise ValueError("Repositories dictionary cannot be empty")
            
            # Note: SubmitQuiz doesn't directly use repositories, but we keep the interface consistent
            self.repositories = repositories
        except Exception as e:
            logging.error(f"Failed to initialize SubmitQuiz: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize SubmitQuiz: {str(e)}")

    def _create_submit_quiz_prompt(self, quiz: list[dict]) -> str:
        try:
            # Input validation
            if not isinstance(quiz, list):
                raise ValueError("Quiz must be a list")
            
            if not quiz:
                raise ValueError("Quiz cannot be empty")
            
            # Validate each quiz item
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

            prompt_data = {
                "role": "You are a calm, clear, and informative AI Tutor. Your primary function is to provide constructive feedback on my answers to questions.",
                "input_description": "I will provide you with quiz questions with my answers. You will then evaluate my response.",
                "core_tasks": [
                    "Score My Answer: Evaluate the correctness and completeness of my answer using one of the following qualitative assessments: 'Correct', 'Partially Correct', or 'Incorrect'.",
                    "Provide Corrections (if needed): If my answer is not perfect, gently point out any inaccuracies or omissions. Clearly explain why it's incorrect or could be better, and then provide a well-explained, corrected version of the answer.",
                    "Offer Additional Information/Context: Regardless of my answer's correctness, provide some relevant background information, interesting facts, or further explanations related to the topic of the question to help deepen my understanding.",
                    "Ensure your feedback is always delivered in a patient, constructive, and easy-to-understand way. Focus on helping me learn.",
                    "Return the result as a single JSON object with a top-level key named 'quiz'. The value of 'quiz' should be a list of dictionaries, just like the example.",
                    "IMPORTANT: Do not include bracketed source citations in the output.",
                    "YOUR OUTPUT SHOULD BE JSON FORMAT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
                    "DO NOT SAY ANYTHING ELSE!!!!! JUST RETURN THE JSON FORMAT I ASKED FOR!!!!!!!!!!!!!"
                ],
                "example_of_output_format(the result should be a json)": {
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
                },
                "user_input": {
                    "quiz_with_answers": quiz
                }
            }

            return json.dumps(prompt_data, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error creating submit quiz prompt: {traceback.format_exc()}")
            raise Exception(f"Failed to create submit quiz prompt: {str(e)}")

    def submit_quiz(self, api_key: str, quiz: list[dict], model: str = "gemini-2.5-pro") -> tuple[dict, dict]:
        try:
            # Input validation
            if not api_key or not api_key.strip():
                raise ValueError("API key cannot be empty")
            
            if not isinstance(quiz, list):
                raise ValueError("Quiz must be a list")
            
            if not quiz:
                raise ValueError("Quiz cannot be empty")
            
            if not model or not model.strip():
                raise ValueError("Model cannot be empty")
            
            # Validate API key format
            if not GeminiWork.validate_api_key(api_key):
                raise ValueError("Invalid API key format")
            
            # Create prompt
            try:
                full_prompt_for_quiz = self._create_submit_quiz_prompt(quiz)
                full_prompt_json_for_quiz = json.loads(full_prompt_for_quiz)
            except Exception as e:
                logging.error(f"Error creating quiz prompt: {traceback.format_exc()}")
                raise Exception(f"Failed to create quiz prompt: {str(e)}")
            
            # Call Gemini API with retry logic
            max_retries = 5
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    result = GeminiWork.call_gemini(
                        api_key=api_key,
                        prompt=full_prompt_for_quiz,
                        model=model
                    )
                    
                    # Parse result
                    try:
                        result_json = json.loads(result)
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse JSON result: {str(e)}")
                        raise Exception(f"Invalid JSON response from Gemini: {str(e)}")
                    
                    # Validate result structure
                    if not result_json.get("quiz"):
                        raise Exception("Missing 'quiz' in Gemini response")
                    
                    if not isinstance(result_json["quiz"], list):
                        raise Exception("'quiz' must be a list")
                    
                    if len(result_json["quiz"]) != len(quiz):
                        raise Exception(f"Expected {len(quiz)} quiz items, got {len(result_json['quiz'])}")
                    
                    # Validate each quiz result item
                    for i, quiz_result in enumerate(result_json["quiz"]):
                        if not isinstance(quiz_result, dict):
                            raise Exception(f"Quiz result item {i} must be a dictionary")
                        
                        required_fields = ["question", "user_answer", "real_answer", "score", 
                                         "correction_and_explanation", "additional_context"]
                        for field in required_fields:
                            if field not in quiz_result:
                                raise Exception(f"Quiz result item {i} missing required field: {field}")
                        
                        # Validate score values
                        valid_scores = ["Correct", "Partially Correct", "Incorrect"]
                        if quiz_result["score"] not in valid_scores:
                            raise Exception(f"Quiz result item {i} has invalid score: {quiz_result['score']}")
                    
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    retry_count += 1
                    logging.warning(f"Submit quiz attempt {retry_count} failed: {str(e)}")
                    
                    if retry_count >= max_retries:
                        logging.error(f"All {max_retries} attempts failed for submit quiz")
                        raise Exception(f"Failed to process quiz after {max_retries} attempts: {str(e)}")
                    
                    time.sleep(2)  # Wait before retrying
            
            # Save result to file
            try:
                with open("result_for_quiz.json", "w", encoding="utf-8") as f:
                    json.dump(result_json, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logging.error(f"Error saving quiz result to file: {traceback.format_exc()}")
                # Don't fail the operation if file save fails
                logging.warning(f"Quiz processed but failed to save result file: {str(e)}")

            return full_prompt_json_for_quiz, result_json
            
        except Exception as e:
            logging.error(f"Error in submit_quiz: {traceback.format_exc()}")
            raise Exception(f"Failed to submit quiz: {str(e)}")
    
    def validate_quiz_structure(self, quiz: list[dict]) -> bool:
        """Validate quiz structure before submission"""
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