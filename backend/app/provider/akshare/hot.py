"""
热点数据接口
包含：赚钱效应分析，创新高/新低、股票热度排名
"""
from typing import List, Optional, Union
from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class MarketActivityInput(BaseModel):
    """入参 - 赚钱效应分析"""
    pass


class MarketActivityOutput(BaseModel):
    """出参 - 赚钱效应分析"""
    item: Optional[str] = Field(default=None, description="指标名称")
    value: Optional[Union[str, float]] = Field(default=None, description="指标值")


class HighLowStatisticsInput(BaseModel):
    """入参 - 创新高/新低"""
    symbol: str = Field(default="all", description="市场：all全部A股/sz50上证50/hs300沪深300/zz500中证500")


class HighLowStatisticsOutput(BaseModel):
    """出参 - 创新高/新低"""
    交易日: Optional[str] = Field(default=None, description="交易日")
    相关指数收盘价: Optional[float] = Field(default=None, description="相关指数收盘价")
    新高20日: Optional[int] = Field(default=None, description="20日新高")
    新低20日: Optional[int] = Field(default=None, description="20日新低")
    新高60日: Optional[int] = Field(default=None, description="60日新高")
    新低60日: Optional[int] = Field(default=None, description="60日新低")
    新高120日: Optional[int] = Field(default=None, description="120日新高")
    新低120日: Optional[int] = Field(default=None, description="120日新低")


class HotRankInput(BaseModel):
    """入参 - 股票热度排名"""
    pass


class HotRankOutput(BaseModel):
    """出参 - 股票热度排名"""
    排名: Optional[int] = Field(default=None, description="当前排名")
    代码: Optional[str] = Field(default=None, description="股票代码")
    名称: Optional[str] = Field(default=None, description="股票名称")
    最新价: Optional[float] = Field(default=None, description="最新价")
    涨跌额: Optional[float] = Field(default=None, description="涨跌额")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")


# ============ 接口函数 ============

def get_market_activity_legu() -> List[MarketActivityOutput]:
    """赚钱效应分析"""
    df = ak.stock_market_activity_legu()
    records = df.to_dict(orient="records")
    return [MarketActivityOutput(**r) for r in records]


def get_a_high_low_statistics(symbol: str = "all") -> List[HighLowStatisticsOutput]:
    """创新高/新低"""
    df = ak.stock_a_high_low_statistics(symbol=symbol)
    records = df.to_dict(orient="records")
    return [HighLowStatisticsOutput(**r) for r in records]


def get_hot_rank_em() -> List[HotRankOutput]:
    """股票热度排名"""
    df = ak.stock_hot_rank_em()
    records = df.to_dict(orient="records")
    return [HotRankOutput(**r) for r in records]
