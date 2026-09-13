"""生成 60 题评测集（基于 sample_docs 内容）。"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "eval" / "questions.json"

QUESTIONS = [
    {"id": "q01", "category": "流程", "question": "报销流程分几步？每步需要什么材料？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q02", "category": "对比", "question": "产品 A 与产品 B 在价格和适用场景上有何区别？", "expected_sources": ["product_manual_a.txt", "product_manual_b.txt"], "require_all_sources": True},
    {"id": "q03", "category": "条款", "question": "采购合同里关于付款周期和违约金如何规定？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q04", "category": "摘要", "question": "用 3 条 bullet 总结员工远程办公制度要点。", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q05", "category": "合规", "question": "知识库里有没有关于数据出境的规定？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q06", "category": "流程", "question": "报销需要在费用发生后多少天内提交？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q07", "category": "流程", "question": "差旅类报销需要什么额外材料？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q08", "category": "流程", "question": "采购类对公报销需要什么材料？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q09", "category": "流程", "question": "财务部复核报销单主要校验什么？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q10", "category": "流程", "question": "出纳付款要在复核通过后几个工作日内完成？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q11", "category": "条款", "question": "采购金额 5 万元以下由谁审批？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q12", "category": "条款", "question": "采购金额 50 万元以上需要什么审批？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q13", "category": "条款", "question": "战略供应商的付款比例如何约定？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q14", "category": "条款", "question": "供应商延迟交付超过多少天可以收取违约金？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q15", "category": "条款", "question": "采购合同违约金的上限是多少？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q16", "category": "制度", "question": "连续远程办公超过几个工作日需要提前申请？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q17", "category": "制度", "question": "跨城市远程办公超过 5 日需要什么手续？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q18", "category": "制度", "question": "远程办公期间市内交通费能否报销？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q19", "category": "制度", "question": "远程办公有哪些信息安全要求？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q20", "category": "制度", "question": "直属主管审批远程办公申请的时限是多久？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q21", "category": "产品", "question": "InsightDoc 标准版价格是多少？", "expected_sources": ["product_manual_a.txt"]},
    {"id": "q22", "category": "产品", "question": "InsightDoc 适合多少人以下的团队？", "expected_sources": ["product_manual_a.txt"]},
    {"id": "q23", "category": "产品", "question": "InsightDoc 有哪些核心功能？", "expected_sources": ["product_manual_a.txt"]},
    {"id": "q24", "category": "产品", "question": "FlowAgent 企业版起步价格是多少？", "expected_sources": ["product_manual_b.txt"]},
    {"id": "q25", "category": "产品", "question": "FlowAgent 适合什么规模的企业？", "expected_sources": ["product_manual_b.txt"]},
    {"id": "q26", "category": "产品", "question": "FlowAgent 是否支持 MCP 接入？", "expected_sources": ["product_manual_b.txt"]},
    {"id": "q27", "category": "对比", "question": "InsightDoc 和 FlowAgent 分别不适合什么场景？", "expected_sources": ["product_manual_a.txt", "product_manual_b.txt"], "require_all_sources": True},
    {"id": "q28", "category": "拒答", "question": "员工年假天数是多少？", "expected_sources": [], "expect_refusal": True},
    {"id": "q29", "category": "拒答", "question": "公司股票期权政策是什么？", "expected_sources": [], "expect_refusal": True},
    {"id": "q30", "category": "合规", "question": "涉及个人信息或跨境传输的采购项目需要提交什么表单？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q31", "category": "流程", "question": "报销第一步要在哪个系统操作？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q32", "category": "流程", "question": "直属主管审批报销时确认什么？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q33", "category": "流程", "question": "逾期报销需要什么额外材料？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q34", "category": "流程", "question": "增值税发票在报销材料里属于哪一类？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q35", "category": "条款", "question": "5 万到 50 万的采购需要哪些人审批？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q36", "category": "条款", "question": "标准付款周期从什么时候开始计算？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q37", "category": "条款", "question": "战略供应商预付比例是多少？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q38", "category": "条款", "question": "违约金按合同金额每天收取多少比例？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q39", "category": "条款", "question": "数据出境合规评估表由哪个部门审核？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q40", "category": "制度", "question": "远程办公申请要在 OA 填写哪些信息？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q41", "category": "制度", "question": "远程办公期间考勤如何计算？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q42", "category": "制度", "question": "跨城差旅在远程办公时按什么制度执行？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q43", "category": "制度", "question": "远程办公能否使用个人网盘存公司文档？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q44", "category": "制度", "question": "远程访问公司系统需要用什么通道？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q45", "category": "产品", "question": "InsightDoc 标准版包含多少存储空间？", "expected_sources": ["product_manual_a.txt"]},
    {"id": "q46", "category": "产品", "question": "InsightDoc 是否支持混合检索？", "expected_sources": ["product_manual_a.txt"]},
    {"id": "q47", "category": "产品", "question": "InsightDoc 的定位是什么？", "expected_sources": ["product_manual_a.txt"]},
    {"id": "q48", "category": "产品", "question": "FlowAgent 是否提供 LangGraph 可视化编排？", "expected_sources": ["product_manual_b.txt"]},
    {"id": "q49", "category": "产品", "question": "FlowAgent 如何计费？", "expected_sources": ["product_manual_b.txt"]},
    {"id": "q50", "category": "产品", "question": "FlowAgent 的多 Agent 能力有哪些？", "expected_sources": ["product_manual_b.txt"]},
    {"id": "q51", "category": "对比", "question": "产品 A 和产品 B 的目标客户规模有何不同？", "expected_sources": ["product_manual_a.txt", "product_manual_b.txt"], "require_all_sources": True},
    {"id": "q52", "category": "对比", "question": "InsightDoc 与 FlowAgent 的年费差距大概是多少？", "expected_sources": ["product_manual_a.txt", "product_manual_b.txt"], "require_all_sources": True},
    {"id": "q53", "category": "拒答", "question": "公司食堂开放时间是几点？", "expected_sources": [], "expect_refusal": True},
    {"id": "q54", "category": "拒答", "question": "2026 年全员涨薪比例是多少？", "expected_sources": [], "expect_refusal": True},
    {"id": "q55", "category": "合规", "question": "采购项目涉及跨境传输时签约前要完成什么审核？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q56", "category": "流程", "question": "报销流程中财务部和出纳的分工是什么？", "expected_sources": ["expense_policy.txt"]},
    {"id": "q57", "category": "条款", "question": "采购申请单需要注明哪些信息？", "expected_sources": ["procurement_policy.txt"]},
    {"id": "q58", "category": "制度", "question": "远程办公制度适用于哪种办公方式？", "expected_sources": ["remote_work_policy.txt"]},
    {"id": "q59", "category": "产品", "question": "FlowAgent 为什么不建议小团队使用？", "expected_sources": ["product_manual_b.txt"]},
    {"id": "q60", "category": "产品", "question": "InsightDoc 的 API 调用额度是多少？", "expected_sources": ["product_manual_a.txt"]},
]

if __name__ == "__main__":
    OUT.write_text(json.dumps(QUESTIONS, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(QUESTIONS)} questions to {OUT}")
