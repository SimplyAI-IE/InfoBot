from sqlalchemy.orm import Session
from backend.repository import SessionRepository
from typing import Optional, Any


class MemoryManager:
    def __init__(self, db_session: Session):
        self.repo = SessionRepository(db_session)

    # --- SessionData (if you later reintroduce it) ---
    def load_session(self, session_id: str) -> Optional[dict]:
        session = self.repo.get_session_by_id(session_id)
        return session.data if session else None

    def save_session(self, session_id: str, data: dict[str, Any]) -> None:
        self.repo.upsert_session(session_id, data)

    def delete_session(self, session_id: str) -> None:
        self.repo.delete_session(session_id)

    # --- Profile ---
    def get_user_profile(self, user_id: str) -> Optional[Any]:
        return self.repo.get_user_profile(user_id)

    def save_user_profile(self, user_id: str, updates: dict[str, Any]) -> None:
        self.repo.upsert_user_profile(user_id, updates)

    # --- Chat ---
    def get_chat_history(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        return self.repo.get_chat_history(user_id, limit)

    def save_chat_message(self, user_id: str, role: str, content: str) -> None:
        self.repo.add_chat_message(user_id, role, content)
