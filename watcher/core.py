import logging
import time
from kubernetes import client, config
from watcher.ai import ai_suggest
from watcher.utils import restart_pod, was_recently_restarted
from watcher.slack import send_slack_message
import yaml
import os
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ✅ Load Kubernetes configuration
try:
    config.load_incluster_config()
    logger.info("✅ Loaded in-cluster Kubernetes config.")
except config.ConfigException:
    try:
        config.load_kube_config()
        logger.info("✅ Loaded local Kubernetes config.")
    except config.ConfigException as e:
        logger.error("❌ Failed to load Kubernetes config (neither in-cluster nor local).")
        raise e

def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def watch_logs(namespace, label_selector, config_path):
    cfg = load_config(config_path) or {}  # ✅ Safely fallback to empty dict
    v1 = client.CoreV1Api()

    logger.info(f"📡 Watching all pods in namespace '{namespace}' with label '{label_selector}'")


    while True:
        try:
            pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
            for pod in pods.items:
                pod_name = pod.metadata.name

                logs = v1.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    tail_lines=10,
                    timestamps=True,
                ).splitlines()

                for log_line in logs:
                    if not log_line.strip():
                        continue

                    logger.debug(f"📜 {pod_name}: {log_line}")
                    suggestion = ai_suggest(log_line)
                    logger.info(f"🤖 AI Suggestion: {suggestion}")

                    if suggestion.get("action") == "restart":
                        if was_recently_restarted(pod_name, cfg.get("restart_cooldown", 60)):
                            logger.warning(f"⏳ Skipping restart: {pod_name} was restarted recently.")
                            continue

                        restart_pod(namespace, pod_name)
                        logger.info(f"🔁 Restarted pod {pod_name} in namespace: {namespace}")

                    elif suggestion.get("action") == "alert":
                        send_slack_message(log_line, cfg)
                        logger.info(f"📨 Sent Slack alert for {pod_name}")

            time.sleep(10)

        except Exception as e:
            logger.exception(f"❌ Error while watching logs: {e}")
            time.sleep(5)
def save_suggestions(suggestions):
    with open("logs/latest_suggestions.json", "w") as f:
        json.dump({"suggestions": suggestions}, f)