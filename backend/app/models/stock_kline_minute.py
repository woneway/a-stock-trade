"""
分时数据模型
对应数据库 astock.stock_kline_minute
"""
from typing import Optional
from datetime import date, time
from sqlmodel import SQLModel, Field


class StockKlineMinute(SQLModel, table=True):
    """分时数据"""
    __tablename__ = "stock_kline_minute"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(description="交易日期")
    stock_code: str = Field(description="股票代码", max_length=10)
    time_minute: time = Field(description="分钟时间")
    open: Optional[float] = Field(default=None, description="开盘价")
    close: Optional[float] = Field(default=None, description="收盘价")
    high: Optional[float] = Field(default=None, description="最高价")
    low: Optional[float] = Field(default=None, description="最低价")
    volume: Optional[float] = Field(default=None, description="成交量")
    amount: Optional[float] = Field(default=None, description="成交额")
    avg_price: Optional[float] = Field(default=None, description="均价")
