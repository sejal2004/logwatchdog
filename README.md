# LogWatchdog 🐶  
**AI-Powered Kubernetes Log Monitoring & Auto-Healing Tool**

LogWatchdog is a lightweight, pluggable CLI tool that watches your Kubernetes logs in real-time, detects anomalies using LLMs (OpenAI, Mistral, Claude), and auto-heals your containers using smart restart logic.

> Think Grafana meets GPT for logs — but CLI-native and AI-native.

---

## 🚀 Features

- Real-time Kubernetes log monitoring
- LLM-based root cause analysis
- Auto-restart containers on crash
- Optional Slack alerts
- Supports `config.yaml` for full control
- Works with OpenAI, Mistral, Claude via ENV variables

---

## 📦 Installation

```bash
pip install logwatchdog
