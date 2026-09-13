# Demo A：企业文档深度研究 Agent（v1.1）

基于 **LangGraph** 的企业文档 Deep Research：**规划 → Hybrid 检索 → Rerank → 反思循环 → 带引用报告**。

## 技术栈

- LangGraph · LangChain · FastAPI · Streamlit
- 通义千问（百炼）`qwen-plus` + `text-embedding-v3` + `gte-rerank-v2`
- Chroma 向量库 + BM25 关键词检索（RRF 融合）

## 快速开始

```bash
conda activate agent-dev
cd enterprise-doc-research
pip install -r requirements.txt
```

### Streamlit（推荐演示）

```bash
streamlit run ui/streamlit_app.py --server.port 8501
```

侧边栏 **「加载 sample_docs 示例文档」** → 点演示问题或自行输入。

### FastAPI

```bash
uvicorn app.main:app --reload --port 8001
```

- `GET /health`
- `POST /documents/load-samples`
- `POST /research` — body: `{"question": "..."}`
- `POST /research/stream` — SSE 流式 trace + 报告分块

## Agent 流程（v1.0）

```
用户问题 → plan（研究计划 + 检索词）
         → retrieve（BM25 + 向量 RRF → Rerank）
         → reflect（覆盖够吗？不够 → 补充检索，最多 2 轮）
         → write（Markdown 报告 + [来源: 文件#chunk]）
```

## 评测

```bash
python eval/run_eval.py --quick   # 冒烟 5 题
python eval/run_eval.py           # 全量 60 题（约 30–40 分钟）
```

| 指标 | 说明 |
|------|------|
| Recall@5 | 引用是否命中预期文档 |
| Faithfulness | 回答是否 grounded 于检索片段 |
| Citation accuracy | 正文 `[来源:]` 与引用列表是否一致 |
| Refusal accuracy | 拒答题是否正确拒答 |

**版本 baseline**

| 版本 | Recall@5 | 题量 |
|------|----------|------|
| v0.1 | 80% | 5 |
| v0.2 | 100% | 30 |
| v1.0 | Recall 100% / Faithfulness 76% / Cite 100% | 60 |

## 目录结构

```
enterprise-doc-research/
├── app/
│   ├── research/       # LangGraph：plan → retrieve → reflect → write
│   └── retrieval.py    # Hybrid + Rerank
├── ui/                 # Streamlit
├── eval/               # 60 题 + metrics
├── docs/BAD_CASES.md
├── sample_docs/
└── data/chroma/
```

## 环境变量

见 `.env.example`：`USE_HYBRID`、`USE_RERANK`、`MAX_RETRIEVAL_ROUNDS`（默认 2）。
