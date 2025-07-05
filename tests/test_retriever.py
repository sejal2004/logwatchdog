import pytest
from watcher.chains.retriever import retrieve_related, qa_chain

@pytest.mark.asyncio
async def test_retrieve_related(monkeypatch):
    # Stub out the chain’s `arun` method
    async def fake_arun(query):
        return "found similar logs"
    monkeypatch.setattr(qa_chain, "arun", fake_arun)

    out = await retrieve_related("error happened")
    assert out == "found similar logs"
