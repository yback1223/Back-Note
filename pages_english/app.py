from pages_english.controller import Controller
from pages_english.views.home_view import HomeView
from pages_english.views.new_note_view import NewNoteView
import streamlit as st
from streamlit_option_menu import option_menu

class App:
    def __init__(self):
        self.controller = Controller()
        self.language = "en"
        self.new_note_view = NewNoteView(self.controller, self.language)
        self.home_view = HomeView(self.controller, self.language)
        self.side_bar = {
            "Home": self.home_view,
            "New Note": self.new_note_view,
        }

    def run(self):
        if self.language == "en":
            options = list(self.side_bar.keys())
            page_dict = self.side_bar

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
                        "background-color": "transparent",
                        "color": "var(--text-color)"
                    }
                }
            )

        page = page_dict[selection]
        page.render()