import pytest
from watcher.chains.embeddings import index_log_chunks, vectorstore

def test_index_log_chunks(tmp_path, monkeypatch):
    # Patch the Chroma vectorstore to record calls instead of real I/O
    added = []
    class FakeVS:
        def add_texts(self, chunks, metadatas):
            added.append((chunks, metadatas))
        def persist(self):
            pass

    monkeypatch.setattr(vectorstore, "add_texts", FakeVS().add_texts)
    monkeypatch.setattr(vectorstore, "persist", FakeVS().persist)

    chunks = ["line1", "line2"]
    metas = [{"pod_name": "a"}, {"pod_name": "b"}]
    index_log_chunks(chunks, metas)

    assert added == [(chunks, metas)]
