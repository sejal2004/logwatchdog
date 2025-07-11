import pytest

from watcher.chains.retriever import retrieve_related, qa_chain, search_logs

# --- Test the QA‐chain path ----------------------------------------------

@pytest.mark.asyncio
async def test_retrieve_related(monkeypatch):
    # Stub out the chain’s `arun` method to simulate a response
    async def fake_arun(query):
        assert query == "error happened"
        return "found similar logs"

    monkeypatch.setattr(qa_chain, "arun", fake_arun)

    out = await retrieve_related("error happened")
    assert out == "found similar logs"


# --- Test the embedding‐based retriever ---------------------------------

class DummyDoc:
    def __init__(self, content):
        self.page_content = content

class DummyEmbeddings:
    def embed(self, txt):
        # Ensure we receive exactly what was passed in
        assert txt in ("test query", "another query")
        return [1, 2, 3]

class DummyVectorStore:
    def similarity_search_by_vector(self, vec, k):
        # Ensure the right vector and k are used
        assert vec == [1, 2, 3]
        # Return a predictable set of DummyDocs
        return [DummyDoc("chunk1"), DummyDoc("chunk2")]

@pytest.fixture(autouse=True)
def patch_search(monkeypatch):
    # Monkey‐patch the embeddings & vectorstore clients in the retriever module
    import watcher.chains.retriever as mod
    monkeypatch.setattr(mod, "embeddings", DummyEmbeddings())
    monkeypatch.setattr(mod, "vectorstore", DummyVectorStore())

def test_search_logs_default():
    # Default top_k=5 (DummyVectorStore doesn’t check k)
    snippets = search_logs("test query")
    assert snippets == ["chunk1", "chunk2"]

def test_search_logs_custom_k():
    # Explicit top_k
    snippets = search_logs("another query", top_k=3)
    assert snippets == ["chunk1", "chunk2"]
