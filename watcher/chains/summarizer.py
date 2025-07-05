# watcher/chains/summarizer.py

from watcher.chains.embeddings import vectorstore
from watcher.chains.retriever import llm

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
