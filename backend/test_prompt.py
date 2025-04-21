from backend.gpt_engine import get_gpt_response
from backend.memory import MemoryManager
from backend.models import SessionLocal
from backend.apps.pension_guru.extract_user_data import extract_user_data  # ✅ corrected import

def interactive_test() -> None:
    user_id = "debug123"
    tone = "14"

    db = SessionLocal()
    memory = MemoryManager(db)
    try:
        print("🧪 Starting interactive pension assistant test.")
        while True:
            prompt = input("You: ")
            if prompt.strip().lower() in ["exit", "quit"]:
                break

            extract_user_data(user_id, prompt)
            reply = get_gpt_response(prompt, user_id, tone=tone)
            print("Pension Guru:", reply)
    finally:
        db.close()

if __name__ == "__main__":
    test_user = "test123"
    test_msg = "I'm 42, based in Ireland, earning €55k, retiring at 65, low risk"
    db = SessionLocal()
    memory = MemoryManager(db)
    try:
        profile = extract_user_data(test_user, test_msg)
        print("✅ Initial test profile updated:", profile)
    finally:
        db.close()

    interactive_test()