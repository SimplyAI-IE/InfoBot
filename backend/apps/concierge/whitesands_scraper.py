import requests
from bs4 import BeautifulSoup
import openai
import json
import time
from pathlib import Path

CACHE_PATH = Path(__file__).resolve().parent.parent.parent / "cache" / "whitesands_facts.json"
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours

def scrape_whitesands_raw() -> str:
    url = "https://www.whitesands.ie"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def parse_whitesands_content(raw_text: str) -> str:
    system_prompt = (
        "You are a structured data extractor. Read hotel website text and extract key facts. "
        "Include check-in/out times, contact details, amenities, dining options, room types, nearby attractions, and other useful guest info. "
        "Return your response in bullet points for readability."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text}
        ],
        temperature=0.3,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

def get_cached_whitesands_facts() -> str:
    # Load cache if fresh
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if time.time() - data["timestamp"] < CACHE_TTL_SECONDS:
                return data["facts"]

    # Scrape and parse fresh
    raw = scrape_whitesands_raw()
    facts = parse_whitesands_content(raw)

    # Save cache
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({"timestamp": time.time(), "facts": facts}, f, indent=2)

    return facts
