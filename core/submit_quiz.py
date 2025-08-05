import copy
import json
from .gemini_work import call_gemini

def create_submit_quiz_prompt(quiz: list[dict]) -> str:

    prompt_data = {
        "role": "You are a calm, clear, and informative AI Tutor. Your primary function is to provide constructive feedback on my answers to questions.",
        "input_description": "I will provide you with quiz questions with my answers. You will then evaluate my response.",
        "core_tasks": [
            "Score My Answer: Evaluate the correctness and completeness of my answer using one of the following qualitative assessments: 'Correct', 'Partially Correct', or 'Incorrect'.",
            "Provide Corrections (if needed): If my answer is not perfect, gently point out any inaccuracies or omissions. Clearly explain why it's incorrect or could be better, and then provide a well-explained, corrected version of the answer.",
            "Offer Additional Information/Context: Regardless of my answer's correctness, provide some relevant background information, interesting facts, or further explanations related to the topic of the question to help deepen my understanding.",
            "Ensure your feedback is always delivered in a patient, constructive, and easy-to-understand way. Focus on helping me learn.",
            "Return the result just like the example_of_output_format which is a list of dictionaries.",
            "IMPORTANT: Do not include bracketed source citations in the output."
        ],
        "example_of_output_format(the result should be a json)": [
            {
                "question": "string",
                "options": ["array of strings if question_type is multiple_choice otherwise None"],
                "user_answer": "string",
                "real_answer": "string",
                "score": "string (e.g., 'Correct', 'Partially Correct', 'Incorrect')",
                "correction_and_explanation": "string (A detailed explanation of any errors and the ideal correct answer. This should be a brief confirmation if the user's answer was perfect.)",
                "additional_context": "string (Interesting facts, historical background, or deeper context related to the topic.)"
            }
        ],
        "user_input": {
            "quiz_with_answers": quiz
        }
    }

    return json.dumps(prompt_data, indent=4, ensure_ascii=False)

def submit_quiz(api_key: str, quiz: list[dict], model: str = "gemini-2.5-pro") -> tuple[dict, dict]:
    full_prompt_for_quiz = create_submit_quiz_prompt(quiz)
    full_prompt_json_for_quiz = json.loads(full_prompt_for_quiz)

    with open("full_prompt_for_quiz.json", "w", encoding="utf-8") as f:
        json.dump(full_prompt_json_for_quiz, f, indent=4, ensure_ascii=False)

    result_for_quiz = call_gemini(
        api_key=api_key,
        prompt=full_prompt_for_quiz,
        model=model
    ).replace("```json", "").replace("```", "").replace("```json", "").replace("```", "")
    
    with open("result_for_quiz.txt", "w", encoding="utf-8") as f:
        f.write(result_for_quiz)
    result_for_quiz_json = json.loads(result_for_quiz)


    with open("result_for_quiz.json", "w", encoding="utf-8") as f:
        json.dump(result_for_quiz_json, f, indent=4, ensure_ascii=False)

    return full_prompt_json_for_quiz, result_for_quiz_json


if __name__ == "__main__":
    test_api_key = "AIzaSyDRg_55NEhdT0ur0L_xzw24_n5H002MaDo"
    test_quiz_type_structure = {
        "multiple_choice": 7,
        "short_answer": 2,
        "long_answer": 1,
        "total": 10
    }
    test_quiz = """
CNCF 

- make cn ubiquitous
- levels
    - sandbox, incubating, graduated
    - chasm
        - between early tech to main stream
        - moving from incubating to graduated
        - challenging
    - innovators → early adopters → early majority → late majority → laggards

CNCF Technical Oversight Committee(TOC)

- different citeria for maturity level

Elections and Voting

- Cloud Native Discussion Reconciliation
    - emphasize and argument
- not resolved → voting

TOC: Technical Oversight Committee

SIG: Special Interest Groups

TAG: Technical Advisory Groups
    """
    full_prompt_json_for_quiz, result_json_for_quiz = submit_quiz(test_api_key, test_quiz)
    
    with open("full_prompt_for_quiz.json", "w", encoding="utf-8") as f:
        json.dump(full_prompt_json_for_quiz, f, indent=4, ensure_ascii=False)
    with open("result_for_quiz.json", "w", encoding="utf-8") as f:
        json.dump(result_json_for_quiz, f, indent=4, ensure_ascii=False)