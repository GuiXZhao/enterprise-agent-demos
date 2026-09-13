"""离线评测脚本（v1.0）：Recall + Faithfulness + Citation accuracy。

用法（在 demos/enterprise-doc-research 目录）：
  python eval/run_eval.py           # 全量 60 题
  python eval/run_eval.py --quick   # 仅前 5 题（冒烟）
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import MAX_RETRIEVAL_ROUNDS, USE_HYBRID, USE_RERANK
from app.ingest import get_vectorstore, load_sample_docs
from app.research import run_research
sys.path.insert(0, str(Path(__file__).parent))
from metrics import (
    citation_accuracy,
    faithfulness_score,
    is_refusal,
    recall_from_citations,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="只跑前 5 题")
    args = parser.parse_args()

    store = get_vectorstore()
    if store is None:
        print("向量库为空，正在加载 sample_docs ...")
        load_sample_docs()
        store = get_vectorstore()
    else:
        print("使用已有向量库 data/chroma（不会重复入库）")
    if store is None:
        print("请先确保 sample_docs 已入库")
        sys.exit(1)

    mode = []
    if USE_HYBRID:
        mode.append("hybrid")
    if USE_RERANK:
        mode.append("rerank")
    print(
        f"Demo A v1.0 | 检索: {' + '.join(mode) or 'vector'} | "
        f"ReAct 最大 {MAX_RETRIEVAL_ROUNDS} 轮"
    )

    questions_path = Path(__file__).parent / "questions.json"
    items = json.loads(questions_path.read_text(encoding="utf-8"))
    if args.quick:
        items = items[:5]
        print(f"Quick mode: {len(items)} questions")

    recalls, faithfulness, cite_acc, refusals = [], [], [], []
    completed = 0

    for item in items:
        q = item["question"]
        result = run_research(q)
        answer = result.get("answer", "")
        cites = result.get("citations", [])
        cite_sources = {c.split("#", 1)[0] for c in cites if "#" in c}
        doc_texts = []
        for step in result.get("trace", []):
            if step.get("step") == "retrieve":
                pass
        # Re-run not needed: use answer + citations; faithfulness from answer numbers/terms
        # Load doc texts from store by citation labels is heavy; use heuristic on answer only
        # For better faithfulness, fetch cited chunks from chroma
        doc_texts = _fetch_cited_texts(store, cites)

        if item.get("expect_refusal"):
            ok = is_refusal(answer, cite_sources)
            refusals.append(ok)
            recalls.append(1.0 if ok else 0.0)
        else:
            recalls.append(
                recall_from_citations(
                    item.get("expected_sources", []),
                    cite_sources,
                    require_all=item.get("require_all_sources", False),
                )
            )

        faithfulness.append(faithfulness_score(answer, doc_texts))
        cite_acc.append(citation_accuracy(answer, cites))
        if answer:
            completed += 1

        print(
            f"[{item['id']}] recall={recalls[-1]:.0f} "
            f"faith={faithfulness[-1]:.2f} cite={cite_acc[-1]:.2f} | {q[:24]}..."
        )

    n = len(items)
    print("\n=== Summary (v1.0) ===")
    print(f"Recall@5: {sum(recalls)/n:.2%} ({sum(recalls):.0f}/{n})")
    print(f"Faithfulness: {sum(faithfulness)/n:.2%}")
    print(f"Citation accuracy: {sum(cite_acc)/n:.2%}")
    print(f"Task completed: {completed/n:.2%} ({completed}/{n})")
    if refusals:
        print(f"Refusal accuracy: {sum(refusals)/len(refusals):.2%} ({sum(refusals)}/{len(refusals)})")


def _fetch_cited_texts(store, citations: list[str]) -> list[str]:
    if not citations:
        return []
    payload = store.get(include=["documents", "metadatas"])
    docs = payload.get("documents") or []
    metas = payload.get("metadatas") or []
    texts = []
    for cite in citations:
        source, _, chunk = cite.partition("#")
        for content, meta in zip(docs, metas, strict=False):
            if meta and meta.get("source") == source:
                if not chunk or meta.get("chunk_id") == chunk:
                    texts.append(content)
                    break
    return texts


if __name__ == "__main__":
    main()
