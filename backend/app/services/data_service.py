"""
统一数据服务层
- 优先级：缓存 > 数据库 > akshare
- 提供股票数据获取、K线同步功能
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
import pandas as pd
import logging
import time
from functools import lru_cache
from threading import Lock

from sqlmodel import Session, select
from app.database import engine
from app.models.external_data import StockBasic, StockKline

logger = logging.getLogger(__name__)


class DataCache:
    """简单的内存缓存"""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self.ttl_seconds = ttl_seconds
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                if time.time() - self._timestamps[key] < self.ttl_seconds:
                    return self._cache[key]
                else:
                    del self._cache[key]
                    del self._timestamps[key]
        return None

    def set(self, key: str, value: Any):
        with self._lock:
            self._cache[key] = value
            self._timestamps[key] = time.time()

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()


# 全局缓存实例
_data_cache = DataCache(ttl_seconds=300)  # 5分钟缓存


class DataService:
    """统一数据服务"""

    @staticmethod
    def get_kline_dataframe(
        stock_code: str,
        start_date: str,
        end_date: str,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        获取K线数据
        优先级：缓存 > 数据库 > akshare
        """
        cache_key = f"kline:{stock_code}:{start_date}:{end_date}"

        # 1. 尝试从缓存获取
        if not force_refresh:
            cached = _data_cache.get(cache_key)
            if cached is not None:
                logger.info(f"从缓存获取 {stock_code} K线数据")
                return cached

        # 2. 尝试从数据库获取
        df = DataService._get_from_database(stock_code, start_date, end_date)
        if df is not None and len(df) > 10:
            logger.info(f"从数据库获取 {stock_code} K线数据: {len(df)}条")
            _data_cache.set(cache_key, df)
            return df

        # 3. 从akshare获取并同步到数据库
        logger.info(f"从akshare获取 {stock_code} K线数据")
        df = DataService._fetch_from_akshare(stock_code, start_date, end_date)
        if df is not None and len(df) > 0:
            # 异步保存到数据库（不阻塞返回）
            DataService._async_save_to_database(stock_code, df)
            _data_cache.set(cache_key, df)

        return df

    @staticmethod
    def _get_from_database(
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """从数据库获取K线数据"""
        try:
            with Session(engine) as session:
                stock = session.exec(
                    select(StockBasic).where(StockBasic.code == stock_code)
                ).first()

                if not stock:
                    return None

                klines = session.exec(
                    select(StockKline).where(
                        StockKline.stock_id == stock.id,
                        StockKline.trade_date >= start_date,
                        StockKline.trade_date <= end_date,
                    ).order_by(StockKline.trade_date.asc())
                ).all()

                if not klines:
                    return None

                data = []
                for k in klines:
                    data.append({
                        'Open': k.open or 0,
                        'High': k.high or 0,
                        'Low': k.low or 0,
                        'Close': k.close or 0,
                        'Volume': k.volume or 0,
                    })

                return pd.DataFrame(data)
        except Exception as e:
            logger.warning(f"从数据库获取失败: {e}")
            return None

    @staticmethod
    def _fetch_from_akshare(
        stock_code: str,
        start_date: str,
        end_date: str,
        max_retries: int = 3
    ) -> Optional[pd.DataFrame]:
        """从akshare获取K线数据"""
        import akshare as ak

        # 转换代码格式
        if stock_code.startswith('sh') or stock_code.startswith('sz'):
            symbol = stock_code
        elif stock_code.startswith('6'):
            symbol = f"sh{stock_code}"
        else:
            symbol = f"sz{stock_code}"

        # 转换日期格式
        start_str = start_date.replace('-', '')
        end_str = end_date.replace('-', '')

        for attempt in range(max_retries):
            try:
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_str,
                    end_date=end_str,
                    adjust="qfq"
                )

                if df is None or df.empty:
                    logger.warning(f"akshare返回空数据: {stock_code}")
                    return None

                result = pd.DataFrame()
                result['Open'] = df['开盘'].astype(float)
                result['High'] = df['最高'].astype(float)
                result['Low'] = df['最低'].astype(float)
                result['Close'] = df['收盘'].astype(float)
                result['Volume'] = df['成交量'].astype(float)

                return result

            except Exception as e:
                logger.warning(f"akshare获取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待后重试

        return None

    @staticmethod
    def _async_save_to_database(stock_code: str, df: pd.DataFrame):
        """异步保存到数据库"""
        import threading
        thread = threading.Thread(
            target=DataService._save_to_database,
            args=(stock_code, df)
        )
        thread.daemon = True
        thread.start()

    @staticmethod
    def _save_to_database(stock_code: str, df: pd.DataFrame):
        """保存到数据库"""
        try:
            with Session(engine) as session:
                # 获取或创建股票
                stock = session.exec(
                    select(StockBasic).where(StockBasic.code == stock_code)
                ).first()

                if not stock:
                    # 根据代码判断市场
                    if stock_code.startswith('6'):
                        market = 'sh'
                        exchange = 'SSE'
                    else:
                        market = 'sz'
                        exchange = 'SZSE'

                    stock = StockBasic(
                        code=stock_code,
                        code_full=f"{market}.{stock_code}",
                        name=f"股票{stock_code}",
                        market=market,
                        exchange=exchange,
                        list_status='L'
                    )
                    session.add(stock)
                    session.commit()
                    session.refresh(stock)

                # 保存K线数据
                from datetime import datetime as dt
                for _, row in df.iterrows():
                    # 检查是否已存在
                    trade_date = row.get('date')
                    if isinstance(trade_date, str):
                        trade_date = dt.strptime(trade_date, '%Y-%m-%d').date()
                    elif hasattr(trade_date, 'date'):
                        trade_date = trade_date.date()

                    existing = session.exec(
                        select(StockKline).where(
                            StockKline.stock_id == stock.id,
                            StockKline.trade_date == trade_date
                        )
                    ).first()

                    if existing:
                        continue

                    kline = StockKline(
                        stock_id=stock.id,
                        trade_date=trade_date,
                        open=row['Open'],
                        high=row['High'],
                        low=row['Low'],
                        close=row['Close'],
                        volume=row['Volume'],
                    )
                    session.add(kline)

                session.commit()
                logger.info(f"已保存 {stock_code} {len(df)} 条K线数据到数据库")

        except Exception as e:
            logger.error(f"保存到数据库失败: {e}")

    @staticmethod
    def sync_stock_to_database(
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """同步股票数据到数据库"""
        df = DataService._fetch_from_akshare(stock_code, start_date, end_date)
        if df is None or len(df) == 0:
            return {"status": "error", "message": "获取数据失败"}

        DataService._save_to_database(stock_code, df)
        return {"status": "success", "count": len(df)}

    @staticmethod
    def clear_cache():
        """清除缓存"""
        _data_cache.clear()


def get_stock_list() -> List[Dict[str, str]]:
    """获取股票列表"""
    cache_key = "stock_list"
    cached = _data_cache.get(cache_key)
    if cached:
        return cached

    try:
        with Session(engine) as session:
            stocks = session.exec(
                select(StockBasic).limit(100)
            ).all()

            result = [
                {"code": s.code, "name": s.name, "market": s.market}
                for s in stocks
            ]

            _data_cache.set(cache_key, result)
            return result
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return []
