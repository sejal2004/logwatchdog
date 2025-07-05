# tests/conftest.py
import os
import sys
import types

# 0) Insert project root (one level up) at the front of sys.path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)),
)

# 1) Stub out langchain_community and its llms submodule
lc_comn_pkg = types.ModuleType("langchain_community")
lc_comn_llms = types.ModuleType("langchain_community.llms")
sys.modules["langchain_community"] = lc_comn_pkg
sys.modules["langchain_community.llms"] = lc_comn_llms

# 2) Stub out langchain.llms and give it an OpenAI class
lc_llms_pkg = types.ModuleType("langchain.llms")

def OpenAI(*args, **kwargs):
    class DummyLLM:
        def __init__(self, *a, **k):
            pass
        async def __call__(self, *a, **k):
            return ""
    return DummyLLM()

lc_llms_pkg.OpenAI = OpenAI
sys.modules["langchain.llms"] = lc_llms_pkg

# 3) Stub out the summarize-chain builder
lc_sum_pkg = types.ModuleType("langchain.chains.summarize")

def load_summarize_chain(llm, chain_type="map_reduce"):
    class Summarizer:
        async def arun(self, docs):
            return "dummy summary"
    return Summarizer()

lc_sum_pkg.load_summarize_chain = load_summarize_chain
sys.modules["langchain.chains.summarize"] = lc_sum_pkg
pytest_plugins = ["pytest_asyncio"]