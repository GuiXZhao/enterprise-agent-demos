# Changelog

本仓库两个 Demo 的版本演进与评测基线。GitHub 作品集：[enterprise-agent-demos](https://github.com/GuiXZhao/enterprise-agent-demos)

## Demo A — enterprise-doc-research

| 版本 | 日期 | 变更 | 评测 | 结果文件 |
|------|------|------|------|----------|
| **v0.1** | 2026-09 | 纯向量检索 + LangGraph plan/retrieve/write；初版对比题 recall 低 | 5 题冒烟 | [v0.1_results.txt](enterprise-doc-research/eval/v0.1_results.txt) |
| **v0.2** | 2026-09 | + BM25/向量 Hybrid（RRF）+ gte-rerank-v2；对比题 boost | 30 题 | [v0.2_results.txt](enterprise-doc-research/eval/v0.2_results.txt) |
| **v1.0** | 2026-09 | + reflect 反思循环（最多 2 轮补检索）；60 题 + Faithfulness/Citation/Refusal | 60 题 | [v1.0_results.txt](enterprise-doc-research/eval/v1.0_results.txt) |
| **v1.1** | 2026-09 | Bad Case 归档、引用格式修复、LLM 重试 | — | [BAD_CASES.md](enterprise-doc-research/docs/BAD_CASES.md) |

**v1.0 指标（60 题）**：Recall@5 100% · Faithfulness 76.1% · Citation 100% · Refusal 100%（4/4）

## Demo B — multi-agent-ops-harness

| 版本 | 日期 | 变更 | 评测 | 结果文件 |
|------|------|------|------|----------|
| **v1.0** | 2026-09 | Supervisor + Research/Analyst/Reporter；MCP rag_search；12 题封闭集 | 12 题 | [v1.0_results.txt](multi-agent-ops-harness/eval/v1.0_results.txt) |

**v1.0 指标（12 题）**：Task success 100% · Agent coverage 100% · Keyword hit 92.4% · Latency avg ~76s

> Demo B 开发期问题见 [BAD_CASES.md](multi-agent-ops-harness/docs/BAD_CASES.md)。
