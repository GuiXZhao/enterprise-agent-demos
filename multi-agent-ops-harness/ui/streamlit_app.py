"""Demo B v1.0：Multi-Agent Harness + SSE 时间线。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.config import API_KEY, DEMO_A_CHROMA, USE_MCP_FOR_RESEARCH
from app.supervisor.graph import iter_task_events

st.set_page_config(page_title="Multi-Agent Harness", page_icon="🧭", layout="wide")
st.title("企业运营任务编排 Harness")
st.caption(
    f"Demo B v1.0 · Supervisor · Research({'MCP' if USE_MCP_FOR_RESEARCH else '本地'})"
    " / Analyst / Reporter · SSE"
)

if not API_KEY or API_KEY.startswith("sk-your"):
    st.error("请配置 OPENAI_API_KEY")
    st.stop()

with st.sidebar:
    st.header("依赖")
    if DEMO_A_CHROMA.exists():
        st.success("Demo A 向量库已就绪")
    else:
        st.warning("请先运行: python scripts/load_demo_a_docs.py")
    if st.button("加载 Demo A 文档"):
        import subprocess

        subprocess.run([sys.executable, "scripts/load_demo_a_docs.py"], cwd=str(ROOT))
        st.rerun()

demo_tasks = [
    "采购合同金额 80 万，供应商延迟 20 天，按制度计算违约金并说明是否触顶 5% 上限。",
    "对比 InsightDoc 与 FlowAgent 年费，200 人团队 3 年总成本相差多少？",
    "连续远程办公 10 个工作日，市内交通能否报销？请引用制度依据。",
    "涉及个人信息或跨境传输的采购项目，签约前要完成什么审核？",
    "战略供应商合同 100 万，预付 30%，验收后应付多少？",
    "知识库里有没有年假规定？若没有请明确拒答。",
]

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("示例任务")
    for i, t in enumerate(demo_tasks):
        if st.button(t[:40] + "...", key=f"task_{i}"):
            st.session_state.pending_task = t

with col2:
    st.subheader("Agent 时间线")

task = st.text_area("输入复合任务", height=100, placeholder="需要检索 + 计算 + 汇总的任务...")
if "pending_task" in st.session_state:
    task = st.session_state.pop("pending_task")

if st.button("运行 Harness", type="primary") and task.strip():
    timeline = col2.container()
    answer_box = st.empty()
    answer_parts: list[str] = []
    result = None

    with timeline:
        status = st.status("Supervisor 调度中...", expanded=True)
        for event in iter_task_events(task.strip()):
            if event["type"] == "step":
                agent = event.get("agent", event.get("node", "?"))
                ms = event.get("elapsed_ms", 0)
                total = event.get("total_ms", 0)
                status.write(f"**{agent}** +{ms}ms（累计 {total}ms）")
                status.caption(event.get("detail", "")[:150])
            elif event["type"] == "answer_chunk":
                answer_parts.append(event["content"])
                answer_box.markdown("".join(answer_parts))
            elif event["type"] == "done":
                result = event["result"]
                status.update(
                    label=(
                        f"完成 · Agents: {', '.join(result.get('agents_used', []))}"
                        f" · {event['total_ms']}ms"
                    ),
                    state="complete",
                )

    if result:
        st.markdown("### 最终报告")
        st.markdown(result["final_answer"])
        with st.expander("完整 Trace"):
            st.json(result["trace"])
