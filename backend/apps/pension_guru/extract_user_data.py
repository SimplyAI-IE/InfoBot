import re
from memory import save_user_profile

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
    msg = msg.lower()
    if "ireland" in msg:
        return "Ireland"
    elif "uk" in msg or "united kingdom" in msg:
        return "UK"
    elif any(c in msg for c in ["us", "usa", "america", "germany", "france", "canada", "india", "australia"]):
        return "unsupported"
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
