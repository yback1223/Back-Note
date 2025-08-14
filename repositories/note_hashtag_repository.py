import sqlite3
from datetime import datetime
import logging
import traceback

class NoteHashtagRepository:
    def __init__(self, conn: sqlite3.Connection):
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error(f"Failed to initialize NoteHashtagRepository: {traceback.format_exc()}")
            raise Exception(f"Failed to initialize NoteHashtagRepository: {str(e)}")

    def insert_note_hashtags(self, note_id: int, hashtags: list[str]) -> None:
        """노트에 해시태그들을 추가합니다."""
        try:
            # Input validation
            if not isinstance(note_id, int) or note_id <= 0:
                raise ValueError("Invalid note ID")
            
            if not isinstance(hashtags, list):
                raise ValueError("Hashtags must be a list")
            
            if not hashtags:
                logging.info(f"No hashtags to insert for note ID {note_id}")
                return
            
            for hashtag in hashtags:
                if not isinstance(hashtag, str) or not hashtag.strip():
                    logging.warning(f"Skipping invalid hashtag: {hashtag}")
                    continue
                
                # 먼저 해시태그가 존재하는지 확인하고, 없으면 생성
                try:
                    self.cursor.execute("SELECT note_hashtag_id FROM note_hashtag WHERE hashtag = ?", (hashtag,))
                    result = self.cursor.fetchone()
                    
                    if result:
                        note_hashtag_id = result[0]
                    else:
                        self.cursor.execute("INSERT INTO note_hashtag (hashtag) VALUES (?)", (hashtag,))
                        note_hashtag_id = self.cursor.lastrowid
                    
                    # 노트와 해시태그 연결
                    try:
                        self.cursor.execute(
                            "INSERT INTO note_note_hashtags (note_id, note_hashtag_id) VALUES (?, ?)", 
                            (note_id, note_hashtag_id)
                        )
                    except sqlite3.IntegrityError:
                        # 이미 연결되어 있는 경우 무시
                        logging.info(f"Hashtag '{hashtag}' already linked to note ID {note_id}")
                        pass
                        
                except sqlite3.Error as e:
                    logging.error(f"Database error processing hashtag '{hashtag}': {str(e)}")
                    continue
            
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database error in insert_note_hashtags: {traceback.format_exc()}")
            raise Exception(f"Failed to insert note hashtags: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in insert_note_hashtags: {traceback.format_exc()}")
            raise Exception(f"Unexpected error inserting note hashtags: {str(e)}")

    def get_hashtags_by_note_id(self, note_id: int) -> list[str]:
        try:
            if not isinstance(note_id, int) or note_id <= 0:
                raise ValueError("Invalid note ID")
            
            self.cursor.execute("""
                SELECT nh.hashtag 
                FROM note_hashtag nh
                JOIN note_note_hashtags nnh ON nh.note_hashtag_id = nnh.note_hashtag_id
                WHERE nnh.note_id = ? AND nnh.deleted_at IS NULL
            """, (note_id,))
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Database error in get_hashtags_by_note_id: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve hashtags: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_hashtags_by_note_id: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving hashtags: {str(e)}")
    
    def get_all_hashtags(self) -> list[str]:
        try:
            self.cursor.execute("SELECT hashtag FROM note_hashtag")
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Database error in get_all_hashtags: {traceback.format_exc()}")
            raise Exception(f"Failed to retrieve all hashtags: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in get_all_hashtags: {traceback.format_exc()}")
            raise Exception(f"Unexpected error retrieving all hashtags: {str(e)}")
    
    def search_hashtags(self, search_term: str) -> list[str]:
        """Search hashtags by partial match for autocomplete"""
        try:
            if not isinstance(search_term, str):
                raise ValueError("Search term must be a string")
            
            if not search_term.strip():
                return []
            
            self.cursor.execute("SELECT hashtag FROM note_hashtag WHERE hashtag LIKE ? LIMIT 10", (f"%{search_term}%",))
            return [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Database error in search_hashtags: {traceback.format_exc()}")
            raise Exception(f"Failed to search hashtags: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in search_hashtags: {traceback.format_exc()}")
            raise Exception(f"Unexpected error searching hashtags: {str(e)}")

    def delete_hashtag_from_note(self, note_id: int, hashtag: str) -> bool:
        """노트에서 특정 해시태그를 삭제합니다."""
        try:
            # Input validation
            if not isinstance(note_id, int) or note_id <= 0:
                raise ValueError("Invalid note ID")
            
            if not isinstance(hashtag, str) or not hashtag.strip():
                raise ValueError("Invalid hashtag")
            
            self.cursor.execute("""
                UPDATE note_note_hashtags 
                SET deleted_at = CURRENT_TIMESTAMP 
                WHERE note_id = ? AND note_hashtag_id = (
                    SELECT note_hashtag_id FROM note_hashtag WHERE hashtag = ?
                )
            """, (note_id, hashtag))
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                logging.warning(f"No hashtag '{hashtag}' found for note ID {note_id}")
            
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Database error in delete_hashtag_from_note: {traceback.format_exc()}")
            raise Exception(f"Failed to delete hashtag from note: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in delete_hashtag_from_note: {traceback.format_exc()}")
            raise Exception(f"Unexpected error deleting hashtag from note: {str(e)}")