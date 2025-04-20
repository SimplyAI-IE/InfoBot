import openai

def concierge_gpt_response(message: str) -> str:
    system_prompt = (
        "You are an intelligent, helpful hotel concierge. "
        "Answer questions about hotel facilities, Wi-Fi, dining, local events, directions, and area info. "
        "If a follow-up makes sense, include it in a polite tone."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Sorry, I couldn’t find an answer right now. ({str(e)})"
