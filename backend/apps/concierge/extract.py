import re
from memory import save_user_profile

def extract_user_data(user_id: str, msg: str):
    msg_lower = msg.lower()

    # Extract party size
    party_match = re.search(r"(table|for|party)\s*(of)?\s*(\d+)", msg_lower)
    if party_match:
        save_user_profile(user_id, "party_size", int(party_match.group(3)))

    # Extract time (simple example)
    time_match = re.search(r"\b(\d{1,2})(:\d{2})?\s*(am|pm)?\b", msg_lower)
    if time_match:
        save_user_profile(user_id, "time", time_match.group(0))

    # Extract date (very simple version)
    if "tonight" in msg_lower:
        save_user_profile(user_id, "date", "today")
    elif "tomorrow" in msg_lower:
        save_user_profile(user_id, "date", "tomorrow")

    # Extract cuisine preferences
    cuisine_match = re.search(r"(italian|indian|thai|sushi|steak|vegan)", msg_lower)
    if cuisine_match:
        save_user_profile(user_id, "cuisine", cuisine_match.group(1))
