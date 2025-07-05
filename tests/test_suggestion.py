import pytest
from pydantic import ValidationError
from watcher.models.suggestion import Suggestion

VALID_JSON = """
{
  "suggestion": "Restart the pod",
  "severity": "medium",
  "confidence": 0.87,
  "remediation": "kubectl rollout restart pod my-pod"
}
"""

INVALID_JSON = """
{
  "suggestion": "Fix it",
  "severity": "urgent"
  /* missing confidence & remediation */
}
"""

def test_valid_suggestion_parses():
    s = Suggestion.parse_raw(VALID_JSON)
    assert s.suggestion == "Restart the pod"
    assert s.severity == "medium"
    assert 0 <= s.confidence <= 1
    assert s.remediation.startswith("kubectl")

def test_invalid_suggestion_raises():
    with pytest.raises(ValidationError):
        Suggestion.parse_raw(INVALID_JSON)
