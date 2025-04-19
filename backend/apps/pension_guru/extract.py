
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

        print(f"🛠 [StrictExtract] extract_user_data for {user_id} → '{msg}'")

        flow = PensionFlow(profile, user_id)
        current_step = flow.current_step_name

        if current_step == "step_1_welcome_intro":
            region = extract_region(msg_lower)
            if region in ["Ireland", "UK"]:
                print(f"📌 Region: {region}")
                save_user_profile(user_id, "region", region)
                profile = get_user_profile(user_id)

        elif current_step == "step_ie_ask_prsi":
            prsi_years = extract_prsi_years(msg_lower)
            if prsi_years is not None:
                print(f"📌 PRSI years: {prsi_years}")
                save_user_profile(user_id, "prsi_years", prsi_years)
                profile = get_user_profile(user_id)

        elif current_step == "step_ie_ask_age":
            age = extract_age(msg_lower)
            if age is not None:
                print(f"📌 Age: {age}")
                save_user_profile(user_id, "age", age)
                profile = get_user_profile(user_id)

        elif current_step == "step_ie_ask_ret_age":
            ret_age = extract_retirement_age(msg_lower)
            if ret_age is not None:
                print(f"📌 Retirement Age: {ret_age}")
                save_user_profile(user_id, "retirement_age", ret_age)
                profile = get_user_profile(user_id)

        # Auto-advance
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

    def block_response(self, user_input, profile):
        return None

    def tips_reply(self):
        return "Tips feature not yet implemented."

    def should_offer_tips(self, reply):
        return False

    def wants_tips(self, profile, msg, history):
        return False

    def format_user_context(self, profile):
        return "User profile summary not available."

    def render_profile_field(self, field, profile):
        return "—"
    
    def get_pension_calculation_reply(self, user_id: str) -> str:
        profile = get_user_profile(user_id)
        region = getattr(profile, "region", "").lower()
        prsi_years = getattr(profile, "prsi_years", None)
        age = getattr(profile, "age", None)
        retirement_age = getattr(profile, "retirement_age", None)

        if not (region and prsi_years and age and retirement_age):
            return "I’m missing some details to calculate your pension. Can you confirm your PRSI years, age, and planned retirement age?"

        calc = calculate_pension(region, prsi_years, age=age, retirement_age=retirement_age)
        if not calc:
            return "I couldn’t run the pension estimate. Please check the details provided."

        now_fmt = f"{calc['currency']}{calc['weekly_pension_now']:.2f}"
        future_fmt = f"{calc['currency']}{calc['weekly_pension_future']:.2f}"

        return (
            f"Thanks! Based on {calc['prsi_years']} PRSI years and retiring at {retirement_age}:\n\n"
            f"If you stopped contributing today:\n"
            f"- {calc['contributions_now']} contributions → {now_fmt}/week\n\n"
            f"If you work until age {retirement_age}:\n"
            f"- {calc['contributions_future']} contributions → {future_fmt}/week\n\n"
            f"Would you like tips to boost your pension?"
        )

