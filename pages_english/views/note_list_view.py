import json
import streamlit as st
from datetime import datetime
from st_flexible_callout_elements import flexible_success
from pages_english.controller import Controller
import logging
import traceback

SCORE_COLORS = {
    "Correct": "green",
    "Incorrect": "red",
    "Partially Correct": "yellow"
}

class NoteListView:
    def __init__(self, controller: Controller, language: str):
        try:
            if not controller:
                raise ValueError("Controller cannot be None")
            
            if not language or not language.strip():
                raise ValueError("Language cannot be empty")
            
            self.controller = controller
            self.language = language
        except Exception as e:
            logging.error(f"Failed to initialize NoteListView: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize NoteListView: {str(e)}")

    def render(self):
        try:
            st.title("Note List")
            
            # Search section
            st.markdown("### Search Notes")
            col2, col3 = st.columns([2, 2])
            
            with col2:
                try:
                    autocomplete_options = self.controller.repositories["note_repository"].get_all_note_names()
                    
                    title_content_search = st.selectbox(
                        "Title Search", 
                        options=[""] + autocomplete_options,
                        placeholder="Enter title to search...", 
                        key="title_content_search"
                    )
                except Exception as e:
                    logging.error(f"Error loading note names for autocomplete: {traceback.format_exc()}")
                    st.error("Failed to load note names for search")
                    title_content_search = ""

            with col3:
                try:
                    hashtag_options = self.controller.repositories["note_hashtag_repository"].get_all_hashtags()
                    hashtag_search = st.selectbox(
                        "Hashtag Search", 
                        options=[""] + hashtag_options,
                        placeholder="Enter hashtag to search...", 
                        key="hashtag_search"
                    )
                except Exception as e:
                    logging.error(f"Error loading hashtags for autocomplete: {traceback.format_exc()}")
                    st.error("Failed to load hashtags for search")
                    hashtag_search = ""

            if st.button("🔍", key="search_button", help="Search notes", use_container_width=True):
                st.rerun()

            # Get all notes with error handling
            try:
                all_notes = self.controller.repositories["note_repository"].get_all_notes()
            except Exception as e:
                logging.error(f"Error retrieving notes: {traceback.format_exc()}")
                st.error("Failed to retrieve notes")
                all_notes = []
            
            if not all_notes:
                st.info("No notes found. Create your first note in the 'New Note' tab!")
                return
            
            st.markdown(f"### Your Notes ({len(all_notes)} found)")
            
            # Sort options
            sort_option = st.selectbox(
                "Sort by",
                ["Newest First", "Oldest First"],
                key="note_sort_option"
            )

            # Filter notes based on search criteria
            try:
                filtered_notes = self._filter_notes(all_notes, hashtag_search, title_content_search)
            except Exception as e:
                logging.error(f"Error filtering notes: {traceback.format_exc()}")
                st.error("Failed to filter notes")
                filtered_notes = all_notes
            
            if not filtered_notes:
                st.warning("No notes found matching your search criteria.")
                return
            
            # Sort notes based on selection
            try:
                if sort_option == "Newest First":
                    filtered_notes = sorted(filtered_notes, key=lambda x: x[2], reverse=True)
                else:
                    filtered_notes = sorted(filtered_notes, key=lambda x: x[2])
            except Exception as e:
                logging.error(f"Error sorting notes: {traceback.format_exc()}")
                st.warning("Failed to sort notes")
                    
            for note_id, note_name, created_at in filtered_notes:
                try:
                    # Format the date with error handling
                    try:
                        if isinstance(created_at, str):
                            try:
                                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            except:
                                created_at = datetime.now()
                    except Exception as e:
                        logging.error(f"Error parsing date for note {note_id}: {traceback.format_exc()}")
                        created_at = datetime.now()
                    
                    formatted_date = created_at.strftime("%Y-%m-%d %H:%M")
                    
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 0.5])
                        
                        with col1:
                            if st.button(f"{note_name}", key=f"note_{note_id}", use_container_width=True):
                                # Navigate to note detail view
                                st.session_state.current_view = "note_detail"
                                st.session_state.selected_note_id = note_id
                                st.session_state.selected_note_name = note_name
                                st.rerun()
                        
                        with col2:
                            st.write(f"📅 {formatted_date}")
                        
                        with col3:
                            if st.button("🗑️", key=f"delete_{note_id}", help="Delete note"):
                                if st.session_state.get(f"confirm_delete_{note_id}", False):
                                    # Delete the note with error handling
                                    try:
                                        self.controller.repositories["note_repository"].delete_note(note_id)
                                        st.success(f"Note '{note_name}' deleted successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        logging.error(f"Error deleting note {note_id}: {traceback.format_exc()}")
                                        st.error(f"Failed to delete note '{note_name}'")
                                else:
                                    st.session_state[f"confirm_delete_{note_id}"] = True
                                    st.warning(f"Click delete again to confirm deletion of '{note_name}'")
                                    st.rerun()
                except Exception as e:
                    logging.error(f"Error rendering note {note_id}: {traceback.format_exc()}")
                    st.error(f"Error displaying note {note_id}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error rendering NoteListView: {traceback.format_exc()}")
            st.error(f"Failed to render note list view: {str(e)}")

    def _filter_notes(self, all_notes, hashtag_search, title_content_search):
        """Filter notes based on hashtag and title/content search criteria"""
        try:
            filtered_notes = []
            
            for note_id, note_name, created_at in all_notes:
                try:
                    hashtag_match = True
                    if hashtag_search:
                        try:
                            hashtags = self.controller.repositories["note_hashtag_repository"].get_hashtags_by_note_id(note_id)
                            hashtag_match = any(hashtag_search.lower() in hashtag.lower() for hashtag in hashtags)
                        except Exception as e:
                            logging.error(f"Error retrieving hashtags for note {note_id}: {traceback.format_exc()}")
                            hashtag_match = False
                    
                    title_content_match = True
                    if title_content_search:
                        title_content_match = title_content_search.lower() in note_name.lower()
                    
                    if hashtag_match and title_content_match:
                        filtered_notes.append((note_id, note_name, created_at))
                except Exception as e:
                    logging.error(f"Error filtering note {note_id}: {traceback.format_exc()}")
                    continue
            
            return filtered_notes
        except Exception as e:
            logging.error(f"Error in _filter_notes: {traceback.format_exc()}")
            return all_notes  # Return all notes if filtering fails