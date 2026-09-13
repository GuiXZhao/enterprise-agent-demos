"""v1.0 评测指标：Recall、Faithfulness、Citation accuracy。"""

from __future__ import annotations

import re

REFUSAL_MARKERS = ("未找到", "没有足够", "无法", "知识库中未")


def recall_from_citations(
    expected_sources: list[str],
    cite_sources: set[str],
    *,
    require_all: bool = False,
) -> float:
    if not expected_sources:
        return 1.0
    if require_all:
        hits = sum(1 for src in expected_sources if src in cite_sources)
        return hits / len(expected_sources)
    return 1.0 if any(src in cite_sources for src in expected_sources) else 0.0


def is_refusal(answer: str, cite_sources: set[str]) -> bool:
    return any(m in answer for m in REFUSAL_MARKERS) or not cite_sources


def citation_accuracy(answer: str, citations: list[str]) -> float:
    """Answer inline [来源: xxx] must match retrieved citation list."""
    inline = set(re.findall(r"\[来源:\s*([^\]]+)\]", answer))
    valid = set(citations)
    if not inline:
        return 1.0 if valid else 1.0
    if not valid:
        return 0.0
    matched = sum(
        1
        for cite in inline
        if cite in valid or any(cite in v or v in cite for v in valid)
    )
    return matched / len(inline)


def faithfulness_score(answer: str, doc_texts: list[str]) -> float:
    """Heuristic: numeric claims and key terms should appear in retrieved context."""
    if any(m in answer for m in REFUSAL_MARKERS):
        return 1.0

    corpus = "\n".join(doc_texts)
    if not corpus.strip():
        return 0.0

    numbers = re.findall(r"\d+(?:\.\d+)?", answer)
    if numbers:
        num_hits = sum(1 for n in numbers if n in corpus)
        num_score = num_hits / len(numbers)
    else:
        num_score = 1.0

    terms = re.findall(r"[\u4e00-\u9fff]{2,6}", answer)
    if not terms:
        return num_score
    term_hits = sum(1 for t in terms if t in corpus)
    term_score = term_hits / len(terms)
    return 0.6 * num_score + 0.4 * term_score
