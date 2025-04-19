from abc import ABC, abstractmethod

class BaseApp(ABC):
    @abstractmethod
    def extract_user_data(self, user_id: str, msg: str) -> None:
        pass

    @abstractmethod
    def block_response(self, msg: str, profile: dict) -> str | None:
        pass

    @abstractmethod
    def wants_tips(self, profile: dict, msg: str, history: list) -> bool:
        pass

    @abstractmethod
    def tips_reply(self) -> str:
        pass

    @abstractmethod
    def should_offer_tips(self, response: str) -> bool:
        pass

    @abstractmethod
    def render_profile_field(self, field: str, profile: dict) -> str:
        pass

    @abstractmethod
    def format_user_context(self, profile: dict) -> str:
        pass

    def pre_prompt(self, profile, user_id: str) -> str | None:
        """
        Optionally return a scripted prompt before GPT response generation.
        This allows structured flows before GPT takes over.
        """
        return None
