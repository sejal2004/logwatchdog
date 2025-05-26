import yaml
import os
from dotenv import load_dotenv

load_dotenv()

def load_config(path="config.yaml"):
    config = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            config = yaml.safe_load(f) or {}

    # Env overrides
    config.setdefault("ai_provider", os.getenv("AI_PROVIDER", "mistral"))
    config.setdefault("restart_on_crash", os.getenv("RESTART_ON_CRASH", "true").lower() == "true")

    config["slack"] = config.get("slack", {})
    config["slack"]["token"] = os.getenv("SLACK_TOKEN", config["slack"].get("token"))
    config["slack"]["channel"] = os.getenv("SLACK_CHANNEL", config["slack"].get("channel"))
    
    return config

