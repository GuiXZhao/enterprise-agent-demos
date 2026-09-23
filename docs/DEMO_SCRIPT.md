# 5 分钟演示脚本（录屏用）

## 准备工作（镜头外完成）

1. `conda activate agent-dev`
2. Demo A：`cd enterprise-doc-research && pip install -r requirements.txt`，侧边栏加载 sample_docs
3. Demo B：`cd multi-agent-ops-harness && python scripts/load_demo_a_docs.py`
4. 浏览器开两个 Tab：8501（Demo A）、8503（Demo B）

## Demo A（约 2.5 分钟）

| 时间 | 动作 | 话术要点 |
|------|------|----------|
| 0:00 | 展示 UI + 侧边栏文档列表 | 「5 份企业制度/产品手册，模拟真实知识库」 |
| 0:30 | 输入 Q2 对比题 | 「产品 A 与 B 价格场景区别」→ 展开 trace：plan → retrieve → **reflect** → write |
| 1:30 | 指引用 `[来源:]` | 「每条结论可回溯到 chunk」 |
| 2:00 | 输入 Q28 拒答题 | 「员工年假多少天」→ 明确拒答，无编造 |

## Demo B（约 2.5 分钟）

| 时间 | 动作 | 话术要点 |
|------|------|----------|
| 2:30 | 输入违约金任务 | 「80 万合同延迟 20 天算违约金」 |
| 3:00 | 展开 Agent 时间线 | research → **analyst（calculator）** → reporter |
| 3:45 | 三年成本对比任务 | 展示 Multi-Agent 多轮协作 |
| 4:30 | 切 GitHub eval 页 | 指 `v1.0_results.txt`：12/12、92.4% keyword |

## 收尾（30 秒）

- 打开 [CHANGELOG.md](../CHANGELOG.md) 版本表
- 打开 [BAD_CASES.md](../enterprise-doc-research/docs/BAD_CASES.md) 说明迭代思路
