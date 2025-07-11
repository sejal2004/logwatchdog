import os
from watcher.chains.embeddings import embeddings, vectorstore

def search_logs(query: str, top_k: int = 5) -> list[str]:
    """
    Embed the query, retrieve the top_k most similar log chunks,
    and return their text content.
    """
    # 1) Make a query vector
    query_vec = embeddings.embed(query)

    # 2) Search the vectorstore
    results = vectorstore.similarity_search_by_vector(query_vec, k=top_k)

    # 3) Return the page_content of each Document
    return [doc.page_content for doc in results]


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

def init_vectorstore(cfg, embed_model):
    """
    Return the pre-configured vectorstore.
    Allows app/main.py to call init_vectorstore(cfg, embed_model).
    """
    return vectorstore
