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

    def pre_prompt(self, profile, user_id):
        from .flow_engine import PensionFlow
        print("📡 pre_prompt triggered")
        flow = PensionFlow(profile, user_id)
        return flow.step()

    def block_response(self, user_input, profile):
        region = ""

        if isinstance(profile, dict):
            region = profile.get("region", "")
        elif profile:
            region = getattr(profile, "region", "")

        region = region.lower()

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

        print(f"🛠 Running extract_user_data for: {user_id} → '{msg}'")
        age = extract_age(msg_lower)
        if age is not None:
            print(f"📌 Detected age: {age}")
            save_user_profile(user_id, "age", age)
            profile = get_user_profile(user_id)
            profile_updated = True

        income = extract_income(msg_lower)
        if income is not None:
            print(f"📌 Detected income: {income}")
            save_user_profile(user_id, "income", income)
            profile = get_user_profile(user_id)
            profile_updated = True

        ret_age = extract_retirement_age(msg_lower)
        if ret_age is not None:
            print(f"📌 Detected retirement age: {ret_age}")
            save_user_profile(user_id, "retirement_age", ret_age)
            profile = get_user_profile(user_id)
            profile_updated = True

        region = extract_region(msg_lower)
        if region in ["Ireland", "UK"]:
            print(f"📌 Detected region: {region}")
            save_user_profile(user_id, "region", region)
            profile = get_user_profile(user_id)
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
            print(f"📌 Detected risk profile: {risk}")
            save_user_profile(user_id, "risk_profile", risk)
            profile = get_user_profile(user_id)
            profile_updated = True

        prsi_years = extract_prsi_years(msg_lower)
        if prsi_years is not None:
            print(f"📌 Detected prsi_years: {prsi_years}")
            save_user_profile(user_id, "prsi_years", prsi_years)
            profile = get_user_profile(user_id)
            profile_updated = True

        # -- Projection Logic --
        profile = get_user_profile(user_id)
        region = getattr(profile, "region", "").lower()
        prsi_years = getattr(profile, "prsi_years", None)
        age = getattr(profile, "age", None)
        retirement_age = getattr(profile, "retirement_age", None)

        if region == "ireland" and prsi_years and retirement_age and age:
            calc = calculate_pension(region, prsi_years, age=age, retirement_age=retirement_age)

            if calc:
                now = calc["weekly_pension_now"]
                future = calc["weekly_pension_future"]
                now_fmt = f"{calc['currency']}{now:.2f}"
                future_fmt = f"{calc['currency']}{future:.2f}"

                reply = (
                    f"Thanks! Based on {calc['prsi_years']} PRSI years and a retirement age of {calc['retirement_age']}:\n\n"
                    f"If you stopped contributing today:\n"
                    f"- {calc['contributions_now']} contributions → {now_fmt}/week\n\n"
                    f"If you work until age {calc['retirement_age']}:\n"
                    f"- {calc['contributions_future']} contributions → {future_fmt}/week\n\n"
                    f"Would you like tips to boost your pension?"
                )
                save_chat_message(user_id, 'assistant', reply)

        elif region == "ireland" and prsi_years:
            if not retirement_age:
                save_user_profile(user_id, "pending_action", "request_retirement_age")
                profile = get_user_profile(user_id)
                save_chat_message(user_id, 'assistant', "Thanks! At what age do you plan to retire?")
            elif not age:
                save_user_profile(user_id, "pending_action", "request_age")
                profile = get_user_profile(user_id)
                save_chat_message(user_id, 'assistant', "Great — and just to confirm, how old are you currently?")

        
        # Auto-advance flow step if expected field was filled
        from .flow_engine import PensionFlow
        flow = PensionFlow(profile, user_id)
        current_step = flow.current_step
        node = flow.flow.get(current_step, {})
        expected_field = node.get("expect_field")
        if expected_field and getattr(profile, expected_field, None):
            next_step = node.get("next_step")
            if next_step:
                print(f"➡️ Auto-advancing to step: {next_step}")
                save_user_profile(user_id, "pending_step", next_step)
                profile = get_user_profile(user_id)
        return get_user_profile(user_id)
    

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

        get = profile.get if isinstance(profile, dict) else lambda k: getattr(profile, k, None)

        region = get("region")
        if region:
            parts.append(f"Region: {region}")

        age = get("age")
        if age:
            parts.append(f"Age: {age}")

        income = get("income")
        if income:
            currency = "£" if region and region.lower() == "uk" else "€"
            try:
                parts.append(f"Income: {currency}{income:,}")
            except Exception:
                parts.append(f"Income: {currency}{income}")

        retirement_age = get("retirement_age")
        if retirement_age:
            parts.append(f"Retirement Age Goal: {retirement_age}")

        risk = get("risk_profile")
        if risk:
            parts.append(f"Risk Tolerance: {risk}")

        prsi = get("prsi_years")
        if prsi is not None:
            parts.append(f"PRSI Contributions: {prsi} years")

        return "User Profile Summary: " + "; ".join(parts)
