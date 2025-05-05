from typing import Any

from backend.apps.base_app import BaseApp


class ConciergeApp(BaseApp):
    def extract_user_data(self, user_id: str, msg: str) -> dict[str, Any]:
        return {}

    def block_response(self, user_input: str, profile: dict[str, Any] | None) -> str | None:
        return None

    def tips_reply(self) -> str:
        return "Here are some helpful tips."

    def should_offer_tips(self, reply: str) -> bool:
        return False

    def wants_tips(self, profile: dict[str, Any] | None, msg: str, history: list[dict[str, str]]) -> bool:
        return False

    def format_user_context(self, profile: dict[str, Any] | None) -> str:
        return f"Formatted context: {profile}"

    def render_profile_field(self, field: str, profile: dict[str, Any] | None) -> str:
        return f"{field}: {profile.get(field, 'N/A') if profile else 'N/A'}"

    def get_pension_calculation_reply(self, user_id: str) -> str:
        return "Pension calculation is currently unavailable."
