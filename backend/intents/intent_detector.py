import json


def parse_intent_response(response: str) -> dict:
    try:
        parsed = json.loads(response)
        return {
            "callback_request": parsed.get("callback_request", False),
            "name": parsed.get("name"),
            "phone": parsed.get("phone"),
        }
    except Exception:
        return {
            "callback_request": False,
            "name": None,
            "phone": None,
        }
