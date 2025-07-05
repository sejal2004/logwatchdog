# watcher/chains/embeddings.py
import os

# — Safe‐guard LangChain imports
try:
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
except ImportError:
    # Minimal stubs so imports still succeed in tests
    class OpenAIEmbeddings:
        def __init__(self, *args, **kwargs): pass

    class Chroma:
        def __init__(self, *args, **kwargs): pass
        def add_texts(self, texts, metadatas): pass
        def persist(self): pass
        def as_retriever(self, **kwargs): return self

# Initialize (will be a no-op in tests)
embeddings = OpenAIEmbeddings(
    os.getenv("OPENAI_API_KEY", "")
)
vectorstore = Chroma(
    collection_name="log-chunks",
    embedding_function=embeddings,
    persist_directory="db/chroma"
)

def index_log_chunks(chunks: list[str], metadatas: list[dict]):
    vectorstore.add_texts(chunks, metadatas=metadatas)
    vectorstore.persist()
