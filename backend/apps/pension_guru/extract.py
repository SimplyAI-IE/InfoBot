import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from backend.apps.base_app import BaseApp
from memory import save_user_profile, get_user_profile, save_chat_message
# Note: PensionFlow import moved to main.py where it's instantiated
from .extract_user_data import (
    extract_age, extract_income, extract_retirement_age,
    extract_risk_profile, extract_region, extract_prsi_years
)
from .pension_calculator import calculate_pension

class PensionGuruApp(BaseApp):

    # pre_prompt is still needed by flow_engine
    def pre_prompt(self, profile, user_id):
        profile = get_user_profile(user_id)
        from .flow_engine import PensionFlow # Keep import here for this method
        print("📡 pre_prompt triggered")
        flow = PensionFlow(profile, user_id)
        return flow.step()

    def block_response(self, user_input, profile):
        # --- (block_response logic remains unchanged) ---
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
        # --- (wants_tips logic remains unchanged) ---
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
         # --- (should_offer_tips logic remains unchanged) ---
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
        # --- (render_profile_field logic remains unchanged) ---
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
        """
        Extracts data from user message and saves it to the profile.
        Returns the updated profile. Does NOT handle flow advancement.
        """
        msg_lower = msg.lower()
        profile = get_user_profile(user_id) # Get current profile

        print(f"🛠 Running extract_user_data for: {user_id} → '{msg}'")
        age = extract_age(msg_lower)
        if age is not None:
            print(f"📌 Detected age: {age}")
            profile = save_user_profile(user_id, "age", age) # Update profile
            profile = get_user_profile(user_id)

        income = extract_income(msg_lower)
        if income is not None:
            print(f"📌 Detected income: {income}")
            profile = save_user_profile(user_id, "income", income) # Update profile
            profile = get_user_profile(user_id)

        ret_age = extract_retirement_age(msg_lower)
        if ret_age is not None:
            print(f"📌 Detected retirement age: {ret_age}")
            profile = save_user_profile(user_id, "retirement_age", ret_age) # Update profile
            profile = get_user_profile(user_id)

        region = extract_region(msg_lower)
        if region in ["Ireland", "UK"]:
            print(f"📌 Detected region: {region}")
            profile = save_user_profile(user_id, "region", region) # Update profile
            profile = get_user_profile(user_id)
        elif region == "unsupported":
            # This is an immediate blocking condition, handle here
            block_msg = (
                "Pension Guru is currently designed to assist users in Ireland or the UK only.\n"
                "Unfortunately, I can't offer reliable pension advice for other countries.\n"
                "Please consult a local advisor or your national pension authority for help."
            )
            save_chat_message(user_id, 'assistant', block_msg)
            # Maybe return a special value or raise an exception to signal blockage in main.py?
            # For now, just save message and return current profile. main.py block_response will catch it later.


        risk = extract_risk_profile(msg_lower)
        if risk:
            print(f"📌 Detected risk profile: {risk}")
            profile = save_user_profile(user_id, "risk_profile", risk) # Update profile
            profile = get_user_profile(user_id)

        prsi_years = extract_prsi_years(msg_lower)
        if prsi_years is not None:
            print(f"📌 Detected prsi_years: {prsi_years}")
            profile = save_user_profile(user_id, "prsi_years", prsi_years) # Update profile
            profile = get_user_profile(user_id)


        # --- Flow Advancement Logic REMOVED from here ---

        # Return the latest profile state after extractions
        return get_user_profile(user_id)


    def get_pension_calculation_reply(self, user_id: str) -> str | None:
        """
        Checks if conditions are met for pension calculation and returns the reply string.
        Returns None if conditions are not met or calculation fails.
        """
        profile = get_user_profile(user_id)
        region = getattr(profile, "region", "").lower()
        prsi_years = getattr(profile, "prsi_years", None)
        age = getattr(profile, "age", None)
        retirement_age = getattr(profile, "retirement_age", None)

        if region == "ireland" and prsi_years is not None and age is not None and retirement_age is not None:
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
                # Set pending action so the main loop knows tips were offered
                save_user_profile(user_id, "pending_action", "offer_tips")
                profile = get_user_profile(user_id)
                return reply
        # TODO: Add UK calculation trigger if needed

        # Conditions not met or calculation failed
        return None


    def tips_reply(self):
        # --- (tips_reply logic remains unchanged) ---
        return (
            "Great! Here are a few ways to boost your State Pension in Ireland:\n\n"
            "1. **Keep Contributing**: Work and pay PRSI for up to 40 years to maximize your pension.\n"
            "2. **Voluntary Contributions**: Check gaps in your record on MyWelfare.ie and make voluntary contributions if eligible.\n"
            "3. **Credits**: You may qualify for credits for periods like childcare or unemployment.\n\n"
            "Does that make sense? Check MyWelfare.ie or consult a financial advisor for personalized advice."
        )


    def format_user_context(self, profile):
        # --- (format_user_context logic remains unchanged) ---
        if not profile:
            return "No user profile available."

        parts = []

        get = profile.get if isinstance(profile, dict) else lambda k, default=None: getattr(profile, k, default)


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

        pending_step = get("pending_step")
        if pending_step:
             parts.append(f"Current Flow Step: {pending_step}")

        return "User Profile Summary: " + "; ".join(parts)

# --- End of PensionGuruApp class ---