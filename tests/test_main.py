# tests/test_main.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_summarize_success(monkeypatch):
    # stub out generate_summary to isolate the endpoint
    monkeypatch.setattr("app.main.generate_summary", lambda text: "OK summary")
    r = client.post("/summarize", json={"text": "Some note"})
    assert r.status_code == 200
    assert r.json() == {"summary": "OK summary"}

def test_summarize_empty_input():
    r = client.post("/summarize", json={"text": ""})
    assert r.status_code == 400
    assert "empty" in r.json()["detail"].lower()

def test_summarize_api_failure(monkeypatch):
    # simulate downstream error
    def fail(text): raise RuntimeError("downstream")
    monkeypatch.setattr("app.main.generate_summary", fail)
    r = client.post("/summarize", json={"text": "Note"})
    assert r.status_code == 502

def test_feedback():
    payload = {"request_id": "abc123", "feedback": "Looks good"}
    r = client.post("/feedback", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["message"] == "Feedback recorded"
    assert body["request_id"] == "abc123"


def test_feedback_empty_input():
    """
    If the client submits only whitespace or an empty string for feedback,
    the API should return HTTP 400.
    """
    payload = {"request_id": "test123", "feedback": "   "}
    r = client.post("/feedback", json=payload)
    assert r.status_code == 400
    assert "feedback" in r.json()["detail"].lower()
