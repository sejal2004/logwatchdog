# watcher/chains/summarizer.py

from watcher.chains.embeddings import vectorstore
from watcher.chains.retriever import llm

async def summarize_logs(pod_name: str) -> str:
    """
    Summarize logs for a given pod by building the LangChain map-reduce chain at runtime.
    """
    # Lazy import and instantiation to avoid import-time validation
    from langchain.chains.summarize import load_summarize_chain
    from langchain.docstore.document import Document

    chain = load_summarize_chain(llm, chain_type="map_reduce")

    # Fetch stored logs and wrap them as LangChain Documents
    docs = vectorstore.search_documents_by_filter({"pod_name": pod_name})
    lc_docs = [Document(page_content=d.page_content, metadata=d.metadata) for d in docs]

    # Run the summarize chain and return its output
    return await chain.arun(lc_docs)
