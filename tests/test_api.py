import pytest
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app              # adjust path if your FastAPI app is elsewhere
from watcher.models.suggestion import Suggestion

client = TestClient(app)

@pytest.fixture(autouse=True)
def stub_ai(monkeypatch):
    # stub out ai_suggest so we don’t actually call any LLM
    async def fake_ai(logs_excerpt, pod_name, namespace):
        return Suggestion(
            suggestion="No action needed",
            severity="low",
            confidence=0.5,
            remediation="none"
        )
    # patch the function in watcher.ai
    monkeypatch.setattr("watcher.ai.ai_suggest", fake_ai)

def test_suggestion_endpoint_returns_valid_shape():
    payload = {
        "pod_name": "web-1",
        "namespace": "default",
        "logs": "Some error happened"
    }
    resp = client.post("/api/suggestion", json=payload)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    # exactly these four keys must be present
    assert set(data.keys()) == {"suggestion","severity","confidence","remediation"}
    assert data["severity"] == "low"
    assert data["remediation"] == "none"
