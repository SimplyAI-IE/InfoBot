import re

from backend.memory import MemoryManager
from backend.models import SessionLocal


def extract_age(msg: str) -> int | None:
    patterns = [
        r"\b(\d{1,2})\s*years?\s*old\b",
        r"\bage\s*(is)?\s*(\d{1,2})\b",
        r"\b(?:i['’]?m|i am)\s*(\d{1,2})\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, msg)
        if match and match.lastindex is not None:
            age = int(match.group(match.lastindex))
            if 18 <= age <= 100:
                return age

    if re.fullmatch(r"\s*\d{1,2}\s*", msg.strip()):
        try:
            age = int(msg.strip())
            if 18 <= age <= 100:
                print(f"✅ Matched simple number as age: {age}")
                return age
        except ValueError:
            pass
    return None


def extract_income(msg: str) -> int | None:
    match = re.search(r"\b(?:€|£)?(\d{2,6})([kK]?)\b", msg.replace(",", ""))
    if match:
        val = int(match.group(1))
        if match.group(2).lower() == "k":
            val *= 1000
        if 5_000 <= val <= 500_000:
            return val
    return None


def extract_retirement_age(msg: str) -> int | None:
    match_keyword = re.search(r"\b(?:retire|retirement).{0,20}?(\d{2})\b", msg)
    if match_keyword:
        age = int(match_keyword.group(1))
        if 50 <= age <= 80:
            print(f"✅ Matched retirement age with keyword: {age}")
            return age

    if re.fullmatch(r"\s*\d{1,2}\s*", msg.strip()):
        try:
            val = int(msg.strip())
            if 50 <= val <= 80:
                print(f"✅ Matched simple number as retirement age: {val}")
                return val
        except ValueError:
            pass
    return None


def extract_risk_profile(msg: str) -> str | None:
    msg = msg.lower()
    if "low risk" in msg:
        return "Low"
    elif "high risk" in msg:
        return "High"
    elif "medium risk" in msg or "moderate" in msg:
        return "Medium"
    return None


def extract_region(msg: str) -> str | None:
    msg = msg.lower().strip()
    print(f"📨 Checking region in msg: {msg}")
    if "ireland" in msg or " ie" in msg or msg == "ie":
        print("✅ Region matched: Ireland")
        return "Ireland"
    elif "uk" in msg or "united kingdom" in msg:
        print("✅ Region matched: UK")
        return "UK"
    elif any(
        c in msg
        for c in [
            "us",
            "usa",
            "america",
            "germany",
            "france",
            "canada",
            "india",
            "australia",
        ]
    ):
        print("❌ Unsupported region")
        return "unsupported"
    print("❌ No region matched")
    return None


def extract_prsi_years(msg: str) -> int | None:
    match_keyword = re.search(
        r"(\d{1,2})\s+(?:years?|yrs?)\s+(?:of\s+)?(?:prsi|contributions?)", msg
    )
    if match_keyword:
        years = int(match_keyword.group(1))
        if 0 <= years <= 60:
            print(f"✅ Matched PRSI years with keyword: {years}")
            return years

    if re.fullmatch(r"\s*\d{1,2}\s*", msg.strip()):
        try:
            val = int(msg.strip())
            if 0 <= val <= 60:
                print(f"✅ Matched simple number as PRSI years: {val}")
                return val
        except ValueError:
            pass
    return None


def extract_user_data(user_id: str, msg: str) -> dict[str, int | None]:
    print(f"🛠 extract_user_data running for user {user_id} with message: {msg}")
    db = SessionLocal()
    memory = MemoryManager(db)
    try:
        extracted: dict[str, int | None] = {}
        age = extract_age(msg.lower())
        if age is not None:
            memory.save_user_profile(user_id, {"age": age})
            extracted["age"] = age
        return extracted
    finally:
        db.close()
