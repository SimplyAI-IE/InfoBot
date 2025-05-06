from pathlib import Path
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


def concierge_gpt_response(message: str, user_id: str, tone: str = "") -> str:
    prompt_path = Path("backend/apps/concierge/prompt.txt")
    links_path = Path("backend/apps/concierge/links.txt")

    try:
        base_prompt = prompt_path.read_text(encoding="utf-8").strip()
    except Exception:
        base_prompt = "You are a helpful hotel concierge."

    try:
        links_text = links_path.read_text(encoding="utf-8").strip()
    except Exception:
        links_text = ""

    readable_image_text = get_combined_readable_image_text()

    system_prompt = (
        f"{base_prompt}\n\n"
        f"Here are trusted reference links you can use in replies:\n{links_text}\n\n"
        f"Local image data from signage, menus, or posts:\n\n{readable_image_text}"
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
