# Demo B 面试话术（v1.0）

## 30 秒

> Multi-Agent 企业任务编排 Harness：Supervisor 将复合任务派给 Research（MCP 文档检索）、Analyst（calculator）、Reporter（汇总报告）。支持 SSE 流式 trace、SQLite 任务日志；与 Demo A 共享文档库，形成「Deep Research + 任务 Harness」双项目。

## 架构

```
用户复合任务
    ↓
Supervisor（LangGraph 路由 + 规则护栏）
    ↓ research / analyst / reporter（循环）
Research → MCP Server(rag_search_tool) → Demo A Chroma
Analyst  → Function Calling calculator
Reporter → Markdown 报告 + save_task_note
```

## 和 Demo A 区别

| Demo A | Demo B |
|--------|--------|
| 固定研究流水线 | Supervisor 动态派活 |
| 单链路 Deep Research | 3 子 Agent + Harness |
| 无 MCP | Research 工具 MCP 化 |

## MCP 怎么说

- 自研 MCP Server `enterprise-research-tools`，暴露 `rag_search_tool`
- Client 在 Research Agent；stdio 传输
- 演示默认 `USE_MCP_FOR_RESEARCH=false` 走本地直连；代码与 Server 完整，可切换 true

## 演示顺序（5 分钟）

1. 违约金计算（research → analyst → reporter）
2. 展开 Agent 时间线 + 耗时 ms
3. 三年成本对比（多轮 research）
4. 拒答题（年假）
5. 提 SQLite 日志与 eval 数字
