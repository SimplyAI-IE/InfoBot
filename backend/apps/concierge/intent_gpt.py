from openai import OpenAI

client = OpenAI()

def resolve_intent(message: str) -> str:
    system_prompt = (
        "You are an intent classifier for a hotel concierge assistant. "
        "Respond with only one word from the following list of supported intents:\n"
        "- wifi\n- menu\n- checkin\n- checkout\n- dining\n- golf\n- activities\n- transport\n- events\n- website\n- facebook\n"
        "If you are unsure, respond with: unknown"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        temperature=0,
        max_tokens=10
    )

    return response.choices[0].message.content.strip().lower()
