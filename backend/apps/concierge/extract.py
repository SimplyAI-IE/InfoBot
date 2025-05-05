import re
from typing import Any

from backend.apps.base_app import BaseApp
from backend.memory import MemoryManager
from backend.models import SessionLocal


class ConciergeApp(BaseApp):
    def extract_user_data(self, user_id: str, message: str) -> dict[str, Any]:
        return {}

    def block_response(self, message: str, profile: dict[str, Any] | None) -> str | None:
        return None

    def wants_tips(self, profile: dict[str, Any] | None, message: str, history: list[dict[str, str]]) -> bool:
        return False

    def tips_reply(self) -> str:
        return "Here are some great local recommendations!"

    def get_pension_calculation_reply(self, user_id: str) -> str:
        return ""

    def should_offer_tips(self, reply: str) -> bool:
        return "recommend" in reply.lower()

    def format_user_context(self, profile: dict[str, Any] | None) -> str:
        return f"Formatted context: {profile}"

    def render_profile_field(self, field: str, profile: dict[str, Any] | None) -> str:
        return f"{field}: {profile.get(field, 'N/A') if profile else 'N/A'}"



def extract_user_data(user_id: str, msg: str) -> dict[str, Any] | None:
    msg_lower = msg.lower()

    db = SessionLocal()
    memory = MemoryManager(db)
    try:
        # --- Extract party size ---
        party_match = re.search(r"(table|for|party)\s*(of)?\s*(\d+)", msg_lower)
        if party_match:
            memory.save_user_profile(user_id, {"party_size": int(party_match.group(3))})

        # --- Extract time ---
        time_match = re.search(r"\b(\d{1,2})(:\d{2})?\s*(am|pm)?\b", msg_lower)
        if time_match:
            memory.save_user_profile(user_id, {"time": time_match.group(0)})

        # --- Extract date ---
        if "tonight" in msg_lower:
            memory.save_user_profile(user_id, {"date": "today"})
        elif "tomorrow" in msg_lower:
            memory.save_user_profile(user_id, {"date": "tomorrow"})

        # --- Extract cuisine ---
        cuisine_match = re.search(r"(italian|indian|thai|sushi|steak|vegan)", msg_lower)
        if cuisine_match:
            memory.save_user_profile(user_id, {"cuisine": cuisine_match.group(1)})

        return memory.get_user_profile(user_id)
    finally:
        db.close()
