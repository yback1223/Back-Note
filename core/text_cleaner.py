import re
import logging
from typing import Dict, Any, List


class TextCleaner:
    
    @staticmethod
    def erase_bracked_source_citations(text: str) -> str:

        if not text or not isinstance(text, str):
            return text
        
        def is_source_citation(content: str) -> bool:

            return bool(re.fullmatch(r'^[0-9,\s]*$', content))
        
        def remove_citation(match) -> str:

            citation_content = match.group(1)
            return "" if is_source_citation(citation_content) else match.group(0)
        
        cleaned_text = re.sub(r'\[(.*?)\]', remove_citation, text)
        
        return cleaned_text.strip()
    
    @staticmethod
    def clean_quiz_result(result_json: Dict[str, Any]) -> Dict[str, Any]:

        try:
            if "summary" in result_json:
                result_json["summary"] = TextCleaner.erase_bracked_source_citations(result_json["summary"])
            
            if "quiz" in result_json and isinstance(result_json["quiz"], list):
                for question in result_json["quiz"]:
                    if isinstance(question, dict):
                        if "question" in question:
                            question["question"] = TextCleaner.erase_bracked_source_citations(question["question"])
                        
                        if "options" in question and isinstance(question["options"], list):
                            question["options"] = [
                                TextCleaner.erase_bracked_source_citations(option) 
                                for option in question["options"]
                            ]
                        
                        if "answer" in question:
                            question["answer"] = TextCleaner.erase_bracked_source_citations(question["answer"])
                        
                        if "real_answer" in question:
                            question["real_answer"] = TextCleaner.erase_bracked_source_citations(question["real_answer"])
                        
                        if "user_answer" in question:
                            question["user_answer"] = TextCleaner.erase_bracked_source_citations(question["user_answer"])
                        
                        if "correction_and_explanation" in question:
                            question["correction_and_explanation"] = TextCleaner.erase_bracked_source_citations(
                                question["correction_and_explanation"]
                            )
                        
                        if "additional_context" in question:
                            question["additional_context"] = TextCleaner.erase_bracked_source_citations(
                                question["additional_context"]
                            )
            
            return result_json
            
        except Exception as e:
            logging.error(f"Error cleaning quiz result: {str(e)}")
            return result_json
