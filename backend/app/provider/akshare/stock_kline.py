"""
历史行情数据接口
包含：日K线数据
"""
from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class StockZhAHistInput(BaseModel):
    """入参 - 日K线数据"""
    symbol: str = Field(description="股票代码，如 603777")
    period: str = Field(default="daily", description="周期：daily/weekly/monthly")
    start_date: str = Field(description="开始日期，格式 YYYYMMDD")
    end_date: str = Field(description="结束日期，格式 YYYYMMDD")
    adjust: str = Field(default="", description="复权类型：qfq前复权/hfq后复权/空字符串不复权")


class StockZhAHistOutput(BaseModel):
    """出参 - 日K线数据"""
    日期: Optional[Union[str, date]] = Field(default=None, description="日期")
    股票代码: Optional[str] = Field(default=None, description="股票代码")
    开盘: Optional[float] = Field(default=None, description="开盘价")
    收盘: Optional[float] = Field(default=None, description="收盘价")
    最高: Optional[float] = Field(default=None, description="最高价")
    最低: Optional[float] = Field(default=None, description="最低价")
    成交量: Optional[float] = Field(default=None, description="成交量(手)")
    成交额: Optional[float] = Field(default=None, description="成交额(元)")
    振幅: Optional[float] = Field(default=None, description="振幅(%)")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    换手率: Optional[float] = Field(default=None, description="换手率(%)")


# ============ 接口函数 ============

def get_stock_zh_a_hist(
    symbol: str,
    period: str = "daily",
    start_date: str = "20240101",
    end_date: str = "20241231",
    adjust: str = ""
) -> List[StockZhAHistOutput]:
    """沪深京A股日频率数据"""
    df = ak.stock_zh_a_hist(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust
    )
    records = df.to_dict(orient="records")
    return [StockZhAHistOutput(**r) for r in records]
