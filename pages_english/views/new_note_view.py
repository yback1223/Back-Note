import json
import streamlit as st
from st_flexible_callout_elements import flexible_success
from pages_english.controller import Controller

SCORE_COLORS = {
    "Correct": "green",
    "Incorrect": "red",
    "Partially Correct": "yellow"
}

class NewNoteView:
    def __init__(self, controller: Controller, language: str):
        self.controller = controller
        self.language = language

    def render(self):
        col1, col2 = st.columns([1, 1])
        with col1: api_key = st.text_input("Gemini API Key", type="password")
        with col2: model = st.selectbox("Model", ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro"])

        tabs = st.tabs([
            "📝 New Note",
            "✨ Summary",
            "❓ Quiz",
            "✅ Grading"
        ], width="stretch")

        with tabs[0]: self._render_new_note_tab(api_key=api_key, model=model)
        with tabs[1]: self._render_summary_tab()
        with tabs[2]: self._render_quiz_tab(api_key=api_key, model=model)
        with tabs[3]: self._render_grading_tab()

    def _render_new_note_tab(self, api_key: str, model: str):
        with st.form("note_form"):
            note_content = st.text_area("Enter your note here.", height=300)
            st.markdown("###### Configure Your Quiz (Total 10 questions)")

            c1, c2, c3 = st.columns(3)
            with c1: st.number_input("Multiple Choice", min_value=0, max_value=10, value=0, step=1, key="multiple_choice_count", help="Number of multiple choice questions")
            with c2: st.number_input("Short Answer", min_value=0, max_value=10, value=0, step=1, key="short_answer_count", help="Number of short answer questions")
            with c3: st.number_input("Long Answer", min_value=0, max_value=10, value=0, step=1, key="long_answer_count", help="Number of long answer questions")
            
            quiz_structure = {
                "multiple_choice": st.session_state.multiple_choice_count,
                "short_answer": st.session_state.short_answer_count,
                "long_answer": st.session_state.long_answer_count
            }

            if st.form_submit_button("Submit", disabled=st.session_state.processing_note):
                if not api_key: st.error("Please enter your API key"); return
                if not note_content: st.error("Please enter your note"); return
                if sum(quiz_structure.values()) != 10: st.error("Please enter at least one question"); return
                st.session_state.processing_note = True
                st.rerun()
            
            if st.session_state.processing_note:
                self.controller.handle_note_submission(
                    api_key=api_key,
                    note=note_content,
                    quiz_structure=quiz_structure,
                    model=model
                )

            if st.session_state.note_submitted and not st.session_state.processing_note:
                flexible_success("Analysis is complete! Please check the results in the Summary tab.", alignment="center")

    def _render_summary_tab(self):
        if not st.session_state.note_submitted: st.info("Please submit a note first.")
        else: st.markdown(st.session_state.summary)

    def _render_quiz_tab(self, api_key: str, model: str):
        if not st.session_state.note_submitted: st.info("Please submit a note first.")
        else:
            with st.form("quiz_solve_form"):
                for i, one_question in enumerate(st.session_state.quiz):
                    st.markdown(f"**Question {i+1}: {one_question['question']}**")
                    if one_question["question_type"] == "multiple_choice":
                        one_question['user_answer'] = st.radio(
                            label="Select your answer",
                            options=one_question["options"],
                            key=f"user_answer_{i}",
                            label_visibility="collapsed"
                        )
                    else:
                        one_question['user_answer'] = st.text_area(
                            label=f"Enter your answer",
                            key=f"user_answer_{i}",
                            label_visibility="collapsed"
                        )
                    with st.expander("Preview answer"):
                        st.write(one_question['answer'])
                    st.divider()
                grade_submitted = st.form_submit_button("Grade", disabled=st.session_state.processing_quiz)
                if grade_submitted:
                    if not api_key: st.error("Please enter your API key"); return
                    if not st.session_state.quiz: st.error("Please enter your quiz"); return

                    st.session_state.processing_quiz = True
                    st.rerun()
                
                if st.session_state.processing_quiz:
                    self.controller.handle_quiz_grading(
                        api_key=api_key,
                        quiz=st.session_state.quiz,
                        model=model
                    )
                
                if st.session_state.graded and not st.session_state.processing_quiz:
                    flexible_success("Grading is completed! Please check the results in the Grading tab.", alignment="center")

    def _render_grading_tab(self):
        if not st.session_state.graded: st.info("Please solve the questions and click the 'Grade' button at .")
        else:
            individual_results = st.session_state.grading_result
            total_correct = 0
            total_partially_correct = 0
            total_incorrect = 0
            for i, result in enumerate(individual_results):
                if result.get("score") == "Correct":
                    total_correct += 1
                elif result.get("score") == "Partially Correct":
                    total_partially_correct += 1
                else:
                    total_incorrect += 1

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
                with st.expander(f"Question {i+1}: {result['question']}", expanded=True):
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