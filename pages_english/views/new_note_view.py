import json
import streamlit as st
from streamlit_tags import st_tags
from st_flexible_callout_elements import flexible_success
from pages_english.controller import Controller
import logging
import traceback

SCORE_COLORS = {
    "Correct": "green",
    "Incorrect": "red",
    "Partially Correct": "yellow"
}

class NewNoteView:
    def __init__(self, controller: Controller, language: str):
        try:
            if not controller:
                raise ValueError("Controller cannot be None")
            
            if not language or not language.strip():
                raise ValueError("Language cannot be empty")
            
            self.controller = controller
            self.language = language
        except Exception as e:
            logging.error(f"Failed to initialize NewNoteView: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize NewNoteView: {str(e)}")

    def render(self):
        try:
            # Initialize session state for API key selection
            if 'selected_api_key_option' not in st.session_state:
                st.session_state.selected_api_key_option = "Add new API key"
            
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
                        key="api_key_select", 
                        index=api_key_options.index(st.session_state.selected_api_key_option) if st.session_state.selected_api_key_option in api_key_options else 0
                    )
                    
                    if selected_api_key_option == "Add new API key":
                        new_api_key = st.text_input("Enter new API Key", type="password", key="new_api_key_input")
                        api_key = new_api_key
                        st.session_state.selected_api_key_option = selected_api_key_option
                    else:
                        # Find the selected API key
                        selected_index = api_key_options.index(selected_api_key_option) - 1  # -1 because of "Add new API key"
                        api_key = saved_api_keys[selected_index][1] if selected_index >= 0 and selected_index < len(saved_api_keys) else ""
                        st.session_state.selected_api_key_option = selected_api_key_option
                        
                        # Add delete button for existing API keys
                        if st.button("🗑️ Delete API Key", key="delete_api_key"):
                            try:
                                api_key_id = saved_api_keys[selected_index][0]
                                self.controller.repositories["api_key_repository"].delete_api_key(api_key_id)
                                st.session_state.selected_api_key_option = "Add new API key"
                                st.rerun()
                            except Exception as e:
                                logging.error(f"Error deleting API key: {traceback.format_exc()}")
                                st.error("Failed to delete API key")
                except Exception as e:
                    logging.error(f"Error in API key selection: {traceback.format_exc()}")
                    st.error("Error in API key selection")
                    api_key = ""
                    
            with col2: 
                try:
                    model = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"])
                except Exception as e:
                    logging.error(f"Error in model selection: {traceback.format_exc()}")
                    st.error("Error in model selection")
                    model = "gemini-2.5-pro"

            tabs = st.tabs([
                "New Note",
                "Summary",
                "Quiz",
                "Grading"
            ], width="stretch")

            with tabs[0]: 
                self._render_new_note_tab(api_key=api_key, model=model)
            with tabs[1]: 
                self._render_summary_tab()
            with tabs[2]: 
                self._render_quiz_tab(api_key=api_key, model=model)
            with tabs[3]: 
                self._render_grading_tab()
                
        except Exception as e:
            logging.error(f"Error rendering NewNoteView: {traceback.format_exc()}")
            st.error(f"Failed to render new note view: {str(e)}")

    def _render_new_note_tab(self, api_key: str, model: str):
        try:
            with st.form("note_form"):
                note_name: str = st.text_input("Note Name", placeholder="Enter your note name here.")
                note_tags: list[str] = st_tags(
                    label="Tags",
                    text="Press enter to add more",
                    value=[],
                    maxtags=5,
                    key="note_tags"
                )
                note_content: str = st.text_area("Note Content", height=300)
                st.markdown("###### Configure Your Quiz (Total 10 questions)", help="Configure the number of multiple choice, short answer, and long answer questions.")

                c1, c2, c3 = st.columns(3)
                with c1: 
                    st.number_input("Multiple Choice", min_value=0, max_value=10, value=0, step=1, key="multiple_choice_count", help="Number of multiple choice questions")
                with c2: 
                    st.number_input("Short Answer", min_value=0, max_value=10, value=0, step=1, key="short_answer_count", help="Number of short answer questions")
                with c3: 
                    st.number_input("Long Answer", min_value=0, max_value=10, value=0, step=1, key="long_answer_count", help="Number of long answer questions")
                
                quiz_structure: dict[str, int] = {
                    "multiple_choice": st.session_state.multiple_choice_count,
                    "short_answer": st.session_state.short_answer_count,
                    "long_answer": st.session_state.long_answer_count
                }

                if st.form_submit_button("Submit", disabled=st.session_state.get("processing_note", False)):
                    # Input validation
                    if not api_key: 
                        st.error("Please enter your API key")
                        return
                    if not note_name or not note_name.strip(): 
                        st.error("Please enter your note name")
                        return
                    if not note_content or not note_content.strip(): 
                        st.error("Please enter your note")
                        return
                    if sum(quiz_structure.values()) != 10: 
                        st.error("Total questions must equal 10")
                        return
                    
                    st.session_state.processing_note = True
                    st.rerun()
                
                if st.session_state.get("processing_note", False):
                    try:
                        self.controller.handle_note_submission(
                            api_key=api_key,
                            note_name=note_name,
                            note_tags=note_tags,
                            note_content=note_content,
                            quiz_structure=quiz_structure,
                            model=model
                        )
                    except Exception as e:
                        logging.error(f"Error in note submission: {traceback.format_exc()}")
                        st.error(f"Failed to submit note: {str(e)}")
                        st.session_state.processing_note = False

                if st.session_state.get("note_submitted", False) and not st.session_state.get("processing_note", False):
                    flexible_success("Analysis is complete! Please check the results in the Summary tab.", alignment="center")
                    
        except Exception as e:
            logging.error(f"Error in _render_new_note_tab: {traceback.format_exc()}")
            st.error(f"Failed to render new note tab: {str(e)}")

    def _render_summary_tab(self):
        try:
            if not st.session_state.get("note_submitted", False): 
                st.info("Please submit a note first.")
            else: 
                summary = st.session_state.get("summary", "")
                if summary:
                    st.markdown(summary)
                else:
                    st.warning("Summary not available")
        except Exception as e:
            logging.error(f"Error in _render_summary_tab: {traceback.format_exc()}")
            st.error(f"Failed to render summary tab: {str(e)}")

    def _render_quiz_tab(self, api_key: str, model: str):
        try:
            if not st.session_state.get("note_submitted", False): 
                st.info("Please submit a note first.")
            else:
                quiz = st.session_state.get("quiz", [])
                if not quiz:
                    st.warning("No quiz available")
                    return
                
                with st.form("quiz_solve_form"):
                    for i, one_question in enumerate(quiz):
                        try:
                            st.markdown(f"**Question {i+1}: {one_question.get('question', 'No question')}**")
                            if one_question.get("question_type") == "multiple_choice":
                                options = one_question.get("options", [])
                                if options:
                                    one_question['user_answer'] = st.radio(
                                        label="Select your answer",
                                        options=options,
                                        key=f"user_answer_{i}",
                                        label_visibility="collapsed"
                                    )
                                else:
                                    st.warning("No options available for multiple choice question")
                            else:
                                one_question['user_answer'] = st.text_area(
                                    label=f"Enter your answer",
                                    key=f"user_answer_{i}",
                                    label_visibility="collapsed"
                                )
                            with st.expander("Preview answer"):
                                st.write(one_question.get('answer', 'No answer available'))
                            st.divider()
                        except Exception as e:
                            logging.error(f"Error rendering question {i}: {traceback.format_exc()}")
                            st.error(f"Error rendering question {i+1}")
                            continue
                    
                    grade_submitted = st.form_submit_button("Grade", disabled=st.session_state.get("processing_quiz", False))
                    if grade_submitted:
                        if not api_key: 
                            st.error("Please enter your API key")
                            return
                        if not quiz: 
                            st.error("No quiz available")
                            return

                        st.session_state.processing_quiz = True
                        st.rerun()
                    
                    if st.session_state.get("processing_quiz", False):
                        try:
                            self.controller.handle_quiz_grading(
                                api_key=api_key,
                                quiz=quiz,
                                model=model
                            )
                        except Exception as e:
                            logging.error(f"Error in quiz grading: {traceback.format_exc()}")
                            st.error(f"Failed to grade quiz: {str(e)}")
                            st.session_state.processing_quiz = False
                    
                    if st.session_state.get("graded", False) and not st.session_state.get("processing_quiz", False):
                        flexible_success("Grading is completed! Please check the results in the Grading tab.", alignment="center")
        except Exception as e:
            logging.error(f"Error in _render_quiz_tab: {traceback.format_exc()}")
            st.error(f"Failed to render quiz tab: {str(e)}")

    def _render_grading_tab(self):
        try:
            if not st.session_state.get("graded", False): 
                st.info("Please solve the questions and click the 'Grade' button.")
            else:
                individual_results = st.session_state.get("grading_result", [])
                if not individual_results:
                    st.warning("No grading results available")
                    return
                
                total_correct = 0
                total_partially_correct = 0
                total_incorrect = 0
                
                for i, result in enumerate(individual_results):
                    try:
                        score = result.get("score", "")
                        if score == "Correct":
                            total_correct += 1
                        elif score == "Partially Correct":
                            total_partially_correct += 1
                        else:
                            total_incorrect += 1
                    except Exception as e:
                        logging.error(f"Error processing result {i}: {traceback.format_exc()}")
                        continue

                total_summary = {
                    "total_correct": total_correct,
                    "total_partially_correct": total_partially_correct,
                    "total_incorrect": total_incorrect,
                    "total_questions": len(individual_results),
                }

                if total_summary:
                    st.markdown(f"Overall Performance")
                    cols = st.columns(3)
                    cols[0].metric("Total Correct", f"{total_summary.get('total_correct', 0)}")
                    cols[1].metric("Partially Correct", f"{total_summary.get('total_partially_correct', 0)}")
                    cols[2].metric("Incorrect", f"{total_summary.get('total_incorrect', 0)}")
                    st.divider()

                st.markdown("### Detailed Breakdown")

                for i, result in enumerate(individual_results):
                    try:
                        with st.expander(f"Question {i+1}: {result.get('question', 'No question')}", expanded=True):
                            score = result.get('score', 'N/A')
                            score_color = SCORE_COLORS.get(score, 'gray')
                            st.markdown(f"**Score: <span style='color: {score_color};'>{score}</span>**", unsafe_allow_html=True)

                            st.markdown(f"**Your Answer**")
                            st.info(result.get('user_answer', 'No answer provided'))
                            st.markdown(f"**Correct Answer**")
                            st.info(result.get('real_answer', 'No answer provided'))
                            st.markdown(f"**Correction and Explanation**")
                            st.info(result.get('correction_and_explanation', 'No explanation provided'))
                            st.markdown(f"**Additional Context**")
                            st.info(result.get('additional_context', 'No additional context provided'))
                    except Exception as e:
                        logging.error(f"Error rendering result {i}: {traceback.format_exc()}")
                        st.error(f"Error displaying result for question {i+1}")
                        continue
        except Exception as e:
            logging.error(f"Error in _render_grading_tab: {traceback.format_exc()}")
            st.error(f"Failed to render grading tab: {str(e)}")