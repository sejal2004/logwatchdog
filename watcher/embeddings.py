# watcher/embeddings.py

# Re-export everything your app expects
from watcher.chains.embeddings import init_embedder, index_log_chunks, embeddings, vectorstore

__all__ = [
    "init_embedder",
    "index_log_chunks",
    "embeddings",
    "vectorstore",
]
