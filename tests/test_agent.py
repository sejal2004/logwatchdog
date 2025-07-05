# tests/test_agent.py

import pytest

from watcher.chains.agent import run_troubleshooter

class DummyAgent:
    async def arun(self, prompt: str) -> str:
        return "step1 → step2"

class DummyToolkit:
    def __init__(self, vectorstore):
        # ignore the passed vectorstore
        pass

    def get_tools(self):
        return []

@pytest.mark.asyncio
async def test_run_troubleshooter(monkeypatch):
    # 1) Stub VectorStoreToolkit to avoid real Pydantic validation
    monkeypatch.setattr(
        "watcher.chains.agent.VectorStoreToolkit",
        DummyToolkit
    )

    # 2) Stub initialize_agent to return DummyAgent
    monkeypatch.setattr(
        "watcher.chains.agent.initialize_agent",
        lambda tools, llm, agent, verbose: DummyAgent()
    )

    # 3) Stub summarize_logs to avoid external dependencies
    monkeypatch.setattr(
        "watcher.chains.agent.summarize_logs",
        lambda pod_name: "dummy summary"
    )

    # 4) Call run_troubleshooter
    result = await run_troubleshooter(
        log_excerpt="error line 1\nerror line 2",
        pod="podA",
        namespace="ns1"
    )

    # 5) Verify the output from DummyAgent is returned
    assert result == "step1 → step2"
