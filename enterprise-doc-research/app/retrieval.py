"""Hybrid retrieval: vector + BM25 (RRF) + DashScope rerank."""

from __future__ import annotations

import re

import httpx
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from app.config import (
    API_KEY,
    HYBRID_POOL_SIZE,
    RERANK_API_URL,
    RERANK_MODEL,
    RERANK_TOP_N,
    RETRIEVAL_K,
    RRF_K,
    USE_HYBRID,
    USE_RERANK,
)
_bm25_retriever: BM25Retriever | None = None
_corpus_size = -1


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", text.lower())


def _content_key(doc: Document) -> str:
    source = doc.metadata.get("source", "")
    chunk_id = doc.metadata.get("chunk_id", "")
    if source and chunk_id:
        return f"{source}#{chunk_id}"
    return doc.page_content[:120]


def invalidate_retrieval_cache() -> None:
    global _bm25_retriever, _corpus_size
    _bm25_retriever = None
    _corpus_size = -1


def _get_vectorstore():
    from app.ingest import get_vectorstore

    return get_vectorstore()


def _load_corpus() -> list[Document]:
    store = _get_vectorstore()
    if store is None:
        return []
    payload = store.get(include=["documents", "metadatas"])
    documents = payload.get("documents") or []
    metadatas = payload.get("metadatas") or []
    return [
        Document(page_content=content, metadata=meta or {})
        for content, meta in zip(documents, metadatas, strict=False)
        if content
    ]


def _get_bm25_retriever() -> BM25Retriever | None:
    global _bm25_retriever, _corpus_size
    docs = _load_corpus()
    if not docs:
        return None
    if _bm25_retriever is None or _corpus_size != len(docs):
        _bm25_retriever = BM25Retriever.from_documents(
            docs, preprocess_func=_tokenize
        )
        _corpus_size = len(docs)
    return _bm25_retriever


def _vector_search(query: str, k: int) -> list[Document]:
    store = _get_vectorstore()
    if store is None:
        return []
    return store.similarity_search(query, k=k)


def _bm25_search(query: str, k: int) -> list[Document]:
    retriever = _get_bm25_retriever()
    if retriever is None:
        return []
    retriever.k = k
    return retriever.invoke(query)


def _rrf_merge(lists: list[list[Document]], *, limit: int) -> list[Document]:
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}
    for result_list in lists:
        for rank, doc in enumerate(result_list):
            key = _content_key(doc)
            doc_map[key] = doc
            scores[key] = scores.get(key, 0.0) + 1.0 / (RRF_K + rank + 1)
    ordered = sorted(scores.keys(), key=lambda item: scores[item], reverse=True)
    return [doc_map[key] for key in ordered[:limit]]


def _rerank(query: str, docs: list[Document], top_n: int) -> list[Document]:
    if not docs or not USE_RERANK or not API_KEY:
        return docs[:top_n]

    payload = {
        "model": RERANK_MODEL,
        "input": {
            "query": query,
            "documents": [doc.page_content for doc in docs],
        },
        "parameters": {
            "top_n": min(top_n, len(docs)),
            "return_documents": False,
        },
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(RERANK_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
        results = body.get("output", {}).get("results") or []
        ranked: list[Document] = []
        for item in results:
            idx = item.get("index")
            if isinstance(idx, int) and 0 <= idx < len(docs):
                ranked.append(docs[idx])
        return ranked[:top_n] if ranked else docs[:top_n]
    except Exception:
        return docs[:top_n]


def _search_one_query(query: str, k: int) -> list[Document]:
    if USE_HYBRID:
        return _rrf_merge(
            [_vector_search(query, k), _bm25_search(query, k)],
            limit=k * 2,
        )
    return _vector_search(query, k)


def ensure_source_coverage(
    ranked: list[Document], pool: list[Document], max_docs: int
) -> list[Document]:
    result = dedupe_docs(ranked)
    present = {doc.metadata.get("source") for doc in result}
    for doc in pool:
        src = doc.metadata.get("source", "unknown")
        if src in present:
            continue
        result.append(doc)
        present.add(src)
    return result[:max_docs]


def merge_with_source_coverage(docs: list[Document]) -> list[Document]:
    by_source: dict[str, list[Document]] = {}
    source_order: list[str] = []
    seen: set[str] = set()
    for doc in docs:
        key = _content_key(doc)
        if key in seen:
            continue
        seen.add(key)
        src = doc.metadata.get("source", "unknown")
        if src not in by_source:
            source_order.append(src)
            by_source[src] = []
        by_source[src].append(doc)

    merged: list[Document] = []
    for src in source_order:
        merged.append(by_source[src][0])
    for src in source_order:
        for doc in by_source[src][1:]:
            if len(merged) >= RERANK_TOP_N:
                break
            if doc not in merged:
                merged.append(doc)
    return merged


def dedupe_docs(docs: list[Document]) -> list[Document]:
    seen: set[str] = set()
    merged: list[Document] = []
    for doc in docs:
        key = _content_key(doc)
        if key in seen:
            continue
        seen.add(key)
        merged.append(doc)
    return merged


def rerank_documents(query: str, docs: list[Document], top_n: int) -> list[Document]:
    return _rerank(query, dedupe_docs(docs), top_n)


def multi_query_retrieve(
    question: str,
    search_queries: list[str],
    *,
    comparison: bool = False,
    boost_queries: list[str] | None = None,
) -> tuple[list[Document], str]:
    if _get_vectorstore() is None:
        return [], "知识库为空，请先上传文档"

    queries = list(search_queries)
    if boost_queries:
        queries.extend(boost_queries)

    pool_lists: list[list[Document]] = []
    for query in queries:
        pool_lists.append(_search_one_query(query, RETRIEVAL_K))

    pool = _rrf_merge(pool_lists, limit=HYBRID_POOL_SIZE)
    ranked = _rerank(question, pool, RERANK_TOP_N)
    if comparison:
        ranked = ensure_source_coverage(
            ranked, pool, max(RERANK_TOP_N, 4)
        )
    else:
        ranked = dedupe_docs(ranked)[:RERANK_TOP_N]

    mode = []
    if USE_HYBRID:
        mode.append("BM25+向量 RRF")
    else:
        mode.append("向量")
    if USE_RERANK:
        mode.append("Rerank")
    suffix = "（对比类：按文档来源覆盖）" if comparison else ""
    detail = (
        f"{' → '.join(mode)} | {len(queries)} 轮检索 | "
        f"候选 {len(pool)} → 输出 {len(ranked)} 片段{suffix}"
    )
    return ranked, detail
