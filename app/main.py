# app/main.py
from dotenv import load_dotenv
load_dotenv()   # <-- this reads .env into os.environ

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
import watcher.ai as ai_module
from kubernetes import client, config as k8s_config
from pydantic import BaseModel
from pydantic import ValidationError
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

@app.post("/api/suggestion", response_model=Suggestion, response_model_exclude={"reasoning"})
async def suggestion_endpoint(
    pod_name: str = Body(..., embed=True),
    namespace: str = Body(..., embed=True),
    logs: str = Body(..., embed=True),
):
    """
    Take pod_name, namespace and logs from the request body,
    hand them off to ai_suggest(), and guarantee we always return
    a fully‐formed Suggestion object.
    """
    try:
        # 1) Call the AI helper
        import watcher.ai as _ai_mod
        result = ai_module.ai_suggest(logs, pod_name, namespace)
        if asyncio.iscoroutine(result):
            result = await result

        # 2) Try to validate what came back
        try:
            suggestion = Suggestion.model_validate(result)
        except ValidationError as ve:
            # If the LLM output was malformed, log and build our own fallback
            logging.warning("🚨 Suggestion validation failed, falling back: %s", ve)
            # If ai_suggest returned a custom dict (e.g. {"agent_response": …}), forward it
            if "agent_response" in result:
                return JSONResponse(content=result)

            suggestion = Suggestion(
                suggestion  = result.get("action", "none"),
                severity    = result.get("severity", "low"),
                confidence  = result.get("confidence", 0.0),
                remediation = result.get("remediation", ""),
                reasoning   = result.get("reasoning", "") or "Rule‑based fallback after malformed AI output."
            )

        # 3) (Optional) dump out the chain‑of‑thought
        logging.getLogger("app").debug("LLM reasoning: %s", suggestion.reasoning)

        # 4) Return it
        return suggestion

    except HTTPException:
        # Re‑raise any HTTPExceptions we explicitly threw above
        raise

    except Exception:
        # Catch everything else, log full traceback, return 500
        logging.exception("💥 Unexpected error in /api/suggestion")
        raise HTTPException(status_code=500, detail="Internal server error, see logs")

@app.on_event("startup")
async def load_vectorstore():
    """
    Defer loading of embeddings & vectorstore until AFTER the server is live,
    so that `uvicorn app.main:app` can start immediately.
    """
    global embed_model, vectorstore
    embed_model  = init_embedder(cfg)
    vectorstore  = init_vectorstore(cfg, embed_model)
@app.get("/ping")
def ping():
    return {"pong": True}

