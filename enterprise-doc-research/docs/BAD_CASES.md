# Demo A Bad Cases（v1.1）

| # | 问题 | 现象 | 根因 | 改进 |
|---|------|------|------|------|
| 1 | 产品 A vs B 对比 | 有时只引用 B | 文档写 InsightDoc 而非「产品 A」；纯向量语义 gap | v0.1 加对比 boost + 来源覆盖；v0.2 Hybrid+Rerank |
| 2 | 引用格式重复 | `file.txt#file.txt#0` | chunk_id 与 label 重复拼接 | 规范化 `_citation_label()` |
| 3 | plan 步 SSL 断连 | 整页报错 | 百炼 API 网络抖动 | `invoke_llm` 重试 3 次 |

Faithfulness 76%：启发式指标（数字/词是否出现在引用片段），非 Ragas LLM judge。
