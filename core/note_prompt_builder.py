import json
import logging
import traceback
from typing import Dict, Any


class NotePromptBuilder:
    
    @staticmethod
    def create_submit_note_prompt(note: str, quiz_structure: dict) -> str:
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
            
            prompt_data = NotePromptBuilder._build_prompt_structure(note, quiz_structure)
            return json.dumps(prompt_data, indent=4, ensure_ascii=False)
            
        except Exception as e:
            logging.error(f"Error creating submit note prompt: {traceback.format_exc()}")
            raise Exception(f"Failed to create submit note prompt: {str(e)}")
    
    @staticmethod
    def _build_prompt_structure(note: str, quiz_structure: dict) -> Dict[str, Any]:
        mc_count = quiz_structure.get("multiple_choice", 0)
        sa_count = quiz_structure.get("short_answer", 0)
        la_count = quiz_structure.get("long_answer", 0)
        
        prompt_data = {
            "role": "You are an AI Lecture Transcript Analyst and Tutor. Your primary function is to help me understand lecture material better by analyzing, refining, and explaining concepts based on the transcripts I provide.",
            "input_description": "I will provide you with a transcript from a lecture. These transcripts might be automatically generated (and thus contain errors), incomplete, or lack proper formatting.",
            "core_tasks": NotePromptBuilder._get_core_tasks(mc_count, sa_count, la_count),
            "example_of_output_format(the result should be a json)": NotePromptBuilder._get_output_format_example(),
            "user_input": {
                "note_transcript": note
            }
        }
        
        return prompt_data
    
    @staticmethod
    def _get_core_tasks(mc_count: int, sa_count: int, la_count: int) -> list[str]:
        tasks = [
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
            "Please structure the summary for at-a-glance comprehension. It must be organized into clear categories based on context or usage level, such as 'Most Common Expressions', 'Simpler Terms', and 'More Technical/Professional Expressions'.",
            f"Generate Practice Questions: Create exactly {mc_count} multiple-choice, {sa_count} short-answer, and {la_count} long-answer questions. Adhere strictly to the 'quiz' structure defined in the 'output_format'."
        ]
        
        return tasks
    
    @staticmethod
    def _get_output_format_example() -> Dict[str, Any]:
        return {
            "summary": "summary in markdown, which looks professional and concise(do not include bracketed source citations)",
            "quiz": [
                {
                    "question_type": "string(multiple_choice, short_answer, long_answer)",
                    "question": "string",
                    "options": ["array of strings if question_type is multiple_choice otherwise None(options don't include option labels)"],
                    "answer": "string"
                }
            ]
        }
