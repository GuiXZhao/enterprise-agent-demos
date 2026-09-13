"""文档检索工具（读取 Demo A 向量库）。"""

import sys
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from app.config import API_KEY, BASE_URL, DEMO_A_CHROMA, EMBEDDING_MODEL


def _get_store() -> Chroma | None:
    if not DEMO_A_CHROMA.exists() or not any(DEMO_A_CHROMA.iterdir()):
        return None
    return Chroma(
        persist_directory=str(DEMO_A_CHROMA),
        embedding_function=OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=API_KEY,
            base_url=BASE_URL,
            check_embedding_ctx_length=False,
        ),
    )


def rag_search(query: str, k: int = 4) -> str:
    """在企业文档库中检索与 query 相关的片段。"""
    store = _get_store()
    if store is None:
        return "错误：Demo A 向量库为空，请先在 enterprise-doc-research 加载 sample_docs"
    hits = store.similarity_search(query, k=k)
    if not hits:
        return "未找到相关文档片段"
    blocks = []
    for i, doc in enumerate(hits, start=1):
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "0")
        blocks.append(f"[{i}] {source}#{chunk_id}\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks)
