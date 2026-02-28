"""
AKShare 数据获取工具
直接使用 akshare 库
"""
import akshare as ak
import json
from typing import Any, Dict, List, Optional
from datetime import datetime


class AkshareTool:
    """AKShare 数据获取工具"""

    def __init__(self, mcp_client=None):
        """初始化工具，mcp_client 参数保留用于兼容"""
        pass

    async def get_market_emotion(self) -> Optional[Dict[str, Any]]:
        """获取市场情绪"""
        try:
            # 使用东方财富网市场总貌
            df = ak.stock_em_market_activity_netease(symbol="北交所")
            return df.to_dict('records') if df is not None else None
        except Exception as e:
            print(f"获取市场情绪失败: {e}")
            return None

    async def get_zt_pool(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """获取涨停板"""
        try:
            # akshare 需要 YYYYMMDD 格式
            df = ak.stock_zt_pool_em(date=date)
            return df.to_dict('records') if df is not None else None
        except Exception as e:
            print(f"获取涨停板失败: {e}")
            return None

    async def get_dtgc(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """获取跌停板"""
        try:
            df = ak.stock_zt_pool_dtgc_em(date=date)
            return df.to_dict('records') if df is not None else None
        except Exception as e:
            print(f"获取跌停板失败: {e}")
            return None

    async def get_zbgc(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """获取炸板股"""
        try:
            df = ak.stock_zt_pool_zbgc_em(date=date)
            return df.to_dict('records') if df is not None else None
        except Exception as e:
            print(f"获取炸板股失败: {e}")
            return None

    async def get_fund_flow(self) -> Optional[Dict[str, Any]]:
        """获取资金流向"""
        try:
            df = ak.stock_fund_flow_em(symbol="今日", sector_type="今日")
            return df.to_dict('records') if df is not None else None
        except Exception as e:
            print(f"获取资金流向失败: {e}")
            return None

    async def get_lhb_detail(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """获取龙虎榜详情"""
        try:
            df = ak.stock_lhb_detail_em(start_date=date, end_date=date)
            return df.to_dict('records') if df is not None else None
        except Exception as e:
            print(f"获取龙虎榜详情失败: {e}")
            return None

    async def get_margin(self, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取两融数据"""
        try:
            df = ak.margin_sse(start_date=start_date, end_date=end_date)
            return df.to_dict('records') if df is not None else None
        except Exception as e:
            print(f"获取两融数据失败: {e}")
            return None

    async def get_sectors(self, indicator: str = "今日", sector_type: str = "行业资金流") -> Optional[List[Dict[str, Any]]]:
        """获取板块资金流"""
        try:
            df = ak.stock_fund_flow_rank_em(indicator=indicator, sector_type=sector_type)
            return df.to_dict('records') if df is not None else None
        except Exception as e:
            print(f"获取板块资金流失败: {e}")
            return None

    async def get_basic_data(self, date: str) -> Dict[str, Any]:
        """
        获取基础数据（市场情绪、涨停板、炸板、两融）
        用于第一次迭代
        """
        import asyncio
        # 串行获取数据，避免并发过高
        emotion = await self.get_market_emotion()
        zt_pool = await self.get_zt_pool(date)
        zbgc = await self.get_zbgc(date)
        margin = await self.get_margin(date, date)

        return {
            "market_emotion": emotion,
            "zt_pool": zt_pool,
            "zbgc": zbgc,
            "margin": margin
        }

    def _parse_result(self, result: Any) -> Any:
        """解析返回结果"""
        return result


# 工具函数：带重试的数据获取
async def fetch_with_retry(tool_func, *args, max_retries: int = 3, **kwargs):
    """
    带重试的数据获取

    Args:
        tool_func: 异步工具函数
        max_retries: 最大重试次数
        *args, **kwargs: 函数参数

    Returns:
        函数执行结果，失败返回 None
    """
    import asyncio
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            result = await tool_func(*args, **kwargs)
            # 检查结果是否有效
            if result is not None and result != []:
                return result
            retry_count += 1
            last_error = "Empty result"
        except Exception as e:
            retry_count += 1
            last_error = str(e)
            print(f"数据获取失败 (尝试 {retry_count}/{max_retries}): {last_error}")

        if retry_count < max_retries:
            await asyncio.sleep(1)  # 等待 1 秒后重试

    # 超过次数，返回 None，让上层处理
    print(f"数据获取失败，已跳过: {last_error}")
    return None
