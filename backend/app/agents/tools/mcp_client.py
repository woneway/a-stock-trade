"""
MCP 客户端封装
使用线程池运行同步 MCP 调用，避免阻塞事件循环
"""
import json
import asyncio
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 全局线程池
_executor = ThreadPoolExecutor(max_workers=4)

# 配置文件路径
MCP_CONFIG_PATH = Path(__file__).parent.parent.parent / ".mcp.json"


def load_mcp_config() -> Dict:
    """从配置文件加载 MCP 配置"""
    if MCP_CONFIG_PATH.exists():
        try:
            with open(MCP_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("mcp_servers", {})
        except Exception as e:
            print(f"加载 MCP 配置失败: {e}")
    return {}


class MCPClient:
    """MCP 客户端 - 使用线程池避免阻塞"""

    def __init__(self):
        # 加载配置
        mcp_config = load_mcp_config()

        # AKShare MCP 配置
        akshare_cfg = mcp_config.get("akshare", {})
        self.akshare_server = StdioServerParameters(
            command=akshare_cfg.get("command", "/Users/lianwu/ai/projects/a-stock-trade/backend/.venv/bin/python3"),
            args=akshare_cfg.get("args", ["/Users/lianwu/ai/mcp/mcp_akshare/run.py"])
        )

        # MiniMax MCP 配置
        minimax_cfg = mcp_config.get("minimax", {})
        self.minimax_server = StdioServerParameters(
            command=minimax_cfg.get("command", "uvx"),
            args=minimax_cfg.get("args", ["minimax-coding-plan-mcp", "-y"]),
            env=minimax_cfg.get("env", {})
        )

        # 并发限制
        self._semaphore = asyncio.Semaphore(2)
        self._minimax_semaphore = asyncio.Semaphore(1)

    def _call_akshare_sync(self, function: str, params: Dict) -> Any:
        """同步调用 AKShare（在线程池中运行）"""
        try:
            result_holder = [None]
            error_holder = [None]

            def run():
                try:
                    import asyncio
                    from mcp import ClientSession, StdioServerParameters
                    from mcp.client.stdio import stdio_client

                    # 创建新的事件循环
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    async def call_mcp():
                        async with stdio_client(self.akshare_server) as (read, write):
                            async with ClientSession(read, write) as session:
                                # 初始化
                                await session.initialize()

                                # 调用工具
                                result = await session.call_tool(
                                    "ak_call",
                                    {
                                        "function": function,
                                        "params": json.dumps(params)
                                    }
                                )
                                return result

                    # 运行
                    result = loop.run_until_complete(call_mcp())

                    # 解析结果
                    if result and hasattr(result, 'content'):
                        for item in result.content:
                            if hasattr(item, 'text') and item.text:
                                try:
                                    result_holder[0] = json.loads(item.text)
                                except:
                                    result_holder[0] = item.text

                    loop.close()

                except Exception as e:
                    error_holder[0] = e
                    import traceback
                    traceback.print_exc()

            thread = threading.Thread(target=run)
            thread.start()
            thread.join(timeout=30)

            if error_holder[0]:
                print(f"AKShare MCP 错误: {error_holder[0]}")
                return None

            return result_holder[0]

        except Exception as e:
            print(f"AKShare MCP 调用失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def call_akshare(self, function: str, params: Dict = None) -> Any:
        """
        调用 AKShare MCP（在线程池中运行）

        Args:
            function: 函数名
            params: 参数字典

        Returns:
            函数执行结果
        """
        params = params or {}

        async with self._semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                _executor,
                self._call_akshare_sync,
                function,
                params
            )

    def _search_minimax_sync(self, query: str, max_results: int) -> List[Dict]:
        """同步调用 MiniMax 搜索（在线程池中运行）"""
        try:
            result_holder = [None]
            error_holder = [None]

            def run():
                try:
                    import asyncio
                    from mcp import ClientSession, StdioServerParameters
                    from mcp.client.stdio import stdio_client

                    # 创建新的事件循环
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    async def call_mcp():
                        async with stdio_client(self.minimax_server) as (read, write):
                            async with ClientSession(read, write) as session:
                                await session.initialize()
                                result = await session.call_tool(
                                    "web_search",
                                    {"query": query, "num_results": max_results}
                                )
                                return result

                    result = loop.run_until_complete(call_mcp())

                    # 解析结果
                    if result and hasattr(result, 'content'):
                        for item in result.content:
                            if hasattr(item, 'text') and item.text:
                                try:
                                    # 尝试解析 JSON
                                    result_holder[0] = json.loads(item.text)
                                except:
                                    result_holder[0] = [{"text": item.text}]

                    loop.close()

                except Exception as e:
                    error_holder[0] = e
                    import traceback
                    traceback.print_exc()

            thread = threading.Thread(target=run)
            thread.start()
            thread.join(timeout=60)

            if error_holder[0]:
                print(f"MiniMax MCP 错误: {error_holder[0]}")
                return []

            return result_holder[0] or []

        except Exception as e:
            print(f"MiniMax MCP 调用失败: {e}")
            return []

    async def search_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """搜索新闻（使用 MiniMax MCP）"""
        async with self._minimax_semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                _executor,
                self._search_minimax_sync,
                query,
                max_results
            )

    async def call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM"""
        return ""


# 全局 MCP 客户端实例
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """获取 MCP 客户端单例"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client


# 工具函数：带重试的数据获取
async def fetch_with_retry(tool_func, *args, max_retries: int = 3, **kwargs):
    """带重试的数据获取"""
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            result = await tool_func(*args, **kwargs)
            if result is not None and result != [] and result != {}:
                return result
            retry_count += 1
            last_error = "Empty result"
        except Exception as e:
            retry_count += 1
            last_error = str(e)
            print(f"数据获取失败 (尝试 {retry_count}/{max_retries}): {last_error}")

        if retry_count < max_retries:
            await asyncio.sleep(1)

    print(f"数据获取失败，已跳过: {last_error}")
    return None
