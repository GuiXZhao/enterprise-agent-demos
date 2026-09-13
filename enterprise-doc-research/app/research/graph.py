import json
import time
from collections.abc import Iterator
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.config import MAX_RETRIEVAL_ROUNDS
from app.research.nodes import (
    assess_coverage,
    generate_report,
    plan_research,
    retrieve_documents,
)
from app.research.state import ResearchState


def _route_after_reflect(state: ResearchState) -> str:
    if state.get("reflect_sufficient"):
        return "write"
    if state.get("retrieval_round", 0) >= state.get(
        "max_retrieval_rounds", MAX_RETRIEVAL_ROUNDS
    ):
        return "write"
    return "retrieve"


def build_research_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("plan", plan_research)
    graph.add_node("retrieve", retrieve_documents)
    graph.add_node("reflect", assess_coverage)
    graph.add_node("write", generate_report)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "retrieve")
    graph.add_edge("retrieve", "reflect")
    graph.add_conditional_edges(
        "reflect",
        _route_after_reflect,
        {"retrieve": "retrieve", "write": "write"},
    )
    graph.add_edge("write", END)
    return graph.compile()


_graph = None


def get_research_graph():
    global _graph
    if _graph is None:
        _graph = build_research_graph()
    return _graph


def _initial_state(question: str) -> ResearchState:
    return {
        "question": question,
        "plan": "",
        "search_queries": [],
        "retrieved_docs": [],
        "answer": "",
        "citations": [],
        "trace": [],
        "retrieval_round": 0,
        "max_retrieval_rounds": MAX_RETRIEVAL_ROUNDS,
        "reflect_sufficient": False,
    }


def _format_result(question: str, result: dict, *, total_ms: int) -> dict:
    trace = []
    for item in result.get("trace", []):
        enriched = dict(item)
        enriched.setdefault("elapsed_ms", 0)
        enriched.setdefault("total_ms", total_ms)
        trace.append(enriched)
    return {
        "question": question,
        "plan": result.get("plan", ""),
        "search_queries": result.get("search_queries", []),
        "answer": result.get("answer", ""),
        "citations": result.get("citations", []),
        "trace": trace,
        "retrieval_rounds": result.get("retrieval_round", 0),
        "total_ms": total_ms,
    }


def run_research(question: str) -> dict:
    graph = get_research_graph()
    t0 = time.perf_counter()
    result = graph.invoke(_initial_state(question))
    total_ms = int((time.perf_counter() - t0) * 1000)
    return _format_result(question, result, total_ms=total_ms)


def iter_research_events(question: str) -> Iterator[dict[str, Any]]:
    """Yield SSE-friendly events with per-step latency."""
    graph = get_research_graph()
    state = _initial_state(question)
    t0 = time.perf_counter()
    last = t0
    accumulated: dict[str, Any] = {"trace": []}

    yield {"type": "start", "question": question}

    for chunk in graph.stream(state, stream_mode="updates"):
        for node_name, update in chunk.items():
            now = time.perf_counter()
            elapsed_ms = int((now - last) * 1000)
            total_ms = int((now - t0) * 1000)
            last = now

            for key in ("plan", "search_queries", "answer", "citations", "retrieval_round"):
                if key in update and update[key]:
                    accumulated[key] = update[key]

            for trace_item in update.get("trace", []):
                enriched = {
                    **trace_item,
                    "node": node_name,
                    "elapsed_ms": elapsed_ms,
                    "total_ms": total_ms,
                }
                accumulated["trace"].append(enriched)
                yield {"type": "step", **enriched}

            if update.get("answer"):
                answer = update["answer"]
                chunk_size = 80
                for i in range(0, len(answer), chunk_size):
                    yield {
                        "type": "answer_chunk",
                        "content": answer[i : i + chunk_size],
                    }

    total_ms = int((time.perf_counter() - t0) * 1000)
    yield {
        "type": "done",
        "result": _format_result(question, accumulated, total_ms=total_ms),
        "total_ms": total_ms,
    }


def format_sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
