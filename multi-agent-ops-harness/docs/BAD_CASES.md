# Demo B Bad Cases（v1.0 开发记录）

| # | 任务类型 | 现象 | 根因 | 改进 |
|---|----------|------|------|------|
| 1 | 违约金计算 | Analyst 未调用 calculator | Supervisor 路由后 Analyst prompt 未强调「必须算」 | 任务集加入 calc 关键词校验；Analyst 工具调用护栏 |
| 2 | SaaS 成本对比 | 缺少 FlowAgent 起步价 | 单次检索未覆盖 product_manual_b 定价段 | Research 多轮检索 + Reporter 汇总前检查关键词 |
| 3 | 拒答题（年假） | 偶发编造制度 | Reporter 未继承 Research 拒答信号 | t10 期望 agents 含 analyst；拒答关键词校验 |
| 4 | 长任务超时 | P95 延迟 >180s | 多轮 LLM + 检索串行 | 接受 demo 级延迟；生产需并行与缓存 |

**v1.0 评测**：上述问题在 12 题封闭集上已收敛至 Task success 100%（见 `eval/v1.0_results.txt`）。

**说明**：Demo B 无独立 v0.x 评测文件；迭代发生在 v1.0 开发周期内，通过 `eval/tasks.json` 与通过规则驱动修复。
