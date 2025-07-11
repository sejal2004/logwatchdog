# watcher/retriever.py

# Re-export everything your app expects
from watcher.chains.retriever import init_vectorstore, search_logs, retrieve_related, qa_chain

__all__ = [
    "init_vectorstore",
    "search_logs",
    "retrieve_related",
    "qa_chain",
]
