# test_render.py
from utils.prompt_loader import load_and_render

payload = {
    "logs_excerpt": "Error: OOMKilled at 2025-07-10T12:00Z",
    "pod_name": "web-frontend-abc123",
    "namespace": "prod"
}

print(load_and_render("remediation-suggestion", payload))
