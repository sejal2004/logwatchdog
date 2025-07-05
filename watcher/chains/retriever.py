# watcher/chains/retriever.py
import os
from watcher.chains.embeddings import vectorstore

# Attempt to import and build a real QA chain
try:
    from langchain.llms import OpenAI
    from langchain.chains import RetrievalQA

    llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # or "map_rerank"
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5})
    )

except Exception:
    # On any failure (missing module, validation error, etc.) fall back to a stub
    class QAStub:
        async def arun(self, query: str) -> str:
            return ""

    qa_chain = QAStub()

async def retrieve_related(log_excerpt: str) -> str:
    """
    Returns an LLM-driven answer to: "Given this log, what similar events happened before?"
    """
    return await qa_chain.arun(log_excerpt)