import streamlit as st
from streamlit_option_menu import option_menu
from pages_english.controller import Controller
import logging
import traceback

class HomeView:
    def __init__(self, controller: Controller, language: str):
        try:
            if not controller:
                raise ValueError("Controller cannot be None")
            
            if not language or not language.strip():
                raise ValueError("Language cannot be empty")
            
            self.controller = controller
            self.language = language
        except Exception as e:
            logging.error(f"Failed to initialize HomeView: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize HomeView: {str(e)}")

    def render(self):
        try:
            st.title("Home")
            st.write("Welcome to the Home page")
            
            # Add some basic content to make the home page more informative
            st.markdown("""
            ### 🏠 Welcome to Back Note
            
            This application helps you:
            - 📝 **Create and manage notes** with AI-powered analysis
            - 🧠 **Generate quizzes** from your notes automatically
            - 📊 **Review and grade** your quiz performance
            - 🏷️ **Organize notes** with hashtags and search functionality
            
            ### 🚀 Getting Started
            
            1. **New Note**: Create your first note with AI analysis
            2. **Note List**: View and manage all your notes
            3. **Review**: Take quizzes and see your progress
            
            ### 💡 Tips
            
            - Use descriptive note names for better organization
            - Add relevant hashtags to make searching easier
            - Review quiz results to improve your understanding
            """)
            
        except Exception as e:
            logging.error(f"Error rendering HomeView: {traceback.format_exc()}")
            st.error(f"Failed to render home page: {str(e)}")

    def _render_home_tab(self):
        try:
            # This method is currently empty but kept for future use
            pass
        except Exception as e:
            logging.error(f"Error in _render_home_tab: {traceback.format_exc()}")
            st.error(f"Failed to render home tab: {str(e)}")