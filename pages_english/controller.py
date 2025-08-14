
import streamlit as st
from core.submit_note import SubmitNote
from core.submit_quiz import SubmitQuiz
from st_flexible_callout_elements import flexible_success
import re
from typing import Any

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
            st.session_state.update(graded=False, processing_quiz=False, processing_review_quiz=False, grading_result="")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True): 
            st.session_state.processing_quiz = False
            st.rerun()


class Controller:
    def __init__(self, repositories: dict[str, Any]):
        self.repositories = repositories
        self.submit_note = SubmitNote(repositories)
        self.submit_quiz = SubmitQuiz(repositories)
        self.initialize_state()

    def initialize_state(self):
        states = {
            "note_submitted": False,
            "summary": "",
            "quiz": [],
            "graded": False,
            "review_graded": False,
            "grading_result": "",
            "multiple_choice_count": 0,
            "short_answer_count": 0,
            "long_answer_count": 0,
            "processing_note": False,
            "processing_quiz": False,
            "processing_review_quiz": False,
            "question_id_with_question": {}
        }
        for key, value in states.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def handle_note_submission(self, api_key: str, note_name: str, note_tags: list[str], note_content: str, quiz_structure: dict, model: str):
        if st.session_state.note_submitted: reset_new_note_dialog(); return

        with st.spinner("AI is analyzing your note..."):

            _, result_json, question_id_with_question = self.submit_note.submit_note(
                api_key=api_key,
                note_name=note_name,
                note_tags=note_tags,
                note_content=note_content,
                quiz_structure=quiz_structure,
                model=model
            )

            st.session_state.summary = result_json.get("summary", "Error fetching summary")
            st.session_state.quiz = result_json.get("quiz", [])
            st.session_state.question_id_with_question = question_id_with_question
            st.session_state.note_submitted = True
            st.session_state.processing_note = False
            st.rerun()

    def handle_quiz_grading(self, api_key: str, quiz: list[dict], model: str):
        if st.session_state.graded: reset_grading_dialog(); return

        with st.spinner("AI is grading your quiz..."):
            _, result_json = self.submit_quiz.submit_quiz(api_key=api_key, quiz=quiz, model=model)
            for question in result_json.get("quiz"):
                question_id = st.session_state.question_id_with_question.get(question.get("question"))
                self.repositories["grading_repository"].insert_grading(
                    question_id, 
                    question.get("user_answer"), 
                    question.get("real_answer") or question.get("answer"), 
                    question.get("score"), 
                    question.get("correction_and_explanation"), 
                    question.get("additional_context")
                )
            st.session_state.grading_result = result_json.get("quiz")
            st.session_state.graded = True
            st.session_state.processing_quiz = False
            st.rerun()

    def update_grading(self, api_key: str, quiz: list[dict], model: str):
        with st.spinner("AI is updating your grading..."):
            _, result_json = self.submit_quiz.submit_quiz(api_key=api_key, quiz=quiz, model=model)

            for question in result_json.get("quiz"):
                question_id = st.session_state.question_id_with_question[question.get("question")]
                grading = self.repositories["grading_repository"].get_grading_by_question_id(question_id)
                
                if grading:
                    self.repositories["grading_repository"].update_grading(
                        grading[0], 
                        question.get("user_answer"), 
                        question.get("real_answer") or question.get("answer"), 
                        question.get("score"), 
                        question.get("correction_and_explanation"), 
                        question.get("additional_context")
                    )
                else:
                    self.repositories["grading_repository"].insert_grading(
                        question_id, 
                        question.get("user_answer"), 
                        question.get("real_answer") or question.get("answer"), 
                        question.get("score"), 
                        question.get("correction_and_explanation"), 
                        question.get("additional_context")
                    )

            st.session_state.grading_result = result_json.get("quiz")
            st.session_state.review_graded = True
            st.session_state.processing_review_quiz = False
            st.rerun()