import argparse
from watcher.core import watch_logs

def main():
    parser = argparse.ArgumentParser(description="LogWatchdog: AI-powered Kubernetes log watcher")
    parser.add_argument("--namespace", default="logwatchdog", help="Kubernetes namespace to watch")
    parser.add_argument("--label", default="app=crash-app", help="Label selector for pods")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    watch_logs(namespace=args.namespace, label_selector=args.label, config_path=args.config)
