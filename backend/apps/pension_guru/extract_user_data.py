import re
from memory import save_user_profile, get_user_profile, save_chat_message # Imports remain the same

# Updated extract_age function
def extract_age(msg):
    # Keep existing patterns
    patterns = [
        r"\b(\d{1,2})\s*years?\s*old\b",
        r"\bage\s*(is)?\s*(\d{1,2})\b",
        r"\b(?:i['’]?m|i am)\s*(\d{1,2})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, msg)
        if match:
            age = int(match.group(match.lastindex))
            # Keep reasonable age check
            if 18 <= age <= 100:
                return age

    # --- NEW: Add fallback for simple number input ---
    # Check if the message is just a 1 or 2 digit number
    if re.fullmatch(r"\s*\d{1,2}\s*", msg.strip()):
         try:
             age = int(msg.strip())
             # Apply the same reasonable age check
             if 18 <= age <= 100:
                 print(f"✅ Matched simple number as age: {age}")
                 return age
         except ValueError:
             pass # Not a valid integer

    return None # Return None if no pattern matched or number out of range

# --- Other extraction functions remain the same ---

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
    # Slightly prioritize looking for keywords first
    match_keyword = re.search(r"\b(?:retire|retirement).{0,20}?(\d{2})\b", msg)
    if match_keyword:
        age = int(match_keyword.group(1))
        if 50 <= age <= 80:
             print(f"✅ Matched retirement age with keyword: {age}")
             return age

    # Fallback for just a number - BE CAREFUL not to grab current age
    # Consider adding context check here later if needed (e.g., if pending_step == ask_ret_age)
    if re.fullmatch(r"\s*\d{1,2}\s*", msg.strip()):
            try:
                val = int(msg.strip())
                # Use retirement age range
                if 50 <= val <= 80:
                     print(f"✅ Matched simple number as retirement age: {val}")
                     # Potentially add a check here: if 'age' is already known and similar, maybe this isn't retirement age?
                     return val
            except ValueError:
                 pass
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
    if "ireland" in msg or " ie" in msg or msg == "ie": # Added variations
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
    # Prioritize pattern with "years" "prsi" "contributions"
    match_keyword = re.search(r"(\d{1,2})\s+(?:years?|yrs?)\s+(?:of\s+)?(?:prsi|contributions?)", msg)
    if match_keyword:
        years = int(match_keyword.group(1))
        if 0 <= years <= 60: # Keep range check
             print(f"✅ Matched PRSI years with keyword: {years}")
             return years

    # Fallback for just a number - BE CAREFUL not to grab current age or retirement age
    # Consider adding context check here later if needed (e.g., if pending_step == ask_prsi)
    if re.fullmatch(r"\s*\d{1,2}\s*", msg.strip()):
        try:
            val = int(msg.strip())
            # Use PRSI years range
            if 0 <= val <= 60:
                 print(f"✅ Matched simple number as PRSI years: {val}")
                 # Potentially add checks: if 'age' or 'ret_age' are known and similar, maybe this isn't PRSI years?
                 return val
        except ValueError:
            pass
    return None

# This function is called by PensionGuruApp.extract_user_data, no changes needed here
def extract_user_data(user_id: str, msg: str):
    print(f"🛠 (Old standalone) extract_user_data running for user {user_id} with message: {msg}")
    # This function body is essentially superseded by the method in PensionGuruApp
    # but we keep the individual extractor functions above.
    # The logic inside PensionGuruApp.extract_user_data now calls the functions above.
    profile = get_user_profile(user_id)
    # Example of calling the updated function:
    age = extract_age(msg.lower())
    if age is not None:
         print(f"📌 (Example Call) Extracted age: {age}")
         save_user_profile(user_id, "age", age)
    # ... rest of the extraction calls would happen in PensionGuruApp method ...
    print("🧾 (Old standalone) Final user profile after extraction:", get_user_profile(user_id).__dict__)
    return get_user_profile(user_id)