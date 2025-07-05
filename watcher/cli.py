import argparse
import os
from watcher.core import watch_logs

def main():
    parser = argparse.ArgumentParser(description="🔍 LogWatchdog - AI-powered K8s log auto-healer")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--label-selector", required=True, help="Label selector to filter pods")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML")
    parser.add_argument("--provider", choices=["mistral", "openai"], help="LLM provider to use")
    parser.add_argument("--dry-run", action="store_true", help="Only simulate actions, don't perform them")

    args = parser.parse_args()
    print("🚀 Starting LogWatchdog...")

    if args.provider:
        os.environ["AI_PROVIDER"] = args.provider

    watch_logs(args.namespace, args.label_selector, config_path=args.config)

if __name__ == "__main__":
    main()
