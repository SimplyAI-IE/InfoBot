import re
from memory import save_user_profile, get_user_profile, save_chat_message

def extract_age(msg):
    patterns = [
        r"\b(\d{1,2})\s*years?\s*old\b",
        r"\bage\s*(is)?\s*(\d{1,2})\b",
        r"\b(?:i['’]?m|i am)\s*(\d{1,2})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, msg)
        if match:
            age = int(match.group(match.lastindex))
            if 18 <= age <= 100:
                return age
    return None

def extract_income(msg):
    match = re.search(r"\b(?:€|£)?(\d{2,6})([kK]?)\b", msg.replace(",", ""))
    if match:
        val = int(match.group(1))
        if match.group(2).lower() == 'k':
            val *= 1000
        if 5_000 <= val <= 500_000:
            return val
    return None

def extract_retirement_age(msg):
    match = re.search(r"\b(?:retire|retirement).{0,20}?(\d{2})\b", msg)
    if not match:
    # fallback for just a number like "65"
        if msg.strip().isdigit():
            val = int(msg.strip())
            if 50 <= val <= 80:
                return val
    if match:
        age = int(match.group(1))
        if 50 <= age <= 80:
            return age
    return None

def extract_risk_profile(msg):
    if "low risk" in msg:
        return "Low"
    elif "high risk" in msg:
        return "High"
    elif "medium risk" in msg or "moderate" in msg:
        return "Medium"
    return None

def extract_region(msg):
    msg = msg.lower().strip()
    print(f"📨 Checking region in msg: {msg}")
    if "ireland" in msg:
        print("✅ Region matched: Ireland")
        return "Ireland"
    elif "uk" in msg or "united kingdom" in msg:
        print("✅ Region matched: UK")
        return "UK"
    elif any(c in msg for c in ["us", "usa", "america", "germany", "france", "canada", "india", "australia"]):
        print("❌ Unsupported region")
        return "unsupported"
    print("❌ No region matched")
    return None

def extract_prsi_years(msg):
    match = re.search(r"(\d{1,2})\s+(?:years?|yrs?)\s+(?:of\s+)?(?:prsi|contributions?)", msg)
    if match:
        return int(match.group(1))
    elif re.fullmatch(r"\s*\d{1,2}\s*", msg.strip()):
        val = int(msg.strip())
        if 0 <= val <= 60:
            return val
    return None

def extract_user_data(user_id: str, msg: str):
    print(f"🛠 extract_user_data running for user {user_id} with message: {msg}")
    msg_lower = msg.lower()

    age = extract_age(msg_lower)
    if age is not None:
        print(f"📌 Extracted age: {age}")
        save_user_profile(user_id, "age", age)

    income = extract_income(msg_lower)
    if income is not None:
        print(f"📌 Extracted income: {income}")
        save_user_profile(user_id, "income", income)

    ret_age = extract_retirement_age(msg_lower)
    if ret_age is not None:
        print(f"📌 Extracted retirement age: {ret_age}")
        save_user_profile(user_id, "retirement_age", ret_age)

    region = extract_region(msg_lower)
    if region in ["Ireland", "UK"]:
        print(f"🌍 Extracted region: {region}")
        try:
            save_user_profile(user_id, "region", region)
            print("✅ Region saved to profile")
        except Exception as e:
            print(f"❌ Failed to save region: {e}")
    elif region == "unsupported":
        block_msg = (
            "This assistant currently only supports pensions in Ireland or the UK.\n"
            "Please consult a local advisor or national authority for other regions."
        )
        save_chat_message(user_id, 'assistant', block_msg)

    risk = extract_risk_profile(msg_lower)
    if risk:
        print(f"📌 Extracted risk profile: {risk}")
        save_user_profile(user_id, "risk_profile", risk)

    prsi_years = extract_prsi_years(msg_lower)
    if prsi_years is not None:
        print(f"📌 Extracted PRSI years: {prsi_years}")
        save_user_profile(user_id, "prsi_years", prsi_years)

    print("🧾 Final user profile after extraction:", get_user_profile(user_id).__dict__)
    return get_user_profile(user_id)
