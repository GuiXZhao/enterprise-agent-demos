# Demo B：Multi-Agent 企业任务编排 Harness（v1.0）

Supervisor 将**复合任务**派给 **Research（MCP 检索）/ Analyst（计算）/ Reporter（报告）** 三个子 Agent。

## 技术栈

| 层级 | 技术 |
|------|------|
| 编排 | LangGraph Supervisor + 规则护栏 |
| Multi-Agent | research / analyst / reporter |
| MCP | 自研 Server `rag_search_tool`（stdio） |
| 文档库 | 复用 Demo A Chroma |
| API | FastAPI + **SSE** 流式 trace |
| 日志 | SQLite `data/harness.db` |
| UI | Streamlit **8503** |

## 一键启动

```bash
conda activate agent-dev

# 1. 安装依赖
cd demos/multi-agent-ops-harness
pip install -r requirements.txt

# 2. 加载 Demo A 文档（必须）
python scripts/load_demo_a_docs.py

# 3. UI
streamlit run ui/streamlit_app.py --server.port 8503
```

### API

```bash
uvicorn app.main:app --reload --port 8002
# POST /tasks/run       {"task": "..."}
# POST /tasks/stream    SSE
```

## 示例任务

- 80 万合同延迟 20 天 → 算违约金是否触顶 5%
- InsightDoc vs FlowAgent → 200 人团队 3 年成本差
- 远程办公 10 天 → 市内交通能否报销
- 数据出境合规审核要求

## 评测

```bash
python scripts/smoke_test.py
python eval/run_eval.py --quick   # 3 题，约 5 分钟
python eval/run_eval.py           # 12 题，约 20 分钟
```

**v1.0 baseline（12 题封闭集，`eval/v1.0_results.txt`）：**

| 指标 | 结果 |
|------|------|
| Task success | 100% (12/12) |
| Keyword hit (avg) | 92% |
| Expected agent coverage | 100% |
| Multi-agent (≥2 agents) | 100% |
| Calculator usage | 100% (3/3) |
| Refusal accuracy | 100% (1/1) |
| Latency P50 | ~51s |

## MCP

详见 [docs/MCP.md](docs/MCP.md)。默认本地直连；设 `USE_MCP_FOR_RESEARCH=true` 走 MCP stdio。

## 目录

```
multi-agent-ops-harness/
├── app/supervisor/graph.py   # Supervisor 主图
├── app/agents/workers.py     # 3 子 Agent
├── app/mcp/                  # MCP Server + Client
├── app/tools/                # rag_search, calculator, save_note
├── ui/streamlit_app.py
├── eval/tasks.json           # 12 复合任务
└── docs/INTERVIEW.md
```

## 与 Demo A

| | Demo A | Demo B |
|---|--------|--------|
| 模式 | Deep Research 流水线 | Multi-Agent Harness |
| 任务 | 文档研究问答 | 检索+计算+报告 |
| MCP | 无 | Research 工具 MCP 化 |
