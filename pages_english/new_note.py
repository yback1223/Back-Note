import json
import streamlit as st
from st_flexible_callout_elements import flexible_success
import time
from core.submit_note import submit_note
from core.submit_quiz import submit_quiz

SCORE_COLORS = {
    "Correct": "green",
    "Partially Correct": "orange",
    "Incorrect": "red"
}

def init_session_state():
    if 'note_submitted' not in st.session_state:
        st.session_state.note_submitted = False
    if 'summary' not in st.session_state:
        st.session_state.summary = ""
    if 'quiz' not in st.session_state:
        st.session_state.quiz = []
    if 'graded' not in st.session_state:
        st.session_state.graded = False
    if 'grading_result' not in st.session_state:
        st.session_state.grading_result = ""

@st.dialog("Are you sure you want to erase all existing results and create a new note?")
def reset_new_note_dialog():
    st.warning("By clicking the 'Erase' button, all existing summary, quiz, and grading results will be erased and you can start a new note.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Erase", type="primary", use_container_width=True):
            st.session_state.note_submitted = False
            st.session_state.graded = False
            st.session_state.grading_result = ""
            st.session_state.summary = ""
            st.session_state.quiz = []
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

@st.dialog("Are you sure you want to erase grading results and solve the quiz again?")
def reset_grading_dialog():
    st.warning("By clicking the 'Erase' button, all existing grading results will be erased and you can solve the quiz again.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Erase", type="primary", use_container_width=True):
            st.session_state.graded = False
            st.session_state.grading_result = ""
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

def app():
    init_session_state()
    if 'analyzing' not in st.session_state:
        st.session_state.analyzing = False
    if 'grading' not in st.session_state:
        st.session_state.grading = False

    col1, col2 = st.columns([1, 1])

    with col1:
        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="Enter your API key here.",
            help="The Gemini API key will not be saved if you leave this page."
        )

    with col2:
        gemini_model = st.selectbox(
            "Gemini Model",
            ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
            help="Select the Gemini model to use."
        )


    tab_new, tab_summary, tab_quiz, tab_grading = st.tabs([
        "📝 New Note",
        "✨ Summary",
        "❓ Quiz",
        "✅ Grading"
    ], width="stretch")

    with tab_new:

        with st.form("note_form"):
            note_content = st.text_area(
                "Enter your note here.", 
                height=300
            )

            if 'mc_count' not in st.session_state:
                st.session_state.mc_count = 0
            if 'sa_count' not in st.session_state:
                st.session_state.sa_count = 0
            if 'la_count' not in st.session_state:
                st.session_state.la_count = 0


            st.markdown("###### Configure Your Quiz (Total 10 questions)")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.number_input(
                    "Multiple Choice",
                    min_value=0,
                    max_value=10,
                    key="mc_count"
                )
            with col2:
                st.number_input(
                    "Short Answer",
                    min_value=0,
                    max_value=10,
                    key="sa_count"
                )
            with col3:
                st.number_input(
                    "Long Answer",
                    min_value=0,
                    max_value=10,
                    key="la_count"
                )
            submitted = st.form_submit_button("Submit and Analyze")

            if submitted:

                quiz_type_structure = {
                    "multiple_choice": st.session_state.mc_count,
                    "short_answer": st.session_state.sa_count,
                    "long_answer": st.session_state.la_count,
                    "total": st.session_state.mc_count + st.session_state.sa_count + st.session_state.la_count
                }
                
                if not api_key_input:
                    st.error("Please enter your Gemini API key first.")
                elif not note_content:
                    st.error("Please enter your note.")
                elif st.session_state.mc_count + st.session_state.sa_count + st.session_state.la_count != 10:
                    st.error("Please check the total number of questions. It should be 10.")
                elif st.session_state.note_submitted:
                    reset_new_note_dialog()
                else:
                    with st.spinner("AI is analyzing your note and generating questions..."):
                        full_prompt_json, result_json = submit_note(
                            api_key=api_key_input.strip(), 
                            note=note_content, 
                            quiz_type_structure=quiz_type_structure,
                            model=gemini_model
                        )

                        st.session_state.summary = result_json["summary"]
                        st.session_state.quiz = result_json["quiz"]

                        st.session_state.note_submitted = True
                        flexible_success("Analysis is complete! Please check the results in the Summary tab.", alignment="center")

    with tab_summary:
        if not st.session_state.note_submitted:
            st.info("Please submit your note first.")
        else:
            st.markdown(st.session_state.summary)

    with tab_quiz:
        if not st.session_state.note_submitted:
            st.info("Please submit your note first.")
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

                grade_submitted = st.form_submit_button("Grade")

                if grade_submitted:
                    with open("quiz_with_answers.json", "w", encoding="utf-8") as f:
                        json.dump(st.session_state.quiz, f, indent=4, ensure_ascii=False)
                        
                    with st.spinner("AI is grading..."):
                        full_prompt_json_for_quiz, result_json_for_quiz = submit_quiz(
                            api_key=api_key_input.strip(), 
                            quiz=st.session_state.quiz,
                            model=gemini_model
                        )
                        
                        st.session_state.grading_result = result_json_for_quiz
                        
                        st.session_state.graded = True
                        flexible_success("Grading is completed! Please check the results in the Grading tab.", alignment="center")


    with tab_grading:
        if not st.session_state.graded:
            st.info("Please solve the questions and click the 'Grade' button at .")
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
