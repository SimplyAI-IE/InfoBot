
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from backend.apps.base_app import BaseApp
from memory import save_user_profile, get_user_profile
from .flow_engine import PensionFlow
from .extract_user_data import (
    extract_age, extract_income, extract_retirement_age,
    extract_risk_profile, extract_region, extract_prsi_years
)
from .pension_calculator import calculate_pension

class PensionGuruApp(BaseApp):
    def extract_user_data(self, user_id: str, msg: str):
        msg_lower = msg.lower()
        profile = get_user_profile(user_id)

        print(f"🛠 [HardLinked] extract_user_data for {user_id} → '{msg}'")

        flow = PensionFlow(profile, user_id)
        current_step = flow.current_step_name

        if current_step == "step_1_welcome_intro":
            region = extract_region(msg_lower)
            if region in ["Ireland", "UK"]:
                print(f"📌 Matched region: {region}")
                save_user_profile(user_id, "region", region)
                profile = get_user_profile(user_id)

        elif current_step == "step_ie_ask_prsi":
            prsi_years = extract_prsi_years(msg_lower)
            if prsi_years is not None:
                print(f"📌 Matched PRSI years: {prsi_years}")
                save_user_profile(user_id, "prsi_years", prsi_years)
                profile = get_user_profile(user_id)

        elif current_step == "step_ie_ask_age":
            age = extract_age(msg_lower)
            if age is not None:
                print(f"📌 Matched age: {age}")
                save_user_profile(user_id, "age", age)
                profile = get_user_profile(user_id)

        elif current_step == "step_ie_ask_ret_age":
            ret_age = extract_retirement_age(msg_lower)
            if ret_age is not None:
                print(f"📌 Matched retirement age: {ret_age}")
                save_user_profile(user_id, "retirement_age", ret_age)
                profile = get_user_profile(user_id)

        # Flow auto-advance
        flow = PensionFlow(profile, user_id)
        current_step = flow.current_step_name
        node = flow.flow.get(current_step, {})
        expected_field = node.get("expect_field")
        profile = get_user_profile(user_id)
        if expected_field and getattr(profile, expected_field, None):
            next_step = node.get("next_step")
            if next_step:
                print(f"➡️ Auto-advancing to step: {next_step}")
                save_user_profile(user_id, "pending_step", next_step)

        return get_user_profile(user_id)
