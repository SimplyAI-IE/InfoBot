from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)


@patch("backend.apps.concierge.concierge_gpt.client.chat.completions.create")
def test_wifi_response(mock_create: MagicMock) -> None:
    mock_create.return_value.choices = [MagicMock(message=MagicMock(content="WiFi is free throughout the hotel."))]
    response = client.post("/concierge", json={"message": "wifi"})
    assert response.status_code == 200
    assert "wifi" in response.json()["response"].lower()


@patch("backend.apps.concierge.concierge_gpt.client.chat.completions.create")
def test_activities_response(mock_create: MagicMock) -> None:
    mock_create.return_value.choices = [MagicMock(message=MagicMock(content="Ballyheigue is great for beach walks."))]
    response = client.post("/concierge", json={"message": "activities"})
    assert response.status_code == 200
    assert "ballyheigue" in response.json()["response"].lower() or "walk" in response.json()["response"].lower()


@patch("backend.apps.concierge.concierge_gpt.client.chat.completions.create")
def test_unknown_triggers_gpt(mock_create: MagicMock) -> None:
    mock_create.return_value.choices = [MagicMock(message=MagicMock(content="The weather looks fine today."))]
    response = client.post("/concierge", json={"message": "what's the weather"})
    assert response.status_code == 200
    assert "sorry" not in response.json()["response"].lower()
