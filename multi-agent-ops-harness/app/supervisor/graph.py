import json
import re
import time
from collections.abc import Iterator
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from app.agents.workers import (
    run_analyst_agent,
    run_reporter_agent,
    run_research_agent,
)
from app.config import MAX_SUPERVISOR_STEPS
from app.db import save_task_run
from app.llm import invoke_llm
from app.state import HarnessState

SUPERVISOR_PROMPT = """你是 Supervisor，负责把用户复合任务派给专业 Agent。
可选 Agent：
- research：查企业文档（制度/产品手册）
- analyst：数值计算、对比、推导（必须基于 research 笔记中的数字）
- reporter：汇总 Markdown 报告（必要时保存笔记）
- FINISH：信息足够，结束

输出 JSON（不要 markdown）：
{
  "next": "research|analyst|reporter|FINISH",
  "instruction": "给该 Agent 的一句话子任务",
  "reason": "一句话理由"
}

规则：
- 涉及计算/金额/天数/成本：先 research 查条款数字，再 analyst 调 calculator
- 需要结构化报告：最后 reporter 汇总
- 至少 2 个不同 Agent 参与后再 FINISH
"""


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def _needs_calculation(task: str) -> bool:
    keys = ("计算", "多少", "相差", "应付", "违约金", "成本", "年", "差", "总", "上限")
    return any(k in task for k in keys)


def _apply_guardrails(state: HarnessState, nxt: str, instruction: str) -> tuple[str, str]:
    used = set(state.get("agents_used") or [])
    has_notes = bool((state.get("research_notes") or "").strip())
    has_report = bool((state.get("draft_report") or "").strip())
    task = state["task"]

    if nxt == "FINISH":
        if len(used) < 1:
            return "research", task
        if _needs_calculation(task) and "analyst" not in used and has_notes:
            return "analyst", "根据检索笔记完成所有数值计算，必须调用 calculator"
        if "reporter" not in used:
            return "reporter", "汇总最终 Markdown 报告"
        if len(used) < 2:
            return "research" if "research" not in used else "reporter", task

    if nxt == "analyst" and not has_notes:
        return "research", task

    return nxt, instruction


def supervisor_node(state: HarnessState) -> dict:
    step = state.get("step_count", 0) + 1
    if step > MAX_SUPERVISOR_STEPS:
        nxt, instruction = _apply_guardrails(state, "FINISH", state["task"])
        if nxt != "FINISH":
            return {
                "next_agent": nxt,
                "current_instruction": instruction,
                "step_count": step,
                "trace": [
                    {
                        "agent": "supervisor",
                        "detail": f"达最大步数，补派 → {nxt}",
                    }
                ],
            }
        return {
            "next_agent": "FINISH",
            "step_count": step,
            "trace": [{"agent": "supervisor", "detail": "达到最大步数，强制结束"}],
        }

    used = state.get("agents_used") or []
    context = (
        f"已用 Agent: {', '.join(used) or '无'}\n"
        f"检索笔记摘要: {(state.get('research_notes') or '')[:500]}\n"
        f"分析结果摘要: {(state.get('analysis_result') or '')[:400]}\n"
        f"已有报告: {(state.get('draft_report') or '')[:200]}"
    )
    response = invoke_llm(
        [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=f"用户任务：{state['task']}\n\n{context}"),
        ]
    )
    try:
        payload = _parse_json(response)
        nxt = payload.get("next", "research")
        instruction = payload.get("instruction", state["task"])
        reason = payload.get("reason", "")
    except (json.JSONDecodeError, TypeError):
        nxt = "research" if not used else "reporter"
        instruction = state["task"]
        reason = "Supervisor 解析失败，使用默认路由"

    if nxt not in {"research", "analyst", "reporter", "FINISH"}:
        nxt = "research"

    nxt, instruction = _apply_guardrails(state, nxt, instruction)

    return {
        "next_agent": nxt,
        "current_instruction": instruction,
        "plan": reason,
        "step_count": step,
        "trace": [
            {
                "agent": "supervisor",
                "detail": f"派发 → {nxt} | {reason} | 指令: {instruction[:100]}",
            }
        ],
    }


def _route(state: HarnessState) -> str:
    nxt = state.get("next_agent", "research")
    if nxt == "FINISH":
        return "finish"
    return nxt


def finish_node(state: HarnessState) -> dict:
    answer = state.get("final_answer") or state.get("draft_report")
    if not answer:
        parts = []
        if state.get("research_notes"):
            parts.append("## 检索摘要\n" + state["research_notes"][:800])
        if state.get("analysis_result"):
            parts.append("## 分析结果\n" + state["analysis_result"])
        answer = "\n\n".join(parts) if parts else "未能生成最终报告。"
    return {"final_answer": answer, "trace": [{"agent": "finish", "detail": "任务结束"}]}


def build_harness_graph():
    graph = StateGraph(HarnessState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research", run_research_agent)
    graph.add_node("analyst", run_analyst_agent)
    graph.add_node("reporter", run_reporter_agent)
    graph.add_node("finish", finish_node)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        _route,
        {
            "research": "research",
            "analyst": "analyst",
            "reporter": "reporter",
            "finish": "finish",
        },
    )
    for worker in ("research", "analyst", "reporter"):
        graph.add_edge(worker, "supervisor")
    graph.add_edge("finish", END)
    return graph.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_harness_graph()
    return _graph


def _initial_state(task: str) -> HarnessState:
    return {
        "task": task,
        "plan": "",
        "current_instruction": "",
        "next_agent": "",
        "research_notes": "",
        "analysis_result": "",
        "draft_report": "",
        "final_answer": "",
        "step_count": 0,
        "agents_used": [],
        "trace": [],
    }


def _build_result(task: str, accumulated: dict[str, Any], total_ms: int) -> dict:
    return {
        "task": task,
        "final_answer": accumulated.get("final_answer", ""),
        "trace": accumulated.get("trace", []),
        "agents_used": list(dict.fromkeys(accumulated.get("agents_used", []))),
        "total_ms": total_ms,
        "research_notes": accumulated.get("research_notes", ""),
        "analysis_result": accumulated.get("analysis_result", ""),
    }


def run_task(task: str) -> dict:
    graph = get_graph()
    t0 = time.perf_counter()
    result = graph.invoke(_initial_state(task))
    total_ms = int((time.perf_counter() - t0) * 1000)
    payload = _build_result(task, result, total_ms)
    save_task_run(
        task,
        status="completed",
        total_ms=total_ms,
        trace=payload["trace"],
        final_answer=payload["final_answer"],
    )
    return payload


def iter_task_events(task: str) -> Iterator[dict[str, Any]]:
    graph = get_graph()
    state = _initial_state(task)
    t0 = time.perf_counter()
    last = t0
    accumulated: dict[str, Any] = {"trace": [], "agents_used": []}

    yield {"type": "start", "task": task}

    for chunk in graph.stream(state, stream_mode="updates"):
        for node_name, update in chunk.items():
            now = time.perf_counter()
            elapsed_ms = int((now - last) * 1000)
            total_ms = int((now - t0) * 1000)
            last = now

            for key in (
                "final_answer",
                "research_notes",
                "analysis_result",
                "draft_report",
                "agents_used",
            ):
                if key in update and update[key]:
                    if key == "agents_used":
                        accumulated["agents_used"].extend(update[key])
                    else:
                        accumulated[key] = update[key]

            for item in update.get("trace", []):
                enriched = {
                    **item,
                    "node": node_name,
                    "elapsed_ms": elapsed_ms,
                    "total_ms": total_ms,
                }
                accumulated["trace"].append(enriched)
                yield {"type": "step", **enriched}

            answer = update.get("final_answer") or update.get("draft_report")
            if answer and node_name in ("reporter", "finish"):
                accumulated["final_answer"] = answer
                for i in range(0, len(answer), 80):
                    yield {"type": "answer_chunk", "content": answer[i : i + 80]}

    total_ms = int((time.perf_counter() - t0) * 1000)
    result = _build_result(task, accumulated, total_ms)
    save_task_run(
        task,
        status="completed",
        total_ms=total_ms,
        trace=result["trace"],
        final_answer=result["final_answer"],
    )
    yield {"type": "done", "result": result, "total_ms": total_ms}


def format_sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
