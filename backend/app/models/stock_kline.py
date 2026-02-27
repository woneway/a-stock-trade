"""
K线数据模型
对应数据库 astock.stock_kline
"""
from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class StockKline(SQLModel, table=True):
    """日K线数据"""
    __tablename__ = "stock_kline"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(description="交易日期")
    stock_code: str = Field(description="股票代码", max_length=10)
    open: Optional[float] = Field(default=None, description="开盘价")
    close: Optional[float] = Field(default=None, description="收盘价")
    high: Optional[float] = Field(default=None, description="最高价")
    low: Optional[float] = Field(default=None, description="最低价")
    volume: Optional[float] = Field(default=None, description="成交量(手)")
    amount: Optional[float] = Field(default=None, description="成交额(元)")
    amplitude: Optional[float] = Field(default=None, description="振幅(%)")
    change_pct: Optional[float] = Field(default=None, description="涨跌幅(%)")
    turnover_rate: Optional[float] = Field(default=None, description="换手率(%)")
