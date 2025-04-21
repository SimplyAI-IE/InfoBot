# backend/memory.py

from sqlalchemy.orm import Session
from .repository import SessionRepository


class MemoryManager:
    def __init__(self, db_session: Session):
        self.repo = SessionRepository(db_session)

    # --- SessionData (not core to chat, but included if needed) ---
    def load_session(self, session_id: str) -> dict | None:
        session = self.repo.get_session_by_id(session_id)
        return session.data if session else None

    def save_session(self, session_id: str, data: dict):
        self.repo.upsert_session(session_id, data)

    def delete_session(self, session_id: str):
        self.repo.delete_session(session_id)

    # --- Profile ---
    def get_user_profile(self, user_id: str):
        return self.repo.get_user_profile(user_id)

    def save_user_profile(self, user_id: str, updates: dict):
        self.repo.upsert_user_profile(user_id, updates)

    # --- Chat ---
    def get_chat_history(self, user_id: str, limit: int = 10):
        return self.repo.get_chat_history(user_id, limit)

    def save_chat_message(self, user_id: str, role: str, content: str):
        self.repo.add_chat_message(user_id, role, content)
