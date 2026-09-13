from app.tools.calculator import calculator
from app.tools.rag_search import rag_search
from app.tools.save_note import save_task_note

TOOL_REGISTRY = {
    "rag_search": rag_search,
    "calculator": calculator,
    "save_task_note": save_task_note,
}

TOOL_SCHEMAS: dict[str, list[dict]] = {
    "research": [
        {
            "type": "function",
            "function": {
                "name": "rag_search",
                "description": "在企业制度/产品手册向量库中检索相关片段",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "检索关键词"},
                        "k": {"type": "integer", "description": "返回条数，默认4"},
                    },
                    "required": ["query"],
                },
            },
        }
    ],
    "analyst": [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "计算数学表达式，支持 + - * / 和括号",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": '如 "800000*0.0005*20"',
                        }
                    },
                    "required": ["expression"],
                },
            },
        }
    ],
    "reporter": [
        {
            "type": "function",
            "function": {
                "name": "save_task_note",
                "description": "将任务最终结论保存到本地笔记",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["task_id", "content"],
                },
            },
        }
    ],
}


def run_tool(name: str, arguments: dict) -> str:
    if name not in TOOL_REGISTRY:
        return f"错误：未知工具 {name}"
    fn = TOOL_REGISTRY[name]
    args = dict(arguments)
    if name == "rag_search" and "k" not in args:
        args["k"] = 4
    try:
        return fn(**args)
    except TypeError:
        return fn(**{k: v for k, v in args.items() if k in fn.__code__.co_varnames})
