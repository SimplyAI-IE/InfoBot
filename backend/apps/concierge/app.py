from ...base_app import BaseApp

class ConciergeApp(BaseApp):
    def format_user_context(self, user_context: dict) -> str:
        # Implement the method logic here
        return f"User Context: {user_context}"

    def render_profile_field(self, field_name: str, field_value: str) -> str:
        # Implement the method logic here
        return f"{field_name}: {field_value}"
