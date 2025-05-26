from watcher.config import load_config
from watcher.ai import analyze_with_ai, send_slack_message
from kubernetes import client, config, watch
import logging

logger = logging.getLogger(__name__)

def restart_pod(pod_name, namespace):
    v1 = client.CoreV1Api()
    v1.delete_namespaced_pod(pod_name, namespace)
    logger.info(f"🔁 Restarted pod: {pod_name}")

def watch_logs(namespace="logwatchdog", label_selector="app=crash-app", config_path="config.yaml"):
    cfg = load_config(config_path)
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()

    try:
        pods = v1.list_namespaced_pod(namespace, label_selector=label_selector).items
        for pod in pods:
            pod_name = pod.metadata.name
            logger.info(f"📦 Watching logs from {pod_name}")
            stream = w.stream(v1.read_namespaced_pod_log, name=pod_name, namespace=namespace, follow=True, _preload_content=False)

            for line in stream:
                decoded_line = line.decode("utf-8").strip()
                logger.info(f"{pod_name}: {decoded_line}")
                ai_result = analyze_with_ai(decoded_line, cfg["ai_provider"])
                if ai_result == "CRASH":
                    if cfg.get("slack", {}).get("enabled"):
                        send_slack_message(f"🚨 Crash detected in {pod_name}:\n{decoded_line}", cfg)
                    if cfg.get("restart_on_crash", True):
                        restart_pod(pod_name, namespace)

    except Exception as e:
        logger.error(f"❌ Log watcher crashed: {e}")
