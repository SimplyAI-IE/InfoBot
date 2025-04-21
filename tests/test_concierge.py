from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)


@patch("backend.apps.concierge.intent_gpt.client.chat.completions.create")
@patch("backend.apps.concierge.concierge_gpt.client.chat.completions.create")
def test_wifi_response(mock_concierge: MagicMock, mock_intent: MagicMock) -> None:
    mock_intent.return_value.choices = [MagicMock(message=MagicMock(content="wifi"))]
    mock_concierge.return_value.choices = [
        MagicMock(message=MagicMock(content="The WiFi password is welcome123."))
    ]

    response = client.post("/concierge", json={"message": "wifi"})
    assert response.status_code == 200
    assert "wifi" in response.json()["response"].lower()


@patch("backend.apps.concierge.intent_gpt.client.chat.completions.create")
@patch("backend.apps.concierge.concierge_gpt.client.chat.completions.create")
def test_activities_response(mock_concierge: MagicMock, mock_intent: MagicMock) -> None:
    mock_intent.return_value.choices = [MagicMock(message=MagicMock(content="activities"))]
    mock_concierge.return_value.choices = [MagicMock(message=MagicMock(content="Enjoy walking in Ballyheigue."))]

    response = client.post("/concierge", json={"message": "activities"})
    assert response.status_code == 200
    assert "ballyheigue" in response.json()["response"].lower() or "walk" in response.json()["response"].lower()


@patch("backend.apps.concierge.intent_gpt.client.chat.completions.create")
@patch("backend.apps.concierge.concierge_gpt.client.chat.completions.create")
def test_unknown_triggers_gpt(mock_concierge: MagicMock, mock_intent: MagicMock) -> None:
    mock_intent.return_value.choices = [MagicMock(message=MagicMock(content="unknown"))]
    mock_concierge.return_value.choices = [MagicMock(message=MagicMock(content="The weather is sunny."))]

    response = client.post("/concierge", json={"message": "what's the weather"})
    assert response.status_code == 200
    assert "sorry" not in response.json()["response"].lower()
