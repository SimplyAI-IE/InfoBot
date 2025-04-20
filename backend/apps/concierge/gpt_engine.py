import openai

def concierge_gpt_response(message: str) -> str:
    system_prompt = (
        "You are an intelligent, helpful hotel concierge. "
        "If a guest asks about events, dining, directions, or general inquiries, respond clearly. "
        "If a follow-up question is appropriate, ask it."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Sorry, I had trouble finding an answer. ({str(e)})"
