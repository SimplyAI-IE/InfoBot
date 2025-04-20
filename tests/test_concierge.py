from fastapi.testclient import TestClient
from backend.main import app  # Make sure this points to your FastAPI app

client = TestClient(app)

def test_wifi_response():
    response = client.post("/concierge", json={"message": "wifi"})
    assert response.status_code == 200
    assert "white" in response.json()["response"].lower()

def test_activities_response():
    response = client.post("/concierge", json={"message": "activities"})
    assert response.status_code == 200
    assert "ballyheigue" in response.json()["response"].lower() or "walk" in response.json()["response"].lower()

def test_unknown_triggers_gpt():
    response = client.post("/concierge", json={"message": "what's the weather"})
    assert response.status_code == 200
    assert "sorry" not in response.json()["response"].lower()  # should be GPT generated
