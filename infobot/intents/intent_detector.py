import openai
import json
from typing import Optional, TypedDict


class CallbackIntent(TypedDict):
    callback_request: bool
    name: Optional[str]
    phone: Optional[str]


def detect_callback_intent(user_message: str) -> CallbackIntent:
    """
    Uses OpenAI to detect if a user wants a callback.
    Returns a structured intent dict.
    """
    system_prompt = """
You are an intent detector. If the user asks to speak to someone or requests a callback,
return a JSON object like:

{
  "callback_request": true,
  "name": "<user's name if provided>",
  "phone": "<user's phone if provided>"
}

If there's no such request, return:

{ "callback_request": false }
    """.strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0,
        )

        raw_content = response["choices"][0]["message"]["content"]
        return parse_intent_response(raw_content)

    except Exception:
        return {"callback_request": False, "name": None, "phone": None}


def parse_intent_response(response_str: str) -> CallbackIntent:
    try:
        parsed = json.loads(response_str)
        return {
            "callback_request": parsed.get("callback_request", False),
            "name": parsed.get("name"),
            "phone": parsed.get("phone"),
        }
    except json.JSONDecodeError:
        return {"callback_request": False, "name": None, "phone": None}


if __name__ == "__main__":
    # Example usage
    user_input = "Hi, I’d like someone to call me. My number is +491234567890."
    intent = detect_callback_intent(user_input)
    print("Detected intent:", intent)
