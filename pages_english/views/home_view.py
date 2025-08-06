import streamlit as st
from streamlit_option_menu import option_menu
from pages_english.controller import Controller

class HomeView:
    def __init__(self, controller: Controller, language: str):
        self.controller = controller
        self.language = language

    def render(self):
        st.title("Home")
        st.write("Welcome to the Home page")

    def _render_home_tab(self):
        pass