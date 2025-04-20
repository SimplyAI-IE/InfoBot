import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from openai import OpenAI
import json
import time
from pathlib import Path

# --- Config ---
BASE_URL = "https://www.whitesands.ie"
CACHE_PATH = Path(__file__).resolve().parent.parent.parent / "cache" / "whitesands_facts.json"
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours
client = OpenAI()

# --- Scrape all internal pages ---
def scrape_whitesands_raw() -> str:
    visited = set()
    to_visit = [BASE_URL]
    all_text = []

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url, timeout=10)
            if not response.ok:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            page_text = "\n".join(
                el.get_text(strip=True)
                for el in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])
                if el.get_text(strip=True)
            )
            if page_text:
                all_text.append(page_text)
            visited.add(url)

            # Queue more links
            for link in soup.find_all("a", href=True):
                href = link["href"]
                joined = urljoin(BASE_URL, href)
                if urlparse(joined).netloc == urlparse(BASE_URL).netloc and joined not in visited:
                    to_visit.append(joined)

        except Exception as e:
            print(f"Skipping {url}: {e}")

    return "\n".join(all_text)

# --- GPT fact extraction ---
def parse_whitesands_content(raw_text: str) -> str:
    system_prompt = (
        "You are a structured data extractor. Read hotel website text and extract key facts. "
        "Include check-in/out times, contact details, amenities, dining options, room types, nearby attractions, and other useful guest info. "
        "Return your response in bullet points for readability."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text}
        ],
        temperature=0.3,
        max_tokens=800
    )
    return response.choices[0].message.content.strip()

# --- Cache-aware public API ---
def get_cached_whitesands_facts(force: bool = False) -> str:
    if not force and CACHE_PATH.exists():
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if time.time() - data["timestamp"] < CACHE_TTL_SECONDS:
                return data["facts"]

    raw = scrape_whitesands_raw()
    facts = parse_whitesands_content(raw)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({"timestamp": time.time(), "facts": facts}, f, indent=2)

    return facts
