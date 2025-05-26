import logging
from slack_sdk import WebClient

logger = logging.getLogger(__name__)

def analyze_with_ai(log_line, provider="mistral"):
    if "crash" in log_line.lower() or "error" in log_line.lower():
        return "CRASH"
    return "OK"

def send_slack_message(message, cfg):
    try:
        slack_token = cfg["slack"].get("token")
        channel = cfg["slack"].get("channel")
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel=channel, text=message)
        logger.info("📨 Slack alert sent.")
    except Exception as e:
        logger.error(f"⚠️ Slack send failed: {e}")
