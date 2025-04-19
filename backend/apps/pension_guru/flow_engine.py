import os
import yaml

class PensionFlow:
    def __init__(self, profile):
        self.profile = profile
        flow_path = os.path.join(os.path.dirname(__file__), "conversation_flow.yaml")
        with open(flow_path, "r") as f:
            self.flow = yaml.safe_load(f)["conversation_flow"]

    def step(self, current="welcome"):
        node = self.flow.get(current, {})
        check_field = node.get("check")

        # If field is missing, return the prompt
        if check_field and not getattr(self.profile, check_field, None):
            return node.get("prompt")

        # Branch logic: region-based routing
        if "branch" in node:
            region = getattr(self.profile, "region", "").lower()
            if region == "uk":
                return self.step("uk_nic")
            elif region == "ireland":
                return self.step("ie_prsi")
            else:
                return self.step("general_info")

        # Final fallback: return any message
        return node.get("prompt") or node.get("info")
