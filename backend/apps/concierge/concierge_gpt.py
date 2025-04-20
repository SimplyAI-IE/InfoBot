from openai import OpenAI

client = OpenAI()

def concierge_gpt_response(message: str) -> str:
    system_prompt = (
        "You are a structured hotel assistant..."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Sorry, I couldn’t find an answer right now. ({str(e)})"
