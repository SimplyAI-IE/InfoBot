from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_chat_forbidden_without_payload():
    response = client.post("/chat", json={})
    assert response.status_code in {422, 400}

def test_root_serves_html_or_404():
    response = client.get("/")
    assert response.status_code in {200, 404}
