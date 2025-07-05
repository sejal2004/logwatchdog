# watcher/ai.py
import os
import logging
import requests
from pydantic import ValidationError
from watcher.models.suggestion import Suggestion
from slack_sdk import WebClient

logger = logging.getLogger(__name__)

# === Constant prompt template ===
SYSTEM_PROMPT = """
You are an intelligent Kubernetes troubleshooter.
Given these logs: {logs_excerpt!r}
And this pod context: name={pod_name!r}, namespace={namespace!r}

Respond *only* with JSON matching this schema:
{{
  "suggestion": "string",
  "severity": "low|medium|high",
  "confidence": 0.0–1.0,
  "remediation": "string"
}}
Do not include any extra keys or prose—raw JSON only.
"""


# === Provider selection ===
AI_PROVIDER   = os.getenv("AI_PROVIDER",   "mistral").lower()
MISTRAL_KEY   = os.getenv("MISTRAL_API_KEY")
OPENAI_KEY    = os.getenv("OPENAI_API_KEY")
MISTRAL_URL   = "https://api.mistral.ai/v1/chat/completions"
OPENAI_URL    = "https://api.openai.com/v1/chat/completions"

def ai_suggest(logs_excerpt: str, pod_name: str, namespace: str) -> dict:
    """
    Returns a dict matching the Suggestion schema, or falls back to rule-based.
    """
    prompt = SYSTEM_PROMPT.format(
        logs_excerpt=logs_excerpt,
        pod_name=pod_name,
        namespace=namespace
    )

    # Try Mistral then OpenAI
    for provider, api_key, endpoint in (
        ("mistral", MISTRAL_KEY, MISTRAL_URL),
        ("openai", OPENAI_KEY, OPENAI_URL)
    ):
        if not api_key:
            logger.warning(f"⚠️ {provider.title()} API key missing, skipping.")
            continue

        payload = {
            "model": "mistral-medium" if provider == "mistral" else "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0
        }
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=5)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            # Validate & parse strict JSON
            suggestion = Suggestion.parse_raw(content)
            return suggestion.dict()
        except (requests.RequestException, ValidationError) as e:
            logger.warning(f"❗ {provider.title()} failed: {e}. Trying next or fallback.")
            continue

    # Final rule-based fallback
    return fallback_classifier(logs_excerpt)


def fallback_classifier(log_line: str) -> dict:
    """Basic rule-based fallback if both LLMs fail."""
    text = log_line.lower()
    if "crash" in text or "error" in text:
        return {"action": "restart"}
    return {"action": "none"}


def send_slack_message(message: str, cfg: dict):
    """Unchanged Slack notifier."""
    try:
        token   = cfg["slack"].get("token")
        channel = cfg["slack"].get("channel")
        client  = WebClient(token=token)
        client.chat_postMessage(channel=channel, text=message)
        logger.info("📩 Slack alert sent.")
    except Exception as e:
        logger.error(f"⚠️ Slack send failed: {e}")
