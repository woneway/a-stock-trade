from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import date, datetime
import httpx
import json
import re


class BaseDataProvider(ABC):
    """数据提供者基类"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @abstractmethod
    async def get_stock_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票实时价格"""
        pass

    @abstractmethod
    async def get_market_index(self, index_code: str = "000001") -> Optional[Dict[str, Any]]:
        """获取大盘指数"""
        pass


class EastMoneyProvider(BaseDataProvider):
    """东方财富数据提供者"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://push2.eastmoney.com"

    def _format_stock_code(self, code: str) -> str:
        """格式化股票代码"""
        code = code.strip()
        if code.startswith("6"):
            return f"1.{code}"
        elif code.startswith(("0", "3")):
            return f"0.{code}"
        return code

    async def get_stock_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票实时价格"""
        formatted_code = self._format_stock_code(stock_code)
        url = f"{self.base_url}/api/qt/stock/get"
        params = {
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "invt": "2",
            "fltt": "2",
            "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f57,f58,f59,f60,f116,f117,f162,f167,f168,f169,f170,f171,f173,f177",
            "secid": formatted_code,
            "_": datetime.now().timestamp(),
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
                if data.get("data"):
                    stock_data = data["data"]
                    return {
                        "code": stock_code,
                        "name": stock_data.get("f58"),
                        "price": stock_data.get("f43", 0),
                        "change": stock_data.get("f170", 0) / 100 if stock_data.get("f170") else 0,
                        "change_pct": stock_data.get("f171", 0) / 100 if stock_data.get("f171") else 0,
                        "open": stock_data.get("f46", 0),
                        "high": stock_data.get("f44", 0),
                        "low": stock_data.get("f45", 0),
                        "volume": stock_data.get("f47"),
                        "amount": stock_data.get("f48"),
                        "timestamp": datetime.now().isoformat(),
                    }
            except Exception as e:
                print(f"获取股票价格失败: {e}")
        return None

    async def get_market_index(self, index_code: str = "000001") -> Optional[Dict[str, Any]]:
        """获取大盘指数"""
        index_map = {
            "000001": ("1.000001", "上证指数"),
            "399001": ("0.399001", "深证成指"),
            "399006": ("0.399006", "创业板指"),
            "000300": ("1.000300", "沪深300"),
        }
        secid, name = index_map.get(index_code, ("1.000001", "上证指数"))
        url = f"{self.base_url}/api/qt/stock/get"
        params = {
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "invt": "2",
            "fltt": "2",
            "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f57,f58,f59,f60,f116,f117,f162",
            "secid": secid,
            "_": datetime.now().timestamp(),
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
                if data.get("data"):
                    stock_data = data["data"]
                    return {
                        "code": index_code,
                        "name": name,
                        "points": stock_data.get("f43", 0),
                        "change": stock_data.get("f170", 0) / 100 if stock_data.get("f170") else 0,
                        "change_pct": stock_data.get("f171", 0) / 100 if stock_data.get("f171") else 0,
                        "timestamp": datetime.now().isoformat(),
                    }
            except Exception as e:
                print(f"获取大盘指数失败: {e}")
        return None


class SinaProvider(BaseDataProvider):
    """新浪财经数据提供者"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)

    async def get_stock_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票实时价格"""
        code = stock_code.strip()
        if code.startswith("6"):
            full_code = f"sh{code}"
        else:
            full_code = f"sz{code}"
        url = f"https://hq.sinajs.cn/list={full_code}"
        async with httpx.AsyncClient(headers={"Referer": "https://finance.sina.com.cn"}) as client:
            try:
                response = await client.get(url, timeout=10.0)
                text = response.text
                match = re.search(r'="(.+)"', text)
                if match:
                    parts = match.group(1).split(",")
                    if len(parts) >= 32:
                        return {
                            "code": stock_code,
                            "name": parts[0],
                            "price": float(parts[1]) if parts[1] else 0,
                            "open": float(parts[2]) if parts[2] else 0,
                            "high": float(parts[3]) if parts[3] else 0,
                            "low": float(parts[4]) if parts[4] else 0,
                            "volume": int(parts[5]) if parts[5] else 0,
                            "timestamp": datetime.now().isoformat(),
                        }
            except Exception as e:
                print(f"获取股票价格失败: {e}")
        return None

    async def get_market_index(self, index_code: str = "000001") -> Optional[Dict[str, Any]]:
        """获取大盘指数"""
        index_map = {
            "000001": "sh000001",
            "399001": "sz399001",
            "399006": "sz399006",
        }
        full_code = index_map.get(index_code, "sh000001")
        url = f"https://hq.sinajs.cn/list={full_code}"
        async with httpx.AsyncClient(headers={"Referer": "https://finance.sina.com.cn"}) as client:
            try:
                response = await client.get(url, timeout=10.0)
                text = response.text
                match = re.search(r'="(.+)"', text)
                if match:
                    parts = match.group(1).split(",")
                    if len(parts) >= 6:
                        return {
                            "code": index_code,
                            "name": parts[0],
                            "points": float(parts[1]) if parts[1] else 0,
                            "change": float(parts[2]) if parts[2] else 0,
                            "change_pct": float(parts[3]) if parts[3] else 0,
                            "timestamp": datetime.now().isoformat(),
                        }
            except Exception as e:
                print(f"获取大盘指数失败: {e}")
        return None


class MockDataProvider(BaseDataProvider):
    """模拟数据提供者 - 用于测试"""

    async def get_stock_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        return {
            "code": stock_code,
            "name": "模拟股票",
            "price": 100.0,
            "change": 1.5,
            "change_pct": 1.52,
            "timestamp": datetime.now().isoformat(),
        }

    async def get_market_index(self, index_code: str = "000001") -> Optional[Dict[str, Any]]:
        return {
            "code": index_code,
            "name": "上证指数",
            "points": 3200.0,
            "change": 0.5,
            "change_pct": 0.02,
            "timestamp": datetime.now().isoformat(),
        }


def get_provider(provider_type: str = "eastmoney", **kwargs) -> BaseDataProvider:
    """获取数据提供者实例"""
    providers = {
        "eastmoney": EastMoneyProvider,
        "sina": SinaProvider,
        "mock": MockDataProvider,
    }
    provider_class = providers.get(provider_type, EastMoneyProvider)
    return provider_class(**kwargs)
