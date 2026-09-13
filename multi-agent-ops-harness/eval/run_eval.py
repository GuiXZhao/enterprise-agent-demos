"""Demo B v1.0 评测：任务成功率 / Multi-Agent / 工具调用 / 延迟。

用法：
  python eval/run_eval.py --quick   # 3 题冒烟
  python eval/run_eval.py           # 12 题全量（约 20 分钟）
  python eval/run_eval.py --save    # 写入 eval/v1.0_results.txt
"""

import argparse
import json
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.supervisor.graph import run_task


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def keyword_hit(answer: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    norm = _normalize(answer)
    hits = 0
    for kw in keywords:
        if kw.lower() in answer.lower() or _normalize(kw) in norm:
            hits += 1
        elif kw.replace(" ", "") in norm:
            hits += 1
    return hits / len(keywords)


def agent_coverage(used: list[str], expected: list[str]) -> float:
    if not expected:
        return 1.0
    hits = sum(1 for a in expected if a in used)
    return hits / len(expected)


def calculator_used(trace: list[dict]) -> bool:
    for step in trace:
        if step.get("agent") == "analyst":
            tools = step.get("tools") or []
            if any(t.get("tool") == "calculator" for t in tools):
                return True
            if "calculator" in (step.get("detail") or ""):
                return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="只跑前 3 题")
    parser.add_argument("--save", action="store_true", help="保存到 eval/v1.0_results.txt")
    args = parser.parse_args()

    items = json.loads((Path(__file__).parent / "tasks.json").read_text(encoding="utf-8"))
    if args.quick:
        items = items[:3]

    lines: list[str] = []
    successes, keywords, coverage, multi = [], [], [], []
    refusals, calc_tasks, calc_ok = [], [], []
    latencies: list[int] = []

    def emit(line: str = ""):
        print(line)
        lines.append(line)

    emit(f"Demo B v1.0 | Supervisor Multi-Agent | {datetime.now():%Y-%m-%d %H:%M}")
    emit(f"Tasks: {len(items)}")

    for item in items:
        result = run_task(item["task"])
        answer = result.get("final_answer", "")
        used = result.get("agents_used", [])
        trace = result.get("trace", [])
        ms = int(result.get("total_ms") or 0)
        latencies.append(ms)

        if item.get("expect_refusal"):
            ok = any(m in answer for m in ("未找到", "没有", "无法", "未提及", "未规定"))
            refusals.append(1.0 if ok else 0.0)
            successes.append(1.0 if ok else 0.0)
            kh = 1.0 if ok else 0.0
        else:
            kh = keyword_hit(answer, item.get("expected_keywords", []))
            keywords.append(kh)
            successes.append(1.0 if kh >= 0.34 else 0.0)

        coverage.append(agent_coverage(used, item.get("expected_agents", [])))
        multi.append(1.0 if len(set(used)) >= 2 else 0.0)

        if item.get("require_calculator"):
            calc_tasks.append(1.0)
            calc_ok.append(1.0 if calculator_used(trace) else 0.0)

        emit(
            f"[{item['id']}] ok={successes[-1]:.0f} kw={kh:.2f} "
            f"agents={used} {ms}ms | {item['task'][:32]}..."
        )

    n = len(items)
    emit("")
    emit("=== Summary (Demo B v1.0) ===")
    emit(f"Task success: {sum(successes)/n:.2%} ({sum(successes):.0f}/{n})")
    if keywords:
        emit(f"Keyword hit (avg): {sum(keywords)/len(keywords):.2%}")
    emit(f"Expected agent coverage: {sum(coverage)/n:.2%}")
    emit(f"Multi-agent (>=2 agents): {sum(multi)/n:.2%}")
    if refusals:
        emit(f"Refusal accuracy: {sum(refusals)/len(refusals):.2%} ({sum(refusals):.0f}/{len(refusals)})")
    if calc_tasks:
        emit(
            f"Calculator usage (calc tasks): {sum(calc_ok)/len(calc_ok):.2%} "
            f"({sum(calc_ok):.0f}/{len(calc_ok)})"
        )
    if latencies:
        lat_sorted = sorted(latencies)
        p50 = lat_sorted[len(lat_sorted) // 2]
        p95_idx = min(len(lat_sorted) - 1, int(len(lat_sorted) * 0.95))
        emit(f"Latency avg: {statistics.mean(latencies):.0f}ms")
        emit(f"Latency P50: {p50}ms")
        emit(f"Latency P95: {lat_sorted[p95_idx]}ms")

    if args.save:
        out = Path(__file__).parent / "v1.0_results.txt"
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        emit(f"\nSaved -> {out}")


if __name__ == "__main__":
    main()
