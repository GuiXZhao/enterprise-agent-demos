"""MCP Server：对外暴露 rag_search 工具（stdio）。

运行：
  python -m app.mcp.research_server
"""

from mcp.server.fastmcp import FastMCP

from app.tools.rag_search import rag_search

mcp = FastMCP("enterprise-research-tools")


@mcp.tool()
def rag_search_tool(query: str, k: int = 4) -> str:
    """在企业文档库检索与 query 相关的制度/产品手册片段。"""
    return rag_search(query, k=k)


if __name__ == "__main__":
    mcp.run(transport="stdio")
