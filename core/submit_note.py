import copy
import json
from datetime import datetime
import time
from .gemini_work import GeminiWork
from typing import Any
import logging
import traceback

class SubmitNote:
    def __init__(self, repositories: dict[str, Any]):
        try:
            if not repositories:
                raise ValueError("Repositories dictionary cannot be empty")
            
            required_repos = ["api_key_repository", "note_repository", "note_hashtag_repository", 
                            "question_repository", "option_repository"]
            
            for repo_name in required_repos:
                if repo_name not in repositories:
                    raise ValueError(f"Required repository '{repo_name}' not found")
            
            self.repositories = repositories
        except Exception as e:
            logging.error(f"Failed to initialize SubmitNote: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize SubmitNote: {str(e)}")

    def _create_submit_note_prompt(self, note: str, quiz_structure: dict) -> str:
        try:
            # Input validation
            if not note or not note.strip():
                raise ValueError("Note content cannot be empty")
            
            if not isinstance(quiz_structure, dict):
                raise ValueError("Quiz structure must be a dictionary")
            
            required_keys = ["multiple_choice", "short_answer", "long_answer"]
            for key in required_keys:
                if key not in quiz_structure:
                    raise ValueError(f"Quiz structure missing required key: {key}")
                
                if not isinstance(quiz_structure[key], int) or quiz_structure[key] < 0:
                    raise ValueError(f"Quiz structure value for '{key}' must be a non-negative integer")
            
            prompt_data = {
                "role": "You are an AI Lecture Transcript Analyst and Tutor. Your primary function is to help me understand lecture material better by analyzing, refining, and explaining concepts based on the transcripts I provide.",
                "input_description": "I will provide you with a transcript from a lecture. These transcripts might be automatically generated (and thus contain errors), incomplete, or lack proper formatting.",
                "core_tasks": [
                    "Fact-Check: Identify and point out any potential factual inaccuracies or outdated information that might stem from transcription errors or the lecture's content. Suggest corrections with brief explanations.",
                    "Identify Gaps: Pinpoint areas that seem incomplete or where crucial information might be missing (e.g., a speaker trailed off, or a key detail was omitted). Suggest what might be missing or what questions I could ask to fill these gaps.",
                    "Clarify Ambiguities: If any part of the transcript is unclear, ambiguous, or poorly phrased, rephrase it for better understanding.",
                    "Improve Structure & Organization: If applicable, suggest ways to better structure the information (e.g., using headings, bullet points, summaries).",
                    "Define Key Terms: Identify key terminology within the transcript. Provide clear and concise definitions for any terms that might be complex or foundational to the topic.",
                    "Explain Core Concepts: For the main topics covered in the transcript, provide a clear explanation as if you were teaching it to me for the first time or clarifying a point of confusion.",
                    "Provide Examples: Where appropriate, offer relevant examples, analogies, or real-world applications to illustrate the concepts discussed in the lecture.",
                    "Connect to Broader Topics: If possible, explain how the concepts in the transcript relate to larger themes within the subject or to previously discussed topics.",
                    "Suggest Further Learning: If relevant, suggest resources (articles, videos, concepts to Google) for deeper exploration of the topics.",
                    "DO NOT INCLUDE BRACKETED SOURCE CITATIONS IN THE SUMMARY AND QUIZ like [0, 3, 4, 12, 13, 14, 15].",
                    "YOUR OUTPUT SHOULD BE JSON FORMAT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
                    "DO NOT SAY ANYTHING ELSE!!!!! JUST RETURN THE JSON FORMAT I ASKED FOR!!!!!!!!!!!!!",
                    "The summaary should be concise and easy to read and understand.",
                    "Please structure the summary for at-a-glance comprehension. It must be organized into clear categories based on context or usage level, such as 'Most Common Expressions', 'Simpler Terms', and 'More Technical/Professional Expressions'."
                ],
                "example_of_output_format(the result should be a json)": {
                    "summary": "summary in markdown, which looks professional and concise(do not include bracketed source citations)",
                    "quiz": [
                        {
                            "question_type": "string(multiple_choice, short_answer, long_answer)",
                            "question": "string",
                            "options": ["array of strings if question_type is multiple_choice otherwise None(options don't include option labels)"],
                            "answer": "string"
                        }
                    ]
                },
                "user_input": {
                    "note_transcript": note
                }
            }

            mc_count = quiz_structure.get("multiple_choice", 0)
            sa_count = quiz_structure.get("short_answer", 0)
            la_count = quiz_structure.get("long_answer", 0)

            prompt_data["core_tasks"].append(f"Generate Practice Questions: Create exactly {mc_count} multiple-choice, {sa_count} short-answer, and {la_count} long-answer questions. Adhere strictly to the 'quiz' structure defined in the 'output_format'.")

            return json.dumps(prompt_data, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error creating submit note prompt: {traceback.format_exc()}")
            raise Exception(f"Failed to create submit note prompt: {str(e)}")

    def submit_note(self, api_key: str, note_name: str, note_tags: list[str], note_content: str, quiz_structure: dict, model: str = "gemini-2.5-pro") -> tuple[dict, dict]:
        try:
            # Input validation
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
            
            # Validate API key format
            if not GeminiWork.validate_api_key(api_key):
                raise ValueError("Invalid API key format")
            
            # Process API key
            try:
                all_api_keys: list[tuple[int, str, datetime]] = self.repositories["api_key_repository"].get_all_api_keys()
                
                api_key_id = 0
                for existing_api_key_id, api_key_value, last_used_at in all_api_keys:
                    if api_key == api_key_value:
                        api_key_id = existing_api_key_id
                        self.repositories["api_key_repository"].update_api_key(api_key_id)
                        break
                else:
                    api_key_id = self.repositories["api_key_repository"].insert_api_key(api_key)
            except Exception as e:
                logging.error(f"Error processing API key: {traceback.format_exc()}")
                raise Exception(f"Failed to process API key: {str(e)}")
            
            # Insert note
            try:
                note_id = self.repositories["note_repository"].insert_note(note_name, note_content)
            except Exception as e:
                logging.error(f"Error inserting note: {traceback.format_exc()}")
                raise Exception(f"Failed to insert note: {str(e)}")
            
            # Insert note tags
            if note_tags:
                try:
                    self.repositories["note_hashtag_repository"].insert_note_hashtags(note_id, note_tags)
                except Exception as e:
                    logging.error(f"Error inserting note tags: {traceback.format_exc()}")
                    # Don't fail the entire operation if tag insertion fails
                    logging.warning(f"Note created but tags failed to insert: {str(e)}")
            
            # Create prompt
            try:
                full_prompt = self._create_submit_note_prompt(note_content, quiz_structure)
                full_prompt_json = json.loads(full_prompt)
            except Exception as e:
                logging.error(f"Error creating prompt: {traceback.format_exc()}")
                raise Exception(f"Failed to create prompt: {str(e)}")
            
            # Call Gemini API with retry logic
            max_retries = 5
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    result = GeminiWork.call_gemini(
                        api_key=api_key,
                        prompt=full_prompt,
                        model=model
                    )
                    
                    # Parse result
                    try:
                        result_json = json.loads(result)
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse JSON result: {str(e)}")
                        raise Exception(f"Invalid JSON response from Gemini: {str(e)}")
                    
                    # Validate result structure
                    if not result_json.get("summary"):
                        raise Exception("Missing 'summary' in Gemini response")
                    
                    if not result_json.get("quiz"):
                        raise Exception("Missing 'quiz' in Gemini response")
                    
                    if not isinstance(result_json["quiz"], list):
                        raise Exception("'quiz' must be a list")
                    
                    # Validate each quiz item
                    for i, quiz_item in enumerate(result_json["quiz"]):
                        if not isinstance(quiz_item, dict):
                            raise Exception(f"Quiz item {i} must be a dictionary")
                        
                        required_fields = ["question_type", "question", "answer"]
                        for field in required_fields:
                            if field not in quiz_item:
                                raise Exception(f"Quiz item {i} missing required field: {field}")
                        
                        if quiz_item["question_type"] == "multiple_choice":
                            if "options" not in quiz_item or not isinstance(quiz_item["options"], list):
                                raise Exception(f"Quiz item {i} missing or invalid options for multiple choice")
                    
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    retry_count += 1
                    logging.warning(f"Submit note attempt {retry_count} failed: {str(e)}")
                    
                    if retry_count >= max_retries:
                        logging.error(f"All {max_retries} attempts failed for submit note")
                        raise Exception(f"Failed to process note after {max_retries} attempts: {str(e)}")
                    
                    time.sleep(2)  # Wait before retrying
            
            # Save result to file
            try:
                with open("result_for_note.json", "w", encoding="utf-8") as f:
                    json.dump(result_json, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logging.error(f"Error saving result to file: {traceback.format_exc()}")
                # Don't fail the operation if file save fails
                logging.warning(f"Note processed but failed to save result file: {str(e)}")
            
            # Process quiz questions
            question_id_with_question: dict[str, int] = {}
            try:
                for question in result_json.get("quiz", []):
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
            except Exception as e:
                logging.error(f"Error processing quiz questions: {traceback.format_exc()}")
                raise Exception(f"Failed to process quiz questions: {str(e)}")
            
            return full_prompt_json, result_json, question_id_with_question
            
        except Exception as e:
            logging.error(f"Error in submit_note: {traceback.format_exc()}")
            raise Exception(f"Failed to submit note: {str(e)}")