# watcher/chains/summarizer.py
import os
from watcher.chains.embeddings import vectorstore
#from watcher.chains.retriever import llm
from langchain.text_splitter import CharacterTextSplitter

def chunk_logs(
    text: str,
    source_file: str | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> tuple[list[str], list[dict]]:
    """
    Split `text` into chunks and return (chunks, metadatas).
    Each metadata dict includes the source_file and chunk index.
    """
    splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    texts = splitter.split_text(text)
    metadatas = [
        {"source_file": source_file, "chunk_index": i}
        for i in range(len(texts))
    ]
    return texts, metadatas

async def summarize_logs(pod_name: str) -> str:
    # only import & build the chain when we actually need it
    from langchain.chains.summarize import load_summarize_chain
    from langchain.docstore.document import Document

    chain = load_summarize_chain(llm, chain_type="map_reduce")

    # fetch your stored logs and wrap them as LangChain Documents
    docs = vectorstore.search_documents_by_filter({"pod_name": pod_name})
    lc_docs = [Document(d.page_content, d.metadata) for d in docs]

    # run the summarize chain at runtime
    return await chain.arun(lc_docs)
