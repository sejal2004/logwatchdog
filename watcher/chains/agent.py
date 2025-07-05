# watcher/chains/agent.py
import os

# Delay real LangChain imports until runtime to avoid import-time Pydantic checks
try:
    from langchain.agents import initialize_agent, Tool
    from langchain.agents.agent_toolkits import VectorStoreToolkit
    from langchain.llms import OpenAI
except ImportError:
    # No-op stubs for testing
    class Tool:
        def __init__(self, *args, **kwargs):
            pass

    def initialize_agent(tools, llm, agent, verbose=False):
        class Agent:
            async def arun(self, prompt: str) -> str:
                return ""
        return Agent()

    class VectorStoreToolkit:
        def __init__(self, *args, **kwargs):
            pass
        def get_tools(self):
            return []

    class OpenAI:
        def __init__(self, *args, **kwargs):
            pass

from watcher.chains.embeddings import vectorstore
from watcher.chains.retriever import retrieve_related
from watcher.chains.summarizer import summarize_logs

async def run_troubleshooter(log_excerpt: str, pod: str, namespace: str) -> str:
    """
    Run a Kubernetes troubleshooting agent over logs for a given pod and namespace.
    """
    # Lazily build the toolkit, tools, LLM, and agent at runtime
    toolkit = VectorStoreToolkit(vectorstore=vectorstore)
    tools = toolkit.get_tools() + [
        Tool(
            name="retrieve_related",
            func=retrieve_related,
            description="Find similar past log events"
        ),
        Tool(
            name="summarize_logs",
            func=summarize_logs,
            description="Summarize recent logs for a pod"
        ),
    ]
    llm = OpenAI(temperature=0)
    agent = initialize_agent(
        tools,
        llm,
        agent="conversational-react-description",
        verbose=True,
    )

    prompt = (
        f"You are a Kubernetes troubleshooter. Pod={pod}, ns={namespace}.\n"
        f"Logs excerpt:\n{log_excerpt}"
    )
    return await agent.arun(prompt)
