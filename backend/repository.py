from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import UserProfile, ChatHistory
from datetime import datetime, timezone

class SessionRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    # --- UserProfile ---
    def get_user_profile(self, user_id: str) -> UserProfile | None:
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def upsert_user_profile(self, user_id: str, updates: dict):
        profile = self.get_user_profile(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)

        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        self.db.commit()

    def delete_user_profile(self, user_id: str):
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).delete(synchronize_session=False)

    # --- ChatHistory ---
    def get_chat_history(self, user_id: str, limit: int = 10) -> list[dict]:
        records = (
            self.db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [{"role": r.role, "content": r.content, "timestamp": r.timestamp.isoformat()} for r in reversed(records)]

    def add_chat_message(self, user_id: str, role: str, content: str):
        entry = ChatHistory(user_id=user_id, role=role, content=content, timestamp=datetime.now(timezone.utc))
        self.db.add(entry)
        self.db.commit()
