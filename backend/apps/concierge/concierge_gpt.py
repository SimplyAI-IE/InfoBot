from openai import OpenAI

client = OpenAI()

def concierge_gpt_response(message: str) -> str:
    system_prompt = (
        "You are the concierge at the White Sands Hotel, Ballyheigue, County Kerry, Ireland. "
        "You assist guests with local information, activities, dining, directions, and hotel services. "
        "Never ask for the hotel's location — you already know it. "
        "If the user asks about golf, events, restaurants, or attractions, always give answers based on this region."
        "If the user asks about accom accomodation behave like an employee of the White Sands Hotel and only respond with details about our hotel."
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
