import json

def parse_intent_response(response: str) -> dict:
    try:
        return json.loads(response)
    except Exception:
        return {"callback_request": False}
