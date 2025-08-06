import json
import streamlit as st
from core.submit_note import submit_note
from core.submit_quiz import submit_quiz
from core.gemini_work import call_gemini
from st_flexible_callout_elements import flexible_success
import re

@st.dialog("Are you sure you want to erase all existing results?")
def reset_new_note_dialog():
    st.warning("All existing summary, quiz, and grading results will be erased.")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Erase", type="primary", use_container_width=True):
            st.session_state.update(note_submitted=False, processing_note=False, processing_quiz=False, summary="", quiz=[], graded=False, grading_result="", multiple_choice_count=0, short_answer_count=0, long_answer_count=0)
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True): 
            st.session_state.processing_note = False
            st.rerun()

@st.dialog("Are you sure you want to erase grading results?")
def reset_grading_dialog():
    st.warning("All existing grading results will be erased.")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Erase", type="primary", use_container_width=True):
            st.session_state.update(graded=False, processing_quiz=False, grading_result="")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True): 
            st.session_state.processing_quiz = False
            st.rerun()


class Controller:
    def __init__(self):
        self.initialize_state()

    def initialize_state(self):
        states = {
            "note_submitted": False,
            "summary": "",
            "quiz": [],
            "graded": False,
            "grading_result": "",
            "multiple_choice_count": 0,
            "short_answer_count": 0,
            "long_answer_count": 0,
            "processing_note": False,
            "processing_quiz": False
        }
        for key, value in states.items():
            if key not in st.session_state:
                st.session_state[key] = value


    def erase_bracked_source_citations(self, text: str):
        def replacement_logic(match):
            content_inside_brackets = match.group(1)
            if re.fullmatch(r'[0-9,\s]*', content_inside_brackets):
                return ""
            else:
                return match.group(0)

        processed_text = re.sub(r'\[(.*?)\]', replacement_logic, text)
        
        return processed_text.strip()
    
    def handle_note_submission(self, api_key: str, note: str, quiz_structure: dict, model: str):
        if st.session_state.note_submitted: reset_new_note_dialog(); return

        with st.spinner("AI is analyzing your note..."):

            _, result_json = submit_note(api_key=api_key, note=note, quiz_structure=quiz_structure, model=model)

            # with open("gemini_summary.txt", "w", encoding="utf-8") as f:
            #     f.write(self.erase_bracked_source_citations(result_json["summary"]))
            
            # with open("gemini_quiz.txt", "w", encoding="utf-8") as f:
            #     for question in result_json["quiz"]:
            #         f.write(self.erase_bracked_source_citations(question["question"]))
            #         f.write("\n")
            #         if question.get("options"):
            #             for option in question["options"]:
            #                 f.write(self.erase_bracked_source_citations(option))
            #                 f.write("\n")
            #         f.write(self.erase_bracked_source_citations(question["answer"]))
            #         f.write("\n")
            #         f.write("\n")

            result_json["summary"] = self.erase_bracked_source_citations(result_json["summary"])
            for question in result_json["quiz"]:
                question["question"] = self.erase_bracked_source_citations(question["question"])
                if question.get("options"):
                    question["options"] = [self.erase_bracked_source_citations(option) for option in question["options"]]
                question["answer"] = self.erase_bracked_source_citations(question["answer"])

            st.session_state.summary = result_json.get("summary", "Error fetching summary")
            st.session_state.quiz = result_json.get("quiz", [])
            st.session_state.note_submitted = True
            st.session_state.processing_note = False
            st.rerun()

            

    def handle_quiz_grading(self, api_key: str, quiz: list[dict], model: str):
        if st.session_state.graded: reset_grading_dialog(); return

        with st.spinner("AI is grading your quiz..."):
            _, result_json = submit_quiz(api_key=api_key, quiz=quiz, model=model)
            st.session_state.grading_result = result_json
            st.session_state.graded = True
            st.session_state.processing_quiz = False
            st.rerun()
