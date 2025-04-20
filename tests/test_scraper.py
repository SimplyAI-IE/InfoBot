from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_whitesands_facts_live_scrape():
    response = client.get("/concierge/facts")
    assert response.status_code == 200

    facts = response.json().get("facts", "").lower()

    # Validate some expected patterns
    assert "check-in" in facts or "amenities" in facts or "contact" in facts
    assert len(facts) > 100  # sanity check for non-empty GPT output
    
def test_full_whitesands_scrape_raw_content():
    from backend.apps.concierge.whitesands_scraper import scrape_whitesands_raw

    raw = scrape_whitesands_raw()
    assert isinstance(raw, str)
    assert len(raw) > 1000  # Expecting multiple pages worth of content

    # Spot-check for expected hotel-related keywords
    keywords = ["ballyheigue", "check-in", "restaurant", "facilities", "hotel", "dining"]
    matches = [word for word in keywords if word in raw.lower()]

    assert len(matches) >= 2, f"Expected to find at least 2 key phrases, got: {matches}"

