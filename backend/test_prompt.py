from gpt_engine import get_gpt_response
from memory import save_user_profile
from apps.pension_guru.extract import extract_user_data  # ✅ correct
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apps.pension_guru.extract import extract_user_data

print("Running extraction test...")

user_id = "test123"
message = "I'm 42, based in Ireland, earning €55k, retiring at 65, low risk"
updated = extract_user_data(user_id, message)

print("Profile updated:", updated)

test_user = "debug123"
test_tone = "14"

while True:
    prompt = input("You: ")
    if prompt.strip().lower() in ["exit", "quit"]:
        break

    extract_user_data(test_user, prompt)
    reply = get_gpt_response(prompt, test_user, tone=test_tone)
    print("Pension Guru:", reply)
