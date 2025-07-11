# app/main.py
import json
import os
import logging
import requests
import asyncio
from datetime import datetime
import subprocess
from kubernetes import client, config
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from watcher.ai import ai_suggest
from kubernetes import client, config as k8s_config
from pydantic import BaseModel
from watcher.config    import load_config
from watcher.embeddings import init_embedder
from watcher.retriever  import init_vectorstore
from watcher.models.suggestion import Suggestion



app = FastAPI()
cfg = load_config(path="config.yaml")


# CORS settings to connect frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"  # Mistral API URL
MISTRAL_API_KEY = "Ou8iIABg6zPu53XojL54xQOOgAF8QUki"  # Replace with your actual API key


# Function to get suggestions from Mistral API
def fetch_ai_suggestions():
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-small-latest",  # Ensure this is the correct model name
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Can you suggest ways to improve system performance?"}
        ],
        "max_tokens": 100  # Adjust based on the response length needed
    }

    # Send the POST request to Mistral's Chat API
    response = requests.post(MISTRAL_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        suggestion = data.get("choices", [{}])[0].get("message", {}).get("content", "No suggestion available")
        return suggestion
    else:
        return "Error fetching suggestion from Mistral API."

# Endpoint to get suggestions

@app.get("/api/suggestions")
def get_suggestions():
    try:
        suggestion_text = fetch_ai_suggestions()

        return JSONResponse(content={
            "suggestions": [
                {
                    "text": suggestion_text,
                    "severity": "medium",  # or dynamically assign based on content
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Endpoint to get restarted pods
# ✅ Corrected Endpoint to match frontend expectation
@app.get("/api/restarts")
def get_restarted_pods():
    try:
        config.load_kube_config()  # Load your local kube context
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces()

        restarted_pods = []
        for item in pods.items:
            statuses = item.status.container_statuses or []
            restarts = sum(s.restart_count for s in statuses)
            if restarts > 0:
                restarted_pods.append({
                    "name": item.metadata.name,
                    "namespace": item.metadata.namespace,
                    "restarts": restarts
                })

        return JSONResponse(content={"pods": restarted_pods})
    except Exception as e:
        print("🔥 Error:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)


# — AI-driven suggestion endpoint
@app.post("/api/suggestion", response_model=Suggestion)
async def suggestion_endpoint(payload: dict = Body(...)):
    # 1) Extract fields
    try:
        pod_name  = payload["pod_name"]
        namespace = payload["namespace"]
        logs      = payload["logs"]
    except KeyError as e:
        raise HTTPException(status_code=422, detail=f"Missing field: {e.args[0]}")

    # 2) Dynamic import (so pytest monkeypatch works)
    from watcher.ai import ai_suggest

    # 3) Call it
    result = ai_suggest(logs, pod_name, namespace)

    # 4) If it's a coroutine (i.e. async fake_ai), await it
    if asyncio.iscoroutine(result):
        result = await result

    # 5) Turn that dict into a Suggestion (fills in missing keys if needed)
    try:
        suggestion = Suggestion.parse_obj(result)
    except Exception:
        # fallback when ai_suggest returned {"action": "..."}
        action = result.get("action", "")
        suggestion = Suggestion(
            suggestion = action,
            severity   = "medium",
            confidence = 0.0,
            remediation= ""
        )
    return suggestion

    # 6) Otherwise assume it's already a dict
    return result

    # 1) Index this log snippet for future retrieval
    from watcher.chains.embeddings import index_log_chunks
    # chunk logs however you like; here’s a simple pass-through:
    index_log_chunks([logs], [{"pod_name": pod_name, "timestamp": datetime.utcnow().isoformat()}])

    # 2) Run the agent
    from watcher.chains.agent import run_troubleshooter
    ai_response = await run_troubleshooter(logs, pod_name, namespace)

    return {"agent_response": ai_response}  

embed_model  = init_embedder(cfg)
vectorstore  = init_vectorstore(cfg, embed_model)