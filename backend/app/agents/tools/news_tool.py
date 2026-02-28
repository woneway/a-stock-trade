"""
新闻获取工具
使用东方财富财经新闻接口
"""
from typing import List, Dict, Any
import akshare as ak


class NewsTool:
    """新闻获取工具"""

    def __init__(self, mcp_client=None):
        """初始化工具，mcp_client 参数保留用于兼容"""
        pass

    async def search_news(self, keywords: List[str], date: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        搜索新闻（使用财经网站新闻接口）

        Args:
            keywords: 关键词列表
            date: 日期
            max_results: 最大结果数

        Returns:
            新闻列表
        """
        news_list = []

        try:
            # 尝试获取财经新闻
            df = ak.stock_news_em(symbol="港股")
            if df is not None and not df.empty:
                for _, row in df.head(max_results).iterrows():
                    news_list.append({
                        "title": str(row.get("新闻标题", "")),
                        "url": str(row.get("新闻链接", "")),
                        "time": str(row.get("发布时间", "")),
                        "source": "东方财富"
                    })
        except Exception as e:
            print(f"获取新闻失败: {e}")

        return news_list

    async def get_market_news(self, date: str) -> List[Dict[str, Any]]:
        """获取市场新闻"""
        return await self.search_news(["A股", "收盘", "政策", "行情"], date)

    async def get_sector_news(self, sector: str, date: str) -> List[Dict[str, Any]]:
        """获取板块新闻"""
        return await self.search_news([sector, "板块", "利好", "政策"], date)

    async def get_stock_news(self, stock_name: str, date: str) -> List[Dict[str, Any]]:
        """获取个股新闻"""
        return await self.search_news([stock_name, "股票", "公告", "业绩"], date)

    async def get_policy_news(self, date: str) -> List[Dict[str, Any]]:
        """获取政策新闻"""
        return await self.search_news(["政策", "监管", "证监会", "央行"], date)
