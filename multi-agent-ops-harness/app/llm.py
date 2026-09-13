import json
import time
from functools import lru_cache

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import OpenAIConnectionError
from openai import OpenAI

from app.config import API_KEY, BASE_URL, CHAT_MODEL


@lru_cache
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=CHAT_MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=0.2,
    )


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def invoke_llm(messages: list[BaseMessage], *, max_retries: int = 3) -> str:
    llm = get_llm()
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages).content
        except OpenAIConnectionError as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    if last_error:
        raise last_error
    raise RuntimeError("LLM invoke failed")


def invoke_with_tools(
    messages: list[dict],
    tools: list[dict],
    *,
    max_rounds: int = 3,
) -> tuple[str, list[dict]]:
    client = get_openai_client()
    trace: list[dict] = []
    current = list(messages)

    for _ in range(max_rounds):
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=current,
            tools=tools,
        )
        msg = response.choices[0].message
        if not msg.tool_calls:
            return msg.content or "", trace

        current.append(msg.model_dump())
        for call in msg.tool_calls:
            from app.tools.registry import run_tool

            args = json.loads(call.function.arguments or "{}")
            result = run_tool(call.function.name, args)
            trace.append(
                {
                    "tool": call.function.name,
                    "arguments": args,
                    "result": result[:500],
                }
            )
            current.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )

    return "工具调用超过最大轮次", trace
