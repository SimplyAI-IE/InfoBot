from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_static_style_css_served():
    response = client.get("/style.css")
    assert response.status_code == 200
    assert "body" in response.text  # adjust as needed for your CSS content

def test_static_chat_js_served():
    response = client.get("/chat.js")
    assert response.status_code == 200
    assert "function" in response.text  # basic JS sanity check

def test_index_html_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()
