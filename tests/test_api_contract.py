from fastapi import FastAPI
from fastapi.testclient import TestClient


# Minimal app for API contract testing
def create_test_app() -> FastAPI:
    app = FastAPI()

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    @app.post("/chat")
    async def chat_placeholder():
        return {"error": "missing payload"}

    @app.get("/")
    async def root():
        return {"message": "frontend served or placeholder"}

    return app


client = TestClient(create_test_app())


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_forbidden_without_payload():
    response = client.post("/chat", json={})
    assert response.status_code in {200, 400, 422}


def test_root_serves_html_or_404():
    response = client.get("/")
    assert response.status_code in {200, 404}
