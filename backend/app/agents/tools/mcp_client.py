"""
MCP 客户端封装
支持 AKShare 和 MiniMax 两个 MCP 服务
"""
import os
import json
import asyncio
from typing import Any, Dict, List, Optional
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters


class MCPClient:
    """MCP 客户端"""

    def __init__(self):
        # AKShare MCP 配置
        self.akshare_server = StdioServerParameters(
            command="/Users/lianwu/ai/projects/a-stock-trade/backend/.venv/bin/python3",
            args=["/Users/lianwu/ai/mcp/mcp_akshare/run.py"]
        )

        # MiniMax MCP 配置
        self.minimax_server = StdioServerParameters(
            command="uvx",
            args=["minimax-coding-plan-mcp", "-y"],
            env={
                "MINIMAX_API_HOST": os.getenv("MINIMAX_API_HOST", "https://api.minimaxi.com"),
                "MINIMAX_API_KEY": os.getenv("MINIMAX_API_KEY", "")
            }
        )

    async def call_akshare(self, function: str, params: Dict = None) -> Any:
        """
        调用 AKShare MCP

        Args:
            function: 函数名
            params: 参数字典

        Returns:
            函数执行结果
        """
        params = params or {}
        try:
            async with stdio_client(self.akshare_server) as (read, write):
                # 创建会话
                from mcp import ClientSession
                session = ClientSession(read, write)
                await session.initialize()
                try:
                    result = await session.call_tool("ak_call", {
                        "function": function,
                        "params": json.dumps(params)
                    })
                    # 解析结果
                    if result and hasattr(result, 'content'):
                        for item in result.content:
                            if hasattr(item, 'text'):
                                return json.loads(item.text)
                    return None
                finally:
                    await session.close()
        except Exception as e:
            print(f"AKShare MCP 调用失败: {e}")
            return None

    async def search_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        调用 MiniMax MCP 搜索新闻

        Args:
            query: 搜索关键词
            max_results: 最大结果数

        Returns:
            搜索结果列表
        """
        try:
            async with stdio_client(self.minimax_server) as (read, write):
                async with self._create_session(read, write) as session:
                    result = await session.call_tool("web_search", {
                        "query": query,
                        "max_results": max_results
                    })
                    # 解析结果
                    if result and hasattr(result, 'content'):
                        for item in result.content:
                            if hasattr(item, 'text'):
                                return json.loads(item.text)
                    return []
        except Exception as e:
            print(f"MiniMax MCP 调用失败: {e}")
            return []

    async def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        调用 LLM 生成文本

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词

        Returns:
            LLM 生成的回答
        """
        # TODO: 实现 LLM 调用
        return ""


# 全局 MCP 客户端实例
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """获取 MCP 客户端单例"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
