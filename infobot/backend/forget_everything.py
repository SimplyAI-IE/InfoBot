import requests

user_id = "debug123"
url = "http://localhost:8000/chat/forget"

try:
    res = requests.post(url, json={"user_id": user_id})
    res.raise_for_status()
    print("✅ Forget result:", res.status_code, res.json())
except requests.exceptions.RequestException as e:
    print("❌ Failed to reset user state:", e)
    if res is not None:
        print("Status:", res.status_code)
        print("Response:", res.text)
