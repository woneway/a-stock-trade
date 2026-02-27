"""
龙虎榜数据接口
包含：龙虎榜详情、营业部排行、个股上榜统计、个股龙虎榜详情
"""
from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class LhbDetailInput(BaseModel):
    """入参 - 龙虎榜详情"""
    start_date: str = Field(description="开始日期，格式 YYYYMMDD")
    end_date: str = Field(description="结束日期，格式 YYYYMMDD")


class LhbDetailOutput(BaseModel):
    """出参 - 龙虎榜详情"""
    序号: Optional[int] = Field(default=None, description="序号")
    代码: Optional[str] = Field(default=None, description="股票代码")
    名称: Optional[str] = Field(default=None, description="股票名称")
    上榜日: Optional[Union[str, date]] = Field(default=None, description="上榜日期")
    收盘价: Optional[float] = Field(default=None, description="收盘价")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    龙虎榜净买额: Optional[float] = Field(default=None, description="龙虎榜净买额(元)")
    龙虎榜买入额: Optional[float] = Field(default=None, description="龙虎榜买入额(元)")
    龙虎榜卖出额: Optional[float] = Field(default=None, description="龙虎榜卖出额(元)")
    上榜原因: Optional[str] = Field(default=None, description="上榜原因")
    上榜后1日: Optional[float] = Field(default=None, description="上榜后1日涨幅(%)")


class LhbYybphInput(BaseModel):
    """入参 - 营业部排行"""
    symbol: str = Field(default="近一月", description="时间范围：近一月/近三月/近六月/近一年")


class LhbYybphOutput(BaseModel):
    """出参 - 营业部排行"""
    序号: Optional[int] = Field(default=None, description="序号")
    营业部名称: Optional[str] = Field(default=None, description="营业部名称")
    上榜后1天_买入次数: Optional[int] = Field(default=None, description="上榜后1天-买入次数")
    上榜后1天_平均涨幅: Optional[float] = Field(default=None, description="上榜后1天-平均涨幅(%)")
    上榜后1天_上涨概率: Optional[float] = Field(default=None, description="上榜后1天-上涨概率(%)")


class LhbStockStatisticInput(BaseModel):
    """入参 - 个股上榜统计"""
    symbol: str = Field(default="近一月", description="时间范围：近一月/近三月/近六月/近一年")


class LhbStockStatisticOutput(BaseModel):
    """出参 - 个股上榜统计"""
    序号: Optional[int] = Field(default=None, description="序号")
    代码: Optional[str] = Field(default=None, description="股票代码")
    名称: Optional[str] = Field(default=None, description="股票名称")
    上榜次数: Optional[int] = Field(default=None, description="上榜次数")
    龙虎榜净买额: Optional[float] = Field(default=None, description="龙虎榜净买额(元)")


class LhbStockDetailInput(BaseModel):
    """入参 - 个股龙虎榜详情"""
    symbol: str = Field(description="股票代码")
    date: str = Field(description="日期，格式 YYYYMMDD")
    flag: str = Field(default="买入", description="类型：买入/卖出")


class LhbStockDetailOutput(BaseModel):
    """出参 - 个股龙虎榜详情"""
    序号: Optional[int] = Field(default=None, description="序号")
    交易营业部名称: Optional[str] = Field(default=None, description="交易营业部名称")
    买入金额: Optional[float] = Field(default=None, description="买入金额(元)")
    卖出金额: Optional[float] = Field(default=None, description="卖出金额(元)")
    净额: Optional[float] = Field(default=None, description="净额(元)")


# ============ 接口函数 ============

def get_lhb_detail_em(start_date: str, end_date: str) -> List[LhbDetailOutput]:
    """龙虎榜详情"""
    df = ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
    records = df.to_dict(orient="records")
    return [LhbDetailOutput(**r) for r in records]


def get_lhb_yybph_em(symbol: str = "近一月") -> List[LhbYybphOutput]:
    """营业部排行"""
    df = ak.stock_lhb_yybph_em(symbol=symbol)
    records = df.to_dict(orient="records")
    return [LhbYybphOutput(**r) for r in records]


def get_lhb_stock_statistic_em(symbol: str = "近一月") -> List[LhbStockStatisticOutput]:
    """个股上榜统计"""
    df = ak.stock_lhb_stock_statistic_em(symbol=symbol)
    records = df.to_dict(orient="records")
    return [LhbStockStatisticOutput(**r) for r in records]


def get_lhb_stock_detail_em(symbol: str, date: str, flag: str = "买入") -> List[LhbStockDetailOutput]:
    """个股龙虎榜详情"""
    df = ak.stock_lhb_stock_detail_em(symbol=symbol, date=date, flag=flag)
    records = df.to_dict(orient="records")
    return [LhbStockDetailOutput(**r) for r in records]
