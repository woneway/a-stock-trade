"""
交易日历模型
对应 akshare API: tool_trade_date_hist_sina
"""
from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class TradeCalendar(SQLModel, table=True):
    """交易日历 - tool_trade_date_hist_sina"""
    __tablename__ = "trade_calendar"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 交易日期
    trade_date: date = Field(index=True, unique=True, description="交易日期")

    # 交易状态: 0=非交易日, 1=交易日
    is_trading_day: int = Field(default=1, description="是否交易日: 0=非交易日, 1=交易日")

    class Config:
        populate_by_name = True
