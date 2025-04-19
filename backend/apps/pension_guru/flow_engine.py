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

        self.current_step = getattr(profile, "pending_step", "welcome")

    def step(self):
        node = self.flow.get(self.current_step, {})
        check_field = node.get("check")

        # If field is missing, prompt for it
        if check_field and not getattr(self.profile, check_field, None):
            return node.get("prompt")

        # Branching logic
        if "branch" in node:
            region = getattr(self.profile, "region", "").lower()
            next_branch = (
                "uk_nic" if region == "uk" else
                "ie_prsi" if region == "ireland" else
                "general_info"
            )
            save_user_profile(self.user_id, "pending_step", next_branch)
            self.current_step = next_branch
            return self.step()

        # Advance if possible
        next_step = node.get("next")
        if next_step:
            save_user_profile(self.user_id, "pending_step", next_step)
            self.current_step = next_step
            return self.step()

        # Flow complete
        save_user_profile(self.user_id, "pending_step", None)
        return None
