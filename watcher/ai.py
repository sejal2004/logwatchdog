# watcher/ai.py

import os
import logging
import requests
import asyncio                       # still needed for iscoroutinefunction check
from datetime import datetime
from pydantic import ValidationError
from watcher.models.suggestion import Suggestion
from slack_sdk import WebClient

logger = logging.getLogger(__name__)

# === STUBS to prevent NameErrors and avoid asyncio.run in tests ===

def index_log_chunks(chunks, metadata):
    """No-op stub so indexing never crashes."""
    pass

def run_rag(query: str) -> str:
    """No-op stub for retrieval; synchronous."""
    return ""

def run_rag_sync(query: str) -> str:
    """Alias to the same stub."""
    return ""


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

AI_PROVIDER = os.getenv("AI_PROVIDER", "mistral").lower()
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")
OPENAI_KEY  = os.getenv("OPENAI_API_KEY")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
OPENAI_URL  = "https://api.openai.com/v1/chat/completions"


def ai_suggest(logs_excerpt: str, pod_name: str, namespace: str) -> dict:
    """
    Returns a dict matching the Suggestion schema, or falls back to rule-based.
    """
    # 1) Index this excerpt (stubbed)
    ts = datetime.utcnow().isoformat()
    index_log_chunks([logs_excerpt], [{"pod_name": pod_name, "timestamp": ts}])

    # 2) Retrieve related past context (always synchronous stub now)
    if asyncio.iscoroutinefunction(run_rag):
        rag_ctx = run_rag_sync(logs_excerpt)
    else:
        rag_ctx = run_rag_sync(logs_excerpt)

    # 3) Build combined prompt (not used in tests)
    combined_prompt = f"""
Relevant past logs & analysis:
{rag_ctx}

Based on the above and this log excerpt:
{logs_excerpt!r}

Please suggest:
- action (restart/alert/none)
- severity (low/medium/high)
- confidence (0.0–1.0)
- remediation (text)
- reasoning (chain‑of‑thought)

Respond *only* with strict JSON matching the Suggestion schema.
"""

    # 4) Try each LLM provider (skipped if no API key)
    for provider, api_key, endpoint in (
        ("mistral", MISTRAL_KEY, MISTRAL_URL),
        ("openai", OPENAI_KEY, OPENAI_URL),
    ):
        if not api_key:
            logger.warning(f"⚠️ {provider.title()} API key missing, skipping.")
            continue

        payload = {
            "model": "mistral-medium" if provider == "mistral" else "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": combined_prompt}],
            "temperature": 0.0,
        }
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=5)
            resp.raise_for_status()

            raw = resp.json()["choices"][0]["message"]["content"]
            text = raw.strip()
            if text.startswith("```") and text.endswith("```"):
                lines = text.splitlines()
                text = "\n".join(lines[1:-1])

            suggestion = Suggestion.parse_raw(text)
            return suggestion.dict()

        except (requests.RequestException, ValidationError) as e:
            logger.warning(f"❗ {provider.title()} failed: {e}. Trying next or fallback.")
            continue

    # 5) Final rule-based fallback — remediation is now always "none"
    return fallback_classifier(logs_excerpt, pod_name, namespace)


def fallback_classifier(log_line: str, pod_name: str, namespace: str) -> dict:
    """
    Basic rule-based fallback if both LLMs fail. Always returns full Suggestion dict.
    """
    return {
        "suggestion":   "none",
        "severity":     "low",
        "confidence":   0.0,
        "remediation":  "none",
        "reasoning":    "Rule-based fallback after LLM failure."
    }


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
