import streamlit as st
from datetime import datetime
from pages_english.controller import Controller
from st_flexible_callout_elements import flexible_success
import logging
import traceback

SCORE_COLORS = {
    "Correct": "green",
    "Incorrect": "red",
    "Partially Correct": "yellow"
}

class NoteDetailView:
    def __init__(self, controller: Controller, language: str):
        try:
            if not controller:
                raise ValueError("Controller cannot be None")
            
            if not language or not language.strip():
                raise ValueError("Language cannot be empty")
            
            self.controller = controller
            self.language = language
        except Exception as e:
            logging.error(f"Failed to initialize NoteDetailView: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize NoteDetailView: {str(e)}")

    def render(self):
        try:
            if not hasattr(st.session_state, 'selected_note_id'):
                st.error("No note selected. Please go back to the note list.")
                return
            
            note_id = st.session_state.selected_note_id
            note_name = st.session_state.selected_note_name
            
            try:
                note_details = self.controller.repositories["note_repository"].get_note(note_id)
                if not note_details:
                    st.error("Note not found.")
                    return
            except Exception as e:
                logging.error(f"Error retrieving note details: {traceback.format_exc()}")
                st.error("Failed to retrieve note details.")
                return
            
            note_id, note_name, note_content, created_at = note_details
            
            try:
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        created_at = datetime.now()
            except Exception as e:
                logging.error(f"Error parsing date: {traceback.format_exc()}")
                created_at = datetime.now()
            
            formatted_date = created_at.strftime("%Y-%m-%d %H:%M")
            
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                if st.button("← Back", key="back_to_list"):
                    st.session_state.current_view = "note_list"
                    st.rerun()
            
            with col2:
                st.title(f"📖 {note_name}")
                st.caption(f"Created: {formatted_date}")
            
            with col3:
                if st.button("🗑️ Delete", key="delete_note_detail", type="secondary"):
                    if st.session_state.get("confirm_delete_detail", False):
                        try:
                            self.controller.repositories["note_repository"].delete_note(note_id)
                            st.success(f"Note '{note_name}' deleted successfully!")
                            st.session_state.current_view = "note_list"
                            st.rerun()
                        except Exception as e:
                            logging.error(f"Error deleting note: {traceback.format_exc()}")
                            st.error("Failed to delete note.")
                    else:
                        st.session_state["confirm_delete_detail"] = True
                        st.warning("Click delete again to confirm deletion")
                        st.rerun()

            try:
                questions = self.controller.repositories["question_repository"].get_all_questions(note_id)
            except Exception as e:
                logging.error(f"Error retrieving questions: {traceback.format_exc()}")
                st.error("Failed to retrieve questions.")
                questions = []
            
            has_quiz_results = self._check_quiz_results(note_id, questions)
            
            tab_labels = ["Note", "Summary", "Review Quiz"]
            if has_quiz_results:
                tab_labels.insert(2, "Quiz Result")
            
            tabs = st.tabs(tab_labels, width="stretch")

            with tabs[0]: 
                self._render_note_content_tab(note_content, note_id)
            
            with tabs[1]: 
                self._render_summary_tab(note_id)

            if has_quiz_results:
                with tabs[2]: 
                    self._render_quiz_result_tab(note_id)
                with tabs[3]: 
                    self._render_review_quiz_tab(note_id)
            else:
                with tabs[2]: 
                    self._render_review_quiz_tab(note_id)
                    
        except Exception as e:
            logging.error(f"Error rendering NoteDetailView: {traceback.format_exc()}")
            st.error(f"Failed to render note detail view: {str(e)}")

    def _check_quiz_results(self, note_id: int, questions: list) -> bool:
        try:
            if not questions:
                return False
            
            question_ids = [q[0] for q in questions]
            try:
                gradings = self.controller.repositories["grading_repository"].get_all_gradings(question_ids)
                return len(gradings) > 0
            except Exception as e:
                logging.error(f"Error checking quiz results: {traceback.format_exc()}")
                return False
        except Exception as e:
            logging.error(f"Error in _check_quiz_results: {traceback.format_exc()}")
            return False

    def _render_note_content_tab(self, note_content: str, note_id: int):
        try:
            st.markdown("### Note")

            # Get hashtags with error handling
            try:
                hashtags = self.controller.repositories["note_hashtag_repository"].get_hashtags_by_note_id(note_id)
                if hashtags:
                    hashtags_str = " ".join([f"`#{tag}`" for tag in hashtags])
                    st.markdown(f"{hashtags_str}")
                else:
                    st.info("No tags found for this note.")
            except Exception as e:
                logging.error(f"Error retrieving hashtags: {traceback.format_exc()}")
                st.warning("Failed to load tags.")

            st.text_area(
                "Content", 
                value=note_content, 
                height=500, 
                disabled=True, 
                key="note_content_detail"
            )
        except Exception as e:
            logging.error(f"Error in _render_note_content_tab: {traceback.format_exc()}")
            st.error(f"Failed to render note content tab: {str(e)}")

    def _render_summary_tab(self, note_id: int):
        try:
            st.markdown("### Summary")
            summary: list[tuple[int, int, str, datetime]] = self.controller.repositories["summary_repository"].get_summary_by_note_id(note_id)
            st.markdown(summary[0][2])
        except Exception as e:
            logging.error(f"Error in _render_summary_tab: {traceback.format_exc()}")
            st.error(f"Failed to render summary tab: {str(e)}")

    def _render_quiz_result_tab(self, note_id: int):
        try:
            # Get questions with error handling
            try:
                questions = self.controller.repositories["question_repository"].get_all_questions(note_id)
                if not questions:
                    st.info("No questions found for this note.")
                    return
            except Exception as e:
                logging.error(f"Error retrieving questions: {traceback.format_exc()}")
                st.error("Failed to retrieve questions.")
                return
            
            st.markdown("### Quiz Result")

            question_ids = [q[0] for q in questions]
            
            # Get gradings with error handling
            try:
                gradings = self.controller.repositories["grading_repository"].get_all_gradings(question_ids)
                if not gradings:
                    st.info("No quiz results found.")
                    return
            except Exception as e:
                logging.error(f"Error retrieving gradings: {traceback.format_exc()}")
                st.error("Failed to retrieve quiz results.")
                return
            
            total_correct = 0
            total_incorrect = 0
            total_partially_correct = 0

            for grading in gradings:
                try:
                    if grading[4] == "Correct":
                        total_correct += 1
                    elif grading[4] == "Partially Correct":
                        total_partially_correct += 1
                    else:
                        total_incorrect += 1
                except Exception as e:
                    logging.error(f"Error processing grading: {traceback.format_exc()}")
                    continue

            st.markdown(f"Overall Performance")
            cols = st.columns(3)
            cols[0].metric("Total Correct", f"{total_correct}")
            cols[1].metric("Partially Correct", f"{total_partially_correct}")
            cols[2].metric("Incorrect", f"{total_incorrect}")
            st.divider()

            for i, result in enumerate(gradings):
                try:
                    # Get question details with error handling
                    try:
                        question = self.controller.repositories["question_repository"].get_question_by_id(result[1])
                        if not question:
                            st.warning(f"Question {i+1}: Question not found")
                            continue
                    except Exception as e:
                        logging.error(f"Error retrieving question {result[1]}: {traceback.format_exc()}")
                        st.warning(f"Question {i+1}: Failed to load question")
                        continue
                    
                    with st.expander(f"Question {i+1}: {question[2]}", expanded=True):
                        score = result[4]
                        score_color = SCORE_COLORS.get(score, 'gray')
                        st.markdown(f"**Score: <span style='color: {score_color};'>{score}</span>**", unsafe_allow_html=True)

                        st.markdown(f"**Your Answer**")
                        st.info(result[2])
                        st.markdown(f"**Correct Answer**")
                        st.info(result[3])
                        st.markdown(f"**Correction and Explanation**")
                        st.info(result[5])
                        st.markdown(f"**Additional Context**")
                        st.info(result[6])
                except Exception as e:
                    logging.error(f"Error rendering result {i}: {traceback.format_exc()}")
                    st.error(f"Error displaying result for question {i+1}")
                    continue
        except Exception as e:
            logging.error(f"Error in _render_quiz_result_tab: {traceback.format_exc()}")
            st.error(f"Failed to render quiz result tab: {str(e)}")

    def _render_review_quiz_tab(self, note_id: int):
        try:
            # Get questions with error handling
            try:
                questions = self.controller.repositories["question_repository"].get_all_questions(note_id)
                if not questions:
                    st.info("No questions found for this note.")
                    return
            except Exception as e:
                logging.error(f"Error retrieving questions: {traceback.format_exc()}")
                st.error("Failed to retrieve questions.")
                return
            
            if 'selected_api_key_option_detail' not in st.session_state:
                st.session_state.selected_api_key_option_detail = "Add new API key"
            
            # Get saved API keys with error handling
            try:
                saved_api_keys = self.controller.repositories["api_key_repository"].get_all_api_keys()
                api_key_options = ["Add new API key"] + [f"{key[1][:8]}...{key[1][-4:]}" for key in saved_api_keys]
            except Exception as e:
                logging.error(f"Error retrieving API keys: {traceback.format_exc()}")
                st.error("Failed to load saved API keys")
                saved_api_keys = []
                api_key_options = ["Add new API key"]
            
            col1, col2 = st.columns([1, 1])
            with col1: 
                try:
                    selected_api_key_option = st.selectbox(
                        "Select API Key", 
                        api_key_options, 
                        key="api_key_select_detail", 
                        index=api_key_options.index(st.session_state.selected_api_key_option_detail) if st.session_state.selected_api_key_option_detail in api_key_options else 0
                    )
                    
                    if selected_api_key_option == "Add new API key":
                        new_api_key = st.text_input("Enter new API Key", type="password", key="new_api_key_input_detail")
                        api_key = new_api_key
                        st.session_state.selected_api_key_option_detail = selected_api_key_option
                    else:
                        selected_index = api_key_options.index(selected_api_key_option) - 1
                        api_key = saved_api_keys[selected_index][1] if selected_index >= 0 and selected_index < len(saved_api_keys) else ""
                        st.session_state.selected_api_key_option_detail = selected_api_key_option
                except Exception as e:
                    logging.error(f"Error in API key selection: {traceback.format_exc()}")
                    st.error("Error in API key selection")
                    api_key = ""
                    
            with col2: 
                try:
                    model = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"], key="model_select_detail")
                except Exception as e:
                    logging.error(f"Error in model selection: {traceback.format_exc()}")
                    st.error("Error in model selection")
                    model = "gemini-2.5-pro"
            
            st.markdown("### Review Quiz")
            
            with st.form("quiz_form_detail"):
                user_answers = {}
                
                for i, question in enumerate(questions):
                    try:
                        st.markdown(f"**Question {i+1}: {question[2]}**")
                        
                        if question[3] == "multiple_choice":
                            try:
                                options = self.controller.repositories["option_repository"].get_options_by_question_id(question[0])
                                if options:
                                    option_texts = [option[2] for option in options]
                                    user_answers[f"q_{i}"] = st.radio(
                                        "Select your answer:",
                                        options=option_texts,
                                        key=f"quiz_q_{note_id}_{i}",
                                        label_visibility="collapsed"
                                    )
                                else:
                                    st.warning("No options available for multiple choice question")
                            except Exception as e:
                                logging.error(f"Error retrieving options for question {i}: {traceback.format_exc()}")
                                st.warning("Failed to load options for multiple choice question")
                        else:
                            user_answers[f"q_{i}"] = st.text_area(
                                "Your answer:",
                                key=f"quiz_q_{note_id}_{i}",
                                height=100,
                                label_visibility="collapsed"
                            )
                        
                        st.divider()
                    except Exception as e:
                        logging.error(f"Error rendering question {i}: {traceback.format_exc()}")
                        st.error(f"Error rendering question {i+1}")
                        continue
                
                if st.form_submit_button("Submit", type="primary", disabled=st.session_state.get("processing_review_quiz", False)):
                    if not api_key: 
                        st.error("Please enter your API key")
                        return
                    st.session_state.processing_review_quiz = True
                    quiz_for_grading = []
                    
                    for i, question in enumerate(questions):
                        try:
                            quiz_item = {
                                'question': question[2],
                                'question_type': question[3],
                                'answer': question[4],
                                'user_answer': user_answers.get(f"q_{i}", "")
                            }
                            
                            if question[3] == "multiple_choice":
                                try:
                                    options = self.controller.repositories["option_repository"].get_options_by_question_id(question[0])
                                    if options:
                                        quiz_item['options'] = [option[2] for option in options]
                                except Exception as e:
                                    logging.error(f"Error retrieving options for grading: {traceback.format_exc()}")
                            
                            quiz_for_grading.append(quiz_item)
                        except Exception as e:
                            logging.error(f"Error creating quiz item {i}: {traceback.format_exc()}")
                            continue
                    
                    st.session_state.quiz_for_grading_review_quiz = quiz_for_grading
                    st.rerun()
            
            if st.session_state.get("processing_review_quiz", False):
                try:
                    quiz_for_grading = st.session_state.get("quiz_for_grading_review_quiz", [])
                    
                    questions = self.controller.repositories["question_repository"].get_all_questions(note_id)
                    question_id_with_question = {question[2]: question[0] for question in questions}
                    
                    original_mapping = st.session_state.get("question_id_with_question", {})
                    st.session_state.question_id_with_question = question_id_with_question
                    
                    self.controller.update_grading(
                        api_key=api_key,
                        quiz=quiz_for_grading,
                        model=model
                    )
                    
                    st.session_state.question_id_with_question = original_mapping
                    
                    st.session_state.processing_review_quiz = False
                    st.session_state.quiz_for_grading_review_quiz = None
                except Exception as e:
                    logging.error(f"Error in quiz grading: {traceback.format_exc()}")
                    st.error(f"Failed to grade quiz: {str(e)}")
                    st.session_state.processing_review_quiz = False
            
            if st.session_state.get("review_graded", False) and not st.session_state.get("processing_review_quiz", False):
                flexible_success("Grading is completed! Please check the results in the Quiz Result tab.", alignment="center")
        except Exception as e:
            logging.error(f"Error in _render_review_quiz_tab: {traceback.format_exc()}")
            st.error(f"Failed to render review quiz tab: {str(e)}")
