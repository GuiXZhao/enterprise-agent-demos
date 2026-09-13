# Demo B MCP 说明

## 是什么

自研 **MCP Server**，不是接 GitHub/Slack 等第三方 MCP。

| 组件 | 文件 | 作用 |
|------|------|------|
| Server | `app/mcp/research_server.py` | 暴露 `rag_search_tool` |
| Client | `app/mcp/client.py` | Research Agent 调用 |
| 工具实现 | `app/tools/rag_search.py` | 读 Demo A 的 Chroma |

## 独立运行 Server

```bash
cd demos/multi-agent-ops-harness
pip install "mcp>=1.6.0,<2.0.0"
python -m app.mcp.research_server
```

## 在 Harness 里启用 MCP

`.env`：

```
USE_MCP_FOR_RESEARCH=true
```

默认 `false`：进程内 `rag_search()`，演示更稳定；面试展示 Server 代码即可。

## 调用链

```
Research Agent → mcp_rag_search()
              → MCP Client (stdio 子进程)
              → MCP Server @mcp.tool rag_search_tool
              → Chroma (../enterprise-doc-research/data/chroma)
```
