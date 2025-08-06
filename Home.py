import streamlit as st
from streamlit_option_menu import option_menu
from pages_korean import home as home_ko, new_note as new_note_ko, my_db as my_db_ko
from pages_english import home as home_en, new_note as new_note_en, my_db as my_db_en

if "lang" not in st.session_state:
    st.session_state.lang = "en"

st.set_page_config(
    page_title="Back Note",
    page_icon="🔙",
    layout="wide",
)

PAGES_KO = {
    "홈": home_ko,
    "새 노트": new_note_ko,
    "내 기록": my_db_ko
}

PAGES_EN = {
    "Home": home_en,
    "New note": new_note_en,
    "My records": my_db_en
}

lang = st.sidebar.selectbox("Language / 언어", ["English", "한국어"])

if lang == "한국어":
    options = list(PAGES_KO.keys())
    page_dict = PAGES_KO

else:
    options = list(PAGES_EN.keys())
    page_dict = PAGES_EN

with st.sidebar:
    selection = option_menu(
        menu_title=None,
        options=options,
        default_index=0,
        orientation="vertical",
        icons=['house-door', 'pencil', 'archive'],
        styles={
            "nav-link": {
                "color": "var(--text-color)",
                "--hover-color": "#a2a4a8"
            },
            "nav-link-selected": {
                "background-color": "transparent",       # 배경은 투명하게
                "color": "var(--text-color)",            # ✅ 이 부분이 핵심: 테마에 맞는 텍스트 색상 사용
                "font-weight": "bold",                   # 굵은 글씨로 선택 표시
            }
        }
    )

page = page_dict[selection]
page.app()
