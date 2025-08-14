from pages_english.controller import Controller
from pages_english.views.home_view import HomeView
from pages_english.views.new_note_view import NewNoteView
from pages_english.views.note_list_view import NoteListView
from pages_english.views.note_detail_view import NoteDetailView
import streamlit as st
from streamlit_option_menu import option_menu
from repositories import my_db
from repositories.api_key_repository import ApiKeyRepository
from repositories.note_repository import NoteRepository
from repositories.note_hashtag_repository import NoteHashtagRepository
from repositories.question_repository import QuestionRepository
from repositories.option_repository import OptionRepository
from repositories.grading_repository import GradingRepository
import traceback
import logging

class App:
    def __init__(self):
        try:
            # Initialize database connection
            self.db = my_db.MyDB()
            self.db.connect()
            
            # Initialize repositories with error handling
            self.repositories = {}
            repository_classes = {
                "api_key_repository": ApiKeyRepository,
                "note_repository": NoteRepository,
                "note_hashtag_repository": NoteHashtagRepository,
                "question_repository": QuestionRepository,
                "option_repository": OptionRepository,
                "grading_repository": GradingRepository
            }
            
            for repo_name, repo_class in repository_classes.items():
                try:
                    self.repositories[repo_name] = repo_class(self.db.conn)
                except Exception as e:
                    st.error(f"Failed to initialize {repo_name}: {str(e)}")
                    logging.error(f"Repository initialization error for {repo_name}: {traceback.format_exc()}")
                    raise
            
            # Initialize controller
            self.controller = Controller(self.repositories)
            
            # Initialize language and views
            self.language = "en"
            self.new_note_view = NewNoteView(self.controller, self.language)
            self.home_view = HomeView(self.controller, self.language)
            self.note_list_view = NoteListView(self.controller, self.language)
            self.note_detail_view = NoteDetailView(self.controller, self.language)
            
            # Initialize sidebar
            self.side_bar = {
                "Home": self.home_view,
                "New Note": self.new_note_view,
                "Note List": self.note_list_view
            }
            
        except Exception as e:
            st.error(f"Failed to initialize application: {str(e)}")
            logging.error(f"Application initialization error: {traceback.format_exc()}")
            raise

    def run(self):
        try:
            # Initialize session state with error handling
            if 'current_view' not in st.session_state:
                st.session_state.current_view = "main"
            
            if 'previous_sidebar_selection' not in st.session_state:
                st.session_state.previous_sidebar_selection = None
            
            # Validate language and sidebar configuration
            if self.language == "en":
                options = list(self.side_bar.keys())
                page_dict = self.side_bar
            else:
                st.error(f"Unsupported language: {self.language}")
                return

            # Render sidebar with error handling
            try:
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
            except Exception as e:
                st.error(f"Failed to render sidebar: {str(e)}")
                logging.error(f"Sidebar rendering error: {traceback.format_exc()}")
                return

            # Handle navigation logic with error handling
            try:
                if st.session_state.previous_sidebar_selection != selection:
                    st.session_state.current_view = "main"
                    st.session_state.previous_sidebar_selection = selection

                # Special handling for Note List - if already on note detail and Note List is clicked again
                if (st.session_state.current_view == "note_detail" and 
                    selection == "Note List" and 
                    st.session_state.previous_sidebar_selection == "Note List"):
                    st.session_state.current_view = "main"
                    # Clear note detail related session state
                    if 'selected_note_id' in st.session_state:
                        del st.session_state.selected_note_id
                    if 'selected_note_name' in st.session_state:
                        del st.session_state.selected_note_name
            except Exception as e:
                st.error(f"Navigation error: {str(e)}")
                logging.error(f"Navigation error: {traceback.format_exc()}")
                return

            # Render appropriate view with error handling
            try:
                if st.session_state.current_view == "note_detail":
                    if hasattr(self, 'note_detail_view'):
                        self.note_detail_view.render()
                    else:
                        st.error("Note detail view not available")
                        st.session_state.current_view = "main"
                        st.rerun()
                else:
                    if selection in page_dict:
                        page = page_dict[selection]
                        if hasattr(page, 'render'):
                            page.render()
                        else:
                            st.error(f"Page {selection} does not have a render method")
                    else:
                        st.error(f"Page {selection} not found in page dictionary")
            except Exception as e:
                st.error(f"View rendering error: {str(e)}")
                logging.error(f"View rendering error: {traceback.format_exc()}")
                # Fallback to main view
                st.session_state.current_view = "main"
                st.rerun()
                
        except Exception as e:
            st.error(f"Critical application error: {str(e)}")
            logging.error(f"Critical application error: {traceback.format_exc()}")
            st.stop()