"""
缓存服务
用于交易日历等数据的缓存
"""
import json
import os
from typing import Optional, List
from datetime import datetime


class CacheService:
    """简单的缓存服务"""

    CACHE_DIR = "data/cache"

    @classmethod
    def _ensure_cache_dir(cls):
        os.makedirs(cls.CACHE_DIR, exist_ok=True)

    @classmethod
    def _get_cache_path(cls, key: str) -> str:
        cls._ensure_cache_dir()
        return os.path.join(cls.CACHE_DIR, f"{key}.json")

    @classmethod
    def _get_trade_calendar_from_local(cls, start_date: str, end_date: str) -> Optional[List]:
        """从本地获取交易日历"""
        cache_path = cls._get_cache_path("trade_calendar")
        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 简单检查是否有足够的数据
                return data if len(data) > 100 else None
        except:
            return None

    @classmethod
    def _fetch_trade_calendar_from_akshare(cls, start_date: str, end_date: str):
        """从akshare获取交易日历"""
        try:
            import akshare as ak
            df = ak.tool_trade_date_hist_sina()
            if df is not None:
                df['日期'] = df['日期'].astype(str)
                return df.to_dict(orient='records')
        except Exception as e:
            print(f"获取交易日历失败: {e}")
        return None

    @classmethod
    def _save_trade_calendar_to_local(cls, data):
        """保存交易日历到本地"""
        cache_path = cls._get_cache_path("trade_calendar")
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存交易日历失败: {e}")
