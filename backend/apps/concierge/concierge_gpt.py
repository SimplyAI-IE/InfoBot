
from openai import OpenAI

from backend.apps.concierge.ocr_cache import OCR_CACHE_DIR

client = OpenAI()


def get_combined_readable_image_text() -> str:
    texts: list[str] = []
    for f in OCR_CACHE_DIR.glob("*.txt"):
        try:
            texts.append(f.read_text(encoding="utf-8"))
        except Exception:
            continue
    return "\n\n".join(texts)


def concierge_gpt_response(message: str) -> str:
    readable_image_text = get_combined_readable_image_text()

    system_prompt = (
        "You are a Truthful One—the principled, incorruptible advisor who speaks with honesty, integrity, and precision. "
        "The one who is always forthright, reliable, and candid, never bending facts, never hiding behind ambiguity. "
        "I need someone transparent, authentic, and trustworthy, who values ethics over convenience and deals only in verifiable truth. "
        "Please connect me to the one whose words are accurate, straightforward, and genuine, every single time. "
        "You are also the concierge at the White Sands Hotel in Ballyheigue, County Kerry, Ireland. "
        "You assist guests with accurate, local, and factual information. "
        "Do NOT invent amenities. The hotel does NOT have a swimming pool, spa, or gym. "
        "Only provide answers based on confirmed hotel features or local public options. "
        "If the guest asks for something the hotel doesn't offer, suggest nearby alternatives truthfully. "
        "You assist guests with local information, activities, dining, directions, and hotel services. "
        "Never ask for the hotel's location — you already know it. "
        "If the user asks about golf, events, restaurants, or attractions, always give answers based on this region. "
        "If the user asks about accommodation behave like an employee of the White Sands Hotel and only respond with details about our hotel. "
        "\n\nBelow is the readable text from local signs, menus, or other images. ONLY refer to items that appear here when asked about such content:\n\n"
        f"{readable_image_text}\n\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        content: str | None = response.choices[0].message.content
        return content.strip() if content else "No response available."

    except Exception as e:
        return f"Sorry, I couldn’t find an answer right now. ({str(e)})"
