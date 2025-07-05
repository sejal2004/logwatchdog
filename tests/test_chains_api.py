# tests/test_chains_api.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_suggestion_with_chains(monkeypatch):
    # 0) Set dummy API keys before importing the app
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    monkeypatch.setenv("MISTRAL_API_KEY", "dummy-key")

    # 1) Stub the AI suggestion function
    def fake_ai_suggest(logs, pod_name, namespace):
        return {"agent_response": "agent says ok"}
    monkeypatch.setattr(
        "watcher.ai.ai_suggest",
        fake_ai_suggest
    )

    # 2) Import the FastAPI app after stubs and env are in place
    from app.main import app
    client = TestClient(app)

    # 3) Make the request
    payload = {
        "pod_name":  "web-1",
        "namespace": "default",
        "logs":      "Some error happened"
    }
    resp = client.post("/api/suggestion", json=payload)
    assert resp.status_code == 200

    # 4) Verify we get the stubbed AI response
    assert resp.json() == {"agent_response": "agent says ok"}
