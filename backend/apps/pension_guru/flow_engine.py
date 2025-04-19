import os
import yaml
from memory import save_user_profile

class PensionFlow:
    def __init__(self, profile, user_id):
        self.profile = profile
        self.user_id = user_id
        self.flow_path = os.path.join(os.path.dirname(__file__), "conversation_flow.yaml")
        with open(self.flow_path, "r") as f:
            self.flow = yaml.safe_load(f)["conversation_flow"]

        if isinstance(profile, dict):
            self.current_step = profile.get("pending_step", "step_1_welcome_intro")
        else:
            self.current_step = getattr(profile, "pending_step", "step_1_welcome_intro")

    def step(self):
        current = self.current_step
        node = self.flow.get(current, {})
        print(f"🧭 FLOW: at step {self.current_step}")

        # Enforce one-question-one-answer
        expected = node.get("expect_field")
        if expected and not self._get_profile_value(expected):
            return node.get("script_prompt")

        # Script prompt, advance only if expected field is filled
        if "script_prompt" in node:
            next_step = node.get("next_step")
            if next_step:
                self.profile = save_user_profile(self.user_id, "pending_step", next_step)
            else:
                self.profile = save_user_profile(self.user_id, "pending_step", None)
            return node["script_prompt"]

        # Handle branching logic
        if "branching_logic" in node:
            region = self._get_profile_value("region")
            if region:
                for branch in node["branching_logic"]:
                    if region.lower() in branch["condition"].lower():
                        target = branch.get("target_flow")
                        if target:
                            self.profile = save_user_profile(self.user_id, "pending_step", target)
                            self.current_step = target
                            return self.step()
            fallback = node["branching_logic"][-1].get("prompt")
            return fallback or None

        self.profile = save_user_profile(self.user_id, "pending_step", None)
        return None


    def _get_profile_value(self, key):
        if isinstance(self.profile, dict):
            return self.profile.get(key)
        return getattr(self.profile, key, None)
