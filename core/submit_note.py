import copy
import json
from .gemini_work import call_gemini

def create_submit_note_prompt(note: str, quiz_structure: dict) -> str:

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

def submit_note(api_key: str, note: str, quiz_structure: dict, model: str = "gemini-2.5-pro") -> tuple[dict, dict]:
    full_prompt = create_submit_note_prompt(note, quiz_structure)
    full_prompt_json = json.loads(full_prompt)

    result = call_gemini(
        api_key=api_key,
        prompt=full_prompt,
        model=model
    )

    result_json = json.loads(result.replace("```json", "").replace("```", "").replace("```json", "").replace("```", ""))

    return full_prompt_json, result_json


if __name__ == "__main__":
    test_api_key = "AIzaSyDRg_55NEhdT0ur0L_xzw24_n5H002MaDo"
    test_quiz_type_structure = {
        "multiple_choice": 7,
        "short_answer": 2,
        "long_answer": 1,
        "total": 10
    }
    test_note = """
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
    full_prompt_for_note_json, result_for_note_json = submit_note(test_api_key, test_note, test_quiz_type_structure)

    
    with open("full_prompt_for_note.json", "w", encoding="utf-8") as f:
        json.dump(full_prompt_for_note_json, f, indent=4, ensure_ascii=False)
    with open("result_for_note.json", "w", encoding="utf-8") as f:
        json.dump(result_for_note_json, f, indent=4, ensure_ascii=False)