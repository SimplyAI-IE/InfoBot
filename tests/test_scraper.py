import os

from fastapi.testclient import TestClient
import pytest

from backend.apps.concierge.whitesands_scraper import scrape_whitesands_raw
from backend.main import app

client = TestClient(app)


@pytest.mark.external
@pytest.mark.skipif(
    os.getenv("OPENAI_API_KEY", "") in ["", "test-key", "fake-ci-key"],
    reason="Skipping GPT test due to missing or fake API key",
)
def test_whitesands_facts_live_scrape():
    response = client.get("/concierge/facts")
    assert response.status_code == 200, "Expected 200 OK response from /concierge/facts"

    facts = response.json().get("facts", "").lower()
    assert any(
        keyword in facts for keyword in ["check-in", "amenities", "contact"]
    ), "Expected key terms in facts"
    assert len(facts) > 100, "Facts response too short"


@pytest.mark.external
def test_full_whitesands_scrape_raw_content():
    raw = scrape_whitesands_raw()
    assert isinstance(raw, str), "Raw content should be a string"
    assert len(raw) > 1000, "Scraped content too short"

    keywords = [
        "ballyheigue",
        "check-in",
        "restaurant",
        "facilities",
        "hotel",
        "dining",
    ]
    matches = [word for word in keywords if word in raw.lower()]
    assert (
        len(matches) >= 2
    ), f"Expected at least 2 keywords in raw content, found: {matches}"


@pytest.mark.external
def test_scraped_content_includes_arnold_palmer():
    raw = scrape_whitesands_raw()
    with open("scraped_whitesands.txt", "w", encoding="utf-8") as f:
        f.write(raw)

    assert "arnold palmer" in raw.lower(), "Expected 'arnold palmer' in scraped content"
