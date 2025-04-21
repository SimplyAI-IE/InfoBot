import os
import yaml
import logging
from backend.models import SessionLocal
from backend.memory import MemoryManager

logger = logging.getLogger(__name__)

class PensionFlow:
    def __init__(self, profile, user_id):
        self.profile = profile
        self.user_id = user_id
        self.flow_path = os.path.join(os.path.dirname(__file__), "conversation_flow.yaml")
        with open(self.flow_path, "r") as f:
            self.flow = yaml.safe_load(f)["conversation_flow"]

        self.db = SessionLocal()
        self.memory = MemoryManager(self.db)

        self.current_step_name = self._get_profile_value("pending_step", "step_1_welcome_intro")
        logger.debug(f"PensionFlow initialized for user {user_id}. Current step: {self.current_step_name}")

    def step(self):
        try:
            if not self.current_step_name:
                logger.debug(f"🧭 FLOW {self.user_id}: No current step, returning None.")
                return None

            current_node = self.flow.get(self.current_step_name)
            if not current_node:
                logger.error(f"🧭 FLOW ERROR {self.user_id}: Step '{self.current_step_name}' not found!")
                self.memory.save_user_profile(self.user_id, {"pending_step": None})
                return None

            logger.info(f"🧭 FLOW {self.user_id}: Processing step '{self.current_step_name}'")

            if "branching_logic" in current_node:
                region = self._get_profile_value("region")
                target_flow = None
                fallback_prompt = None

                if region:
                    region_lower = region.lower()
                    for branch in current_node["branching_logic"]:
                        condition = branch.get("condition", "")
                        if isinstance(condition, str) and region_lower in condition.lower():
                            target_flow = branch.get("target_flow")
                            if target_flow:
                                break
                    if not target_flow and len(current_node["branching_logic"]) > 0:
                        fallback_branch = current_node["branching_logic"][-1]
                        if "condition" not in fallback_branch or "other" in fallback_branch.get("condition", "").lower():
                            fallback_prompt = fallback_branch.get("prompt")
                            target_flow = fallback_branch.get("target_flow")

                if target_flow:
                    logger.info(f"🧭 FLOW {self.user_id}: Branching to '{target_flow}'")
                    self.memory.save_user_profile(self.user_id, {"pending_step": target_flow})
                    self.profile = self.memory.get_user_profile(self.user_id)
                    self.current_step_name = target_flow
                    return self.step()
                elif fallback_prompt:
                    logger.warning(f"🧭 FLOW {self.user_id}: Branching fallback for '{self.current_step_name}'")
                    return fallback_prompt
                else:
                    return current_node.get("script_prompt")

            expected_field = current_node.get("expect_field")
            next_step_name = current_node.get("next_step")

            if expected_field:
                field_value = self._get_profile_value(expected_field)
                if field_value is not None:
                    logger.info(f"🧭 FLOW {self.user_id}: Field '{expected_field}' is fulfilled. Advancing.")
                    self.memory.save_user_profile(self.user_id, {"pending_step": next_step_name})
                    self.profile = self.memory.get_user_profile(self.user_id)
                    self.current_step_name = next_step_name
                    return self.step()
                else:
                    return current_node.get("script_prompt")
            else:
                logger.info(f"🧭 FLOW {self.user_id}: Advancing from '{self.current_step_name}' to '{next_step_name}'")
                self.memory.save_user_profile(self.user_id, {"pending_step": next_step_name})
                return current_node.get("script_prompt")

        finally:
            self.db.close()

    def _get_profile_value(self, key, default=None):
        if isinstance(self.profile, dict):
            return self.profile.get(key, default)
        elif self.profile is not None:
            return getattr(self.profile, key, default)
        return default
