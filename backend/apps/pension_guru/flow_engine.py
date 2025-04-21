import os
import yaml
import logging
from backend.models import SessionLocal
from backend.memory import MemoryManager
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)

class PensionFlow:
    def __init__(self, profile: Optional[dict[str, Any]], user_id: str):
        self.profile: Optional[dict[str, Any]] = profile
        self.user_id: str = user_id
        self.flow_path: str = os.path.join(os.path.dirname(__file__), "conversation_flow.yaml")
        with open(self.flow_path, "r") as f:
            self.flow: dict[str, dict[str, Any]] = yaml.safe_load(f)["conversation_flow"]

        self.db = SessionLocal()
        self.memory = MemoryManager(self.db)

        self.current_step_name: str = self._get_profile_value("pending_step", "step_1_welcome_intro")
        logger.debug(f"PensionFlow initialized for user {user_id}. Current step: {self.current_step_name}")

    def step(self) -> Optional[str]:
        try:
            if not self.current_step_name:
                return None

            current_node = self.flow.get(self.current_step_name)
            if not current_node:
                logger.error(f"Invalid step '{self.current_step_name}'")
                self.memory.save_user_profile(self.user_id, {"pending_step": None})
                return None

            if "branching_logic" in current_node:
                region = self._get_profile_value("region")
                target_flow: Optional[str] = None
                fallback_prompt: Optional[str] = None

                if region:
                    for branch in current_node["branching_logic"]:
                        if region.lower() in branch.get("condition", "").lower():
                            target_flow = branch.get("target_flow")
                            break

                    if not target_flow:
                        fallback = current_node["branching_logic"][-1]
                        if "condition" not in fallback or "other" in fallback.get("condition", "").lower():
                            fallback_prompt = fallback.get("prompt")
                            target_flow = fallback.get("target_flow")

                if target_flow:
                    self.memory.save_user_profile(self.user_id, {"pending_step": target_flow})
                    self.profile = self.memory.get_user_profile(self.user_id)
                    self.current_step_name = target_flow
                    return self.step()
                elif fallback_prompt:
                    return fallback_prompt
                return current_node.get("script_prompt")

            expected_field = current_node.get("expect_field")
            next_step_name = current_node.get("next_step")

            if expected_field:
                if self._get_profile_value(expected_field) is not None:
                    self.memory.save_user_profile(self.user_id, {"pending_step": next_step_name})
                    self.profile = self.memory.get_user_profile(self.user_id)
                    if next_step_name:
                         self.current_step_name = next_step_name
                    return self.step()
                return current_node.get("script_prompt")

            self.memory.save_user_profile(self.user_id, {"pending_step": next_step_name})
            return current_node.get("script_prompt")
        finally:
            self.db.close()

    def _get_profile_value(self, key: str, default: Optional[str] = None) -> Any:
        if isinstance(self.profile, dict):
            return self.profile.get(key, default)
        return default
