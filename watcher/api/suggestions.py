# watcher/api/suggestions.py
import json
from fastapi import APIRouter, Body, Header, HTTPException

from watcher.chains.retriever import search_logs
from watcher.ai import fetch_ai_suggestions
from watcher.models.suggestion import Suggestion

router = APIRouter()

@router.post(
    "/suggestions",
    response_model=Suggestion,
    summary="Get a structured, log-aware suggestion"
)
async def suggest(
    query: str = Body(..., description="Your incident or error message"),
    session_id: str = Header(None, description="Optional session for memory"),
):
    # 1) Retrieve the top-5 most relevant log chunks
    snippets = search_logs(query, top_k=5)

    # 2) Build a strict-JSON prompt for the LLM
    prompt = """
You are an observability assistant. Given an error and its context, respond in **strict JSON** with these keys:
- suggestion: what to do next
- severity: one of low, medium, high
- confidence: a float between 0 and 1
- remediation: the exact CLI command or code snippet to run

Here are relevant log excerpts:
{snippets}

Error: {query}

Respond *only* with the JSON object.
""".strip().format(
        snippets="\n".join(f"- {s}" for s in snippets),
        query=query
    )

    # 3) Ask the AI for a JSON response
    raw = await fetch_ai_suggestions(prompt, session_id=session_id)

    # 4) Parse & validate JSON
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(502, f"Invalid JSON from AI: {raw!r}")

    # 5) Coerce into your Pydantic model (will 422 if invalid)
    return Suggestion(**obj)
