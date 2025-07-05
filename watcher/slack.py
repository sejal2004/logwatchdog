import logging
from slack_sdk import WebClient

logger = logging.getLogger(__name__)

def send_slack_message(message, cfg):
    try:
        slack_token = cfg["slack"].get("token")
        channel = cfg["slack"].get("channel")
        client = WebClient(token=slack_token)
        client.chat_postMessage(channel=channel, text=message)
        logger.info("📨 Slack alert sent.")
    except Exception as e:
        logger.error(f"⚠️ Slack send failed: {e}")
