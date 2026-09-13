# Demo A 面试话术（v1.0）

## 30 秒电梯演讲

> 我做了一个企业文档 **Deep Research Agent**：用户提复杂问题后，LangGraph 自动 **规划 → Hybrid 检索（BM25+向量 RRF）→ Rerank → 反思是否够 → 不够再搜 → 写带引用的报告**。v1.0 在 60 题 eval 上 Recall@5、Faithfulness、Citation accuracy 均达标，对比题和拒答题有专门策略。

## 架构（1 分钟）

```
用户问题
  → plan（LLM 拆计划 + 检索词）
  → retrieve（Hybrid + Rerank，最多 2 轮）
  → reflect（LLM 判断覆盖是否充分，不够则补充检索词并 loop）
  → write（只基于片段写 Markdown，[来源: 文件#chunk]）
```

**和 Demo2 单轮 RAG 的区别**：多步编排 + 检索反思循环 + 可观测 trace。

**和完整 ReAct Agent 的关系**：reflect 节点负责「要不要继续搜」，属于 **Agentic Workflow**；工具调用是确定性检索节点，不是 Function Calling 自选工具。

## 技术亮点（被追问时用）

| 问题 | 回答要点 |
|------|----------|
| 为什么 Hybrid？ | 企业文档有专有名词（InsightDoc、FlowAgent），纯向量对「产品 A」类表述 recall 低；BM25 补关键词命中 |
| Rerank 作用？ | RRF 融合后候选仍多，百炼 gte-rerank-v2 按语义相关性重排 Top-N |
| 对比题怎么稳？ | 检测「区别/对比/A&B」→ 追加产品定向 query + 按文档来源覆盖 + reflect 检查双来源 |
| 怎么评测？ | 60 题：Recall@5（引用命中）、Faithfulness（结论是否 grounded）、Citation accuracy、拒答准确率 |
| v0.1→v1.0 提升？ | v0.1 纯向量 Recall 80%；v0.2 Hybrid+Rerank 100%；v1.0 加 ReAct reflect 循环 + 60 题三维指标 |

## 指标（填简历）

**v1.0 实测（60 题）**

- Recall@5: **100%**
- Faithfulness: **76.1%**（启发式 grounded 检查）
- Citation accuracy: **100%**
- Task completed: **100%**
- Refusal accuracy: **100%**（4/4）

Baseline：v0.1 Recall@5 80%（5 题）→ v0.2 100%（30 题）→ v1.0 100%（60 题 + 三维指标）。

## 演示顺序（5 分钟）

1. 加载 sample_docs
2. **对比题** Q2：展示双引用 + reflect 可能 2 轮检索
3. **流程题** Q1：4 步报销 + 引用
4. **拒答题** Q28：年假 → 明确拒答
5. 展开「研究过程」：plan / retrieve / **reflect** / write

## 诚实边界

- Faithfulness 当前是启发式（数字/术语 grounded 检查），不是 Ragas 全量 LLM judge
- 未做 Supervisor 并行子 Agent（open_deep_research 完整版），v1.0 用 reflect 循环替代
- 知识库仅 5 份示例文档，生产需扩文档 + 权限 + 增量索引
