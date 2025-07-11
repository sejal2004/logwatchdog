# watcher/chains/embeddings.py
import os
from watcher.config import load_config
cfg = load_config()   # pulls in embedding_model, vectorstore_type, vectorstore_path

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

EMBED_MODEL_NAME = cfg["embedding_model"]
# Initialize (will be a no-op in tests)
embeddings = OpenAIEmbeddings(
    model=EMBED_MODEL_NAME,
    openai_api_key=os.getenv("OPENAI_API_KEY", "")
)
VSTORE_TYPE = cfg["vectorstore_type"].lower()
VSTORE_PATH = cfg["vectorstore_path"]

# ensure the disk location exists
os.makedirs(os.path.dirname(VSTORE_PATH), exist_ok=True)

if VSTORE_TYPE == "chroma":
    # Chroma expects a directory
    vectorstore = Chroma(
        collection_name="log-chunks",
        embedding_function=embeddings,
        persist_directory=VSTORE_PATH
    )
elif VSTORE_TYPE == "faiss":
    from langchain.vectorstores import FAISS

    if os.path.exists(VSTORE_PATH):
        vectorstore = FAISS.load_local(VSTORE_PATH, embeddings)
    else:
        # start empty; you’ll ingest texts before persisting
        vectorstore = FAISS.from_texts([], embeddings, persist_directory=os.path.dirname(VSTORE_PATH))
else:
    raise ValueError(f"Unsupported vectorstore_type: {VSTORE_TYPE}")

def index_log_chunks(chunks: list[str], metadatas: list[dict]):
    vectorstore.add_texts(chunks, metadatas=metadatas)
    vectorstore.persist()
    
def init_embedder(cfg):
    """
    Return the pre-configured embeddings client.
    This lets app/main.py call init_embedder(cfg) even though
    the real setup lives above.
    """
    return embeddings
