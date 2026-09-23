# Enterprise Agent Demos

企业 Agent 应用作品集：**文档深度研究 Agent** + **Multi-Agent 任务编排 Harness**。

基于 LangGraph、Hybrid RAG、Function Calling、MCP，通义千问（百炼 OpenAI 兼容 API）。

## 项目

| 项目 | 目录 | 说明 | 端口 |
|------|------|------|------|
| **Demo A** | [enterprise-doc-research](enterprise-doc-research/) | 复杂文档 Deep Research，带引用溯源 | UI 8501 · API 8001 |
| **Demo B** | [multi-agent-ops-harness](multi-agent-ops-harness/) | Supervisor 多 Agent 复合任务编排 | UI 8503 · API 8002 |

详细文档见各子目录 README：[Demo A](enterprise-doc-research/README.md) · [Demo B](multi-agent-ops-harness/README.md)

## 快速开始

```bash
git clone https://github.com/GuiXZhao/enterprise-agent-demos.git
cd enterprise-agent-demos
conda activate agent-dev

# 1. 配置 API Key（根目录或子项目 .env 任选其一）
copy .env.example .env        # Windows
# cp .env.example .env        # Linux / macOS

# 2. Demo A
cd enterprise-doc-research
pip install -r requirements.txt
python -c "from app.ingest import load_sample_docs; load_sample_docs()"
streamlit run ui/streamlit_app.py --server.port 8501

# 3. Demo B（另开终端）
cd ../multi-agent-ops-harness
pip install -r requirements.txt
python scripts/load_demo_a_docs.py
streamlit run ui/streamlit_app.py --server.port 8503
```

## 版本演进

| 项目 | 版本线 | 说明 |
|------|--------|------|
| Demo A | v0.1 → v0.2 → v1.0 → v1.1 | 纯向量 → Hybrid+Rerank → reflect 循环 + 60 题三维指标 |
| Demo B | v1.0 | Supervisor 多 Agent 首版即封闭 12 题评测 |

详见 **[CHANGELOG.md](CHANGELOG.md)** · Demo A [Bad Cases](enterprise-doc-research/docs/BAD_CASES.md) · Demo B [Bad Cases](multi-agent-ops-harness/docs/BAD_CASES.md)

**5 分钟录屏脚本**：[docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)

## 评测指标（封闭集，可复现）

| 项目 | 命令 | 关键指标 | 结果文件 |
|------|------|----------|----------|
| Demo A | `python eval/run_eval.py` | Recall@5 100% · Faithfulness 76.1% · Citation 100%（60 题） | [v1.0_results.txt](enterprise-doc-research/eval/v1.0_results.txt) |
| Demo B | `python eval/run_eval.py` | Task success 100% · Agent coverage 100%（12 题） | [v1.0_results.txt](multi-agent-ops-harness/eval/v1.0_results.txt) |

## 隐私与安全

- **请勿**将 `.env` 或 API Key 提交到仓库
- 向量库与 SQLite 为本地运行产物，已在 `.gitignore` 排除
- 示例文档为虚构企业制度/产品手册，仅用于演示

## 技术栈

LangGraph · LangChain · FastAPI · Streamlit · Chroma · MCP · Function Calling · 百炼 API

## 作者

赵贵兴 · [GitHub](https://github.com/GuiXZhao) · AI 应用开发实习求职作品
