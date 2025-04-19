import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from backend.apps.base_app import BaseApp
from memory import save_user_profile, get_user_profile, save_chat_message
from .flow_engine import PensionFlow
from .extract_user_data import (
    extract_age, extract_income, extract_retirement_age,
    extract_risk_profile, extract_region, extract_prsi_years
)
from .pension_calculator import calculate_pension

class PensionGuruApp(BaseApp):

    def pre_prompt(self, profile):
        flow = PensionFlow(profile)
        return flow.step("welcome")

    def block_response(self, user_input, profile):
        region = getattr(profile, "region", None)
        region = region.lower() if region else ""

        if region not in ["ireland", "uk"]:
            return (
                "This assistant is currently available only to users in Ireland or the UK. "
                "Please consult your local government or a licensed advisor for assistance in your region."
            )
        return None

    def wants_tips(self, profile, msg: str, history: list) -> bool:
        affirmatives = {"yes", "ok", "sure", "please", "yep", "fine", "yes please"}

        if getattr(profile, "pending_action", "") == "offer_tips":
            return msg.strip().lower() in affirmatives

        if history and len(history) >= 2:
            prev = history[-2]["content"].lower()
            return any(
                phrase in prev for phrase in [
                    "would you like tips",
                    "boost your pension",
                    "increase your pension",
                    "improve your pension"
                ]
            ) and msg.strip().lower() in affirmatives

        return False

    def should_offer_tips(self, reply: str) -> bool:
        reply = reply.lower()
        return any(
            phrase in reply for phrase in [
                "would you like tips",
                "boost your pension",
                "increase your pension",
                "improve your pension"
            ]
        )

    def render_profile_field(self, field, profile):
        if field == "income":
            income = getattr(profile, "income", None)
            if income is None:
                return "—"
            region = getattr(profile, "region", "").lower()
            currency = "£" if region == "uk" else "€"
            try:
                return f"{currency}{income:,}"
            except Exception:
                return f"{currency}{income}"
        return getattr(profile, field, "—")

    def extract_user_data(self, user_id: str, msg: str):
        msg_lower = msg.lower()
        profile_updated = False
        profile = get_user_profile(user_id)

        age = extract_age(msg_lower)
        if age is not None:
            save_user_profile(user_id, "age", age)
            profile_updated = True

        income = extract_income(msg_lower)
        if income is not None:
            save_user_profile(user_id, "income", income)
            profile_updated = True

        ret_age = extract_retirement_age(msg_lower)
        if ret_age is not None:
            save_user_profile(user_id, "retirement_age", ret_age)
            profile_updated = True

        region = extract_region(msg_lower)
        if region in ["Ireland", "UK"]:
            save_user_profile(user_id, "region", region)
            profile_updated = True
        elif region == "unsupported":
            block_msg = (
                "Pension Guru is currently designed to assist users in Ireland or the UK only.\n"
                "Unfortunately, I can't offer reliable pension advice for other countries.\n"
                "Please consult a local advisor or your national pension authority for help."
            )
            save_chat_message(user_id, 'assistant', block_msg)
            return False

        risk = extract_risk_profile(msg_lower)
        if risk:
            save_user_profile(user_id, "risk_profile", risk)
            profile_updated = True

        prsi_years = extract_prsi_years(msg_lower)
        if prsi_years is not None:
            save_user_profile(user_id, "prsi_years", prsi_years)
            profile_updated = True

        return profile_updated

    def tips_reply(self):
        return (
            "Great! Here are a few ways to boost your State Pension in Ireland:\n\n"
            "1. **Keep Contributing**: Work and pay PRSI for up to 40 years to maximize your pension.\n"
            "2. **Voluntary Contributions**: Check gaps in your record on MyWelfare.ie and make voluntary contributions if eligible.\n"
            "3. **Credits**: You may qualify for credits for periods like childcare or unemployment.\n\n"
            "Does that make sense? Check MyWelfare.ie or consult a financial advisor for personalized advice."
        )

    def format_user_context(self, profile):
        if not profile:
            return "No user profile available."

        parts = []
        if profile.region: parts.append(f"Region: {profile.region}")
        if profile.age: parts.append(f"Age: {profile.age}")
        if profile.income:
            currency = '£' if profile.region == 'UK' else '€'
            parts.append(f"Income: {currency}{profile.income:,}")
        if profile.retirement_age: parts.append(f"Retirement Age Goal: {profile.retirement_age}")
        if profile.risk_profile: parts.append(f"Risk Tolerance: {profile.risk_profile}")
        if hasattr(profile, 'prsi_years') and profile.prsi_years is not None:
            parts.append(f"PRSI Contributions: {profile.prsi_years} years")

        return "User Profile Summary: " + "; ".join(parts)

    def handle_empty_input(self, user_id, history, profile, tone):
        if profile and getattr(profile, "pending_action", None) == "offer_tips":
            save_user_profile(user_id, "pending_action", None)
            reply = self.tips_reply()
            save_chat_message(user_id, 'assistant', reply)
            return reply

        if history and len(history) >= 2:
            if "how many years of prsi contributions" in history[-2]["content"].lower():
                if profile and profile.region in ["Ireland", "UK"] and getattr(profile, "prsi_years", None):
                    calc = calculate_pension(profile.region, profile.prsi_years)
                    reply = (
                        f"For {calc.get('prsi_years') or calc.get('ni_years')} years of contributions in {calc['region']}:\n"
                        f"- Method: {calc['method']}\n"
                        f"- Weekly Pension ≈ {calc['currency']}{calc['weekly_pension']}\n\n"
                        f"Would you like tips to boost your pension?"
                    )
                    save_chat_message(user_id, 'assistant', reply)
                    return reply
