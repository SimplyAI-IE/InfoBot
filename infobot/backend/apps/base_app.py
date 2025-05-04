from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseApp(ABC):

    @abstractmethod
    def extract_user_data(self, user_id: str, msg: str) -> dict[str, Any]: ...

    @abstractmethod
    def block_response(
        self, user_input: str, profile: Optional[dict[str, Any]]
    ) -> Optional[str]: ...

    @abstractmethod
    def tips_reply(self) -> str: ...

    @abstractmethod
    def should_offer_tips(self, reply: str) -> bool: ...

    @abstractmethod
    def wants_tips(
        self, profile: Optional[dict[str, Any]], msg: str, history: list[dict[str, str]]
    ) -> bool: ...

    @abstractmethod
    def format_user_context(self, profile: Optional[dict[str, Any]]) -> str: ...

    @abstractmethod
    def render_profile_field(
        self, field: str, profile: Optional[dict[str, Any]]
    ) -> str: ...

    @abstractmethod
    def get_pension_calculation_reply(self, user_id: str) -> str: ...

    def pre_prompt(
        self, profile: Optional[dict[str, Any]], user_id: str
    ) -> Optional[str]:
        return None
