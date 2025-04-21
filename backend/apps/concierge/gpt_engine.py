from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import Optional

client = OpenAI()

def concierge_gpt_response(message: str) -> str:
    system_prompt = (
        "You are an intelligent, helpful hotel concierge. "
        "If a guest asks about events, dining, directions, or general inquiries, respond clearly. "
        "If a follow-up question is appropriate, ask it."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=300
        )

        content: Optional[str] = response.choices[0].message.content
        return content.strip() if content else "I'm not sure how to respond."

    except Exception as e:
        return f"Sorry, I had trouble finding an answer. ({str(e)})"
