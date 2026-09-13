def calculator(expression: str) -> str:
    """安全计算数学表达式。"""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "错误：仅支持数字和 +-*/()"
    try:
        return str(eval(expression))  # noqa: S307
    except Exception as exc:
        return f"计算错误：{exc}"
