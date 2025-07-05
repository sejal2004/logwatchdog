from datetime import datetime, timedelta
from kubernetes import client, config
import logging

logger = logging.getLogger(__name__)
_restart_cache = {}

def was_recently_restarted(pod_name: str, cooldown: int = 60) -> bool:
    """
    Check if a pod was restarted within the cooldown window.

    Args:
        pod_name (str): The name of the pod.
        cooldown (int): Time in seconds to wait before allowing another restart.

    Returns:
        bool: True if pod was recently restarted, False otherwise.
    """
    now = datetime.utcnow()
    last_restart = _restart_cache.get(pod_name)

    if last_restart and (now - last_restart) < timedelta(seconds=cooldown):
        logger.debug(f"⏱️ Pod {pod_name} was restarted {int((now - last_restart).total_seconds())}s ago — within cooldown.")
        return True

    _restart_cache[pod_name] = now
    return False

def restart_pod(namespace: str, pod_name: str):
    """
    Restart a pod by deleting it from the specified namespace.

    Args:
        namespace (str): Kubernetes namespace where the pod is running.
        pod_name (str): The name of the pod to restart.
    """
    try:
        config.load_incluster_config()
        logger.debug("✅ Loaded in-cluster Kubernetes config.")
    except config.ConfigException:
        config.load_kube_config()
        logger.debug("✅ Loaded local kubeconfig.")

    v1 = client.CoreV1Api()
    logger.info(f"🔄 Deleting pod {pod_name} in namespace {namespace} to trigger restart...")
    try:
        v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        logger.info(f"✅ Successfully triggered restart for pod {pod_name}.")
    except Exception as e:
        logger.exception(f"❌ Failed to restart pod {pod_name}: {e}")
