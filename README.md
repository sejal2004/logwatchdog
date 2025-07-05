# LogWatchdog 🐶

> **AI-Powered Kubernetes Log Monitoring & Auto-Healing CLI Tool**

LogWatchdog is a lightweight, plug-and-play CLI that watches your Kubernetes pod logs in real-time, detects anomalies using LLMs (like OpenAI, Mistral, Claude), and auto-heals failing containers using smart restart logic.

> 🧠 Think **Grafana meets GPT for logs** — but fully CLI-native and AI-native.

---

## 🚀 Features

- 📡 Real-time Kubernetes log monitoring (via stdout or file)
- 🤖 LLM-based root cause diagnosis (OpenAI / Mistral / Claude)
- 🔁 Auto-restart pods with `kubectl` on failure
- 📣 Optional Slack alerts
- 🧩 YAML-based config support (`config.yaml`)
- ⚙️ Dry-run mode for safe testing
- ☁️ Fully containerized via Docker & deployable to any K8s cluster

---

## 📦 Installation

Install via `pip` (after cloning or publishing to PyPI):

```bash
pip install .
