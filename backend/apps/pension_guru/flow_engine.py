import os
import yaml
from memory import save_user_profile, get_user_profile # Added get_user_profile
import logging

logger = logging.getLogger(__name__)

class PensionFlow:
    def __init__(self, profile, user_id):
        self.profile = profile
        self.user_id = user_id
        self.flow_path = os.path.join(os.path.dirname(__file__), "conversation_flow.yaml")
        with open(self.flow_path, "r") as f:
            self.flow = yaml.safe_load(f)["conversation_flow"]

        # Determine the current step from the profile
        self.current_step_name = self._get_profile_value("pending_step", "step_1_welcome_intro")
        logger.debug(f"PensionFlow initialized for user {user_id}. Current step: {self.current_step_name}")

    def step(self):
        """
        Determines the next scripted prompt or action based on the current flow state and profile.
        Handles step advancement internally if conditions are met.
        Returns:
            str: The next scripted prompt to show the user.
            None: If the flow is finished or should transition to GPT/calculation.
        """
        if not self.current_step_name:
            logger.debug(f"🧭 FLOW {self.user_id}: No current step, returning None.")
            return None # Flow is finished or paused

        current_node = self.flow.get(self.current_step_name)
        if not current_node:
            logger.error(f"🧭 FLOW ERROR {self.user_id}: Step '{self.current_step_name}' not found in conversation_flow.yaml!")
            # Attempt to clear the invalid step and return None
            save_user_profile(self.user_id, "pending_step", None)
            return None

        logger.info(f"🧭 FLOW {self.user_id}: Processing step '{self.current_step_name}'")

        # 1. Check Blocking Conditions (e.g., unsupported region - though handled earlier now)
        #    (Could add specific step blocks here if needed)

        # 2. Handle Branching Logic
        if "branching_logic" in current_node:
            region = self._get_profile_value("region")
            target_flow = None
            fallback_prompt = None

            if region:
                region_lower = region.lower()
                for branch in current_node["branching_logic"]:
                    # Ensure condition exists and is a string before lowercasing
                    condition = branch.get("condition", "")
                    if isinstance(condition, str) and region_lower in condition.lower():
                        target_flow = branch.get("target_flow")
                        if target_flow: break # Found matching branch
                # Handle fallback if no specific region matched
                if not target_flow and len(current_node["branching_logic"]) > 0:
                     fallback_branch = current_node["branching_logic"][-1]
                     # Check if the last item is intended as a fallback (e.g., no specific condition or condition like 'other')
                     if "condition" not in fallback_branch or "other" in fallback_branch.get("condition", "").lower():
                          fallback_prompt = fallback_branch.get("prompt")
                          target_flow = fallback_branch.get("target_flow") # Could also target a flow

            if target_flow:
                logger.info(f"🧭 FLOW {self.user_id}: Branching to '{target_flow}' based on region '{region}'")
                self.profile = save_user_profile(self.user_id, "pending_step", target_flow)
                self.current_step_name = target_flow # Update internal state for potential recursion/next call
                # Recursively call step to get the prompt of the *new* step
                return self.step()
            elif fallback_prompt:
                 logger.warning(f"🧭 FLOW {self.user_id}: Branching fallback for step '{self.current_step_name}'.")
                 # Don't advance step, just return the fallback prompt
                 return fallback_prompt
            else:
                 logger.warning(f"🧭 FLOW {self.user_id}: No matching branch or fallback for step '{self.current_step_name}' and region '{region}'. Waiting.")
                 # Return current prompt if any, otherwise None. Don't advance.
                 return current_node.get("script_prompt")


        # 3. Check if current step expects input and if it's fulfilled
        expected_field = current_node.get("expect_field")
        next_step_name = current_node.get("next_step") # Use 'null' in YAML for explicit stop

        if expected_field:
            field_value = self._get_profile_value(expected_field)
            if field_value is not None:
                logger.info(f"🧭 FLOW {self.user_id}: Expected field '{expected_field}' is fulfilled ('{field_value}'). Advancing.")
                # Field is fulfilled, advance to the next step
                self.profile = save_user_profile(self.user_id, "pending_step", next_step_name)
                self.current_step_name = next_step_name
                # Recursively call step to get the prompt of the *new* step (or None if flow ends)
                return self.step()
            else:
                # Field not yet fulfilled, return the prompt for the *current* step
                logger.debug(f"🧭 FLOW {self.user_id}: Waiting for field '{expected_field}'. Returning current prompt.")
                return current_node.get("script_prompt")
        else:
            # No specific field expected, this is likely an informational step.
            # Advance to the next step immediately after showing the prompt.
            logger.info(f"🧭 FLOW {self.user_id}: No expected field. Advancing from '{self.current_step_name}' to '{next_step_name}'.")
            self.profile = save_user_profile(self.user_id, "pending_step", next_step_name)
            # Return the prompt for the *current* step, state is now updated for the *next* call
            return current_node.get("script_prompt")

        # Fallback if none of the above returned
        logger.debug(f"🧭 FLOW {self.user_id}: Reached end of step logic for '{self.current_step_name}', returning None.")
        # Ensure state is cleared if we fall through unexpectedly
        if self.current_step_name: # Avoid clearing if already None
             save_user_profile(self.user_id, "pending_step", None)
        return None

    def _get_profile_value(self, key, default=None):
        """Safely gets a value from the profile, whether it's a dict or object."""
        if isinstance(self.profile, dict):
            return self.profile.get(key, default)
        # Check if profile is None before using getattr
        elif self.profile is not None:
             return getattr(self.profile, key, default)
        # Return default if profile itself is None
        return default