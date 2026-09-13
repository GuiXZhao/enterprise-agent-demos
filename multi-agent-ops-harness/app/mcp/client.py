"""Research Agent 的 MCP 客户端；失败时回退进程内 rag_search。"""

import os

from app.config import DEMO_ROOT, USE_MCP_FOR_RESEARCH
from app.tools.rag_search import rag_search


def mcp_rag_search(query: str, k: int = 4) -> str:
    if not USE_MCP_FOR_RESEARCH:
        return rag_search(query, k=k)

    try:
        return _call_mcp_stdio(query, k)
    except Exception as exc:
        return rag_search(query, k=k) + f"\n\n[MCP 回退: {exc}]"


def _call_mcp_stdio(query: str, k: int) -> str:
    import asyncio
    import sys

    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    env = os.environ.copy()
    env["PYTHONPATH"] = str(DEMO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    async def _run() -> str:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp.research_server"],
            cwd=str(DEMO_ROOT),
            env=env,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "rag_search_tool", {"query": query, "k": k}
                )
                parts = []
                for block in result.content:
                    if hasattr(block, "text"):
                        parts.append(block.text)
                return "\n".join(parts) or "MCP 返回空结果"

    return asyncio.run(_run())
