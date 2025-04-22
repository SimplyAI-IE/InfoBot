import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


@pytest.mark.skipif(
    "fake-ci-key" in os.getenv("OPENAI_API_KEY", "") or not os.getenv("OPENAI_API_KEY"),
    reason="Skipping GPT test due to missing or fake API key",
)
def test_whitesands_facts_live_scrape():
    response = client.get("/concierge/facts")
    assert response.status_code == 200

    facts = response.json().get("facts", "").lower()

    assert "check-in" in facts or "amenities" in facts or "contact" in facts
    assert len(facts) > 100


def test_full_whitesands_scrape_raw_content():
    from backend.apps.concierge.whitesands_scraper import scrape_whitesands_raw

    raw = scrape_whitesands_raw()
    assert isinstance(raw, str)
    assert len(raw) > 1000

    keywords = [
        "ballyheigue",
        "check-in",
        "restaurant",
        "facilities",
        "hotel",
        "dining",
    ]
    matches = [word for word in keywords if word in raw.lower()]
    assert len(matches) >= 2, f"Expected to find at least 2 key phrases, got: {matches}"


def test_scraped_content_includes_arnold_palmer():
    from backend.apps.concierge.whitesands_scraper import scrape_whitesands_raw

    raw = scrape_whitesands_raw()
    with open("scraped_whitesands.txt", "w", encoding="utf-8") as f:
        f.write(raw)

    assert "arnold palmer" in raw.lower()
