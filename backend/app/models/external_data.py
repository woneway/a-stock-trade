from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List


class ExternalStockBasic(SQLModel, table=True):
    __tablename__ = "external_stock_basics"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, description="股票代码")
    code_full: str = Field(unique=True, index=True, description="完整代码(sz.000001)")
    name: str = Field(description="股票名称")
    market: str = Field(index=True, description="市场(sh/sz)")
    exchange: str = Field(description="交易所(SSE/SZSE)")
    list_status: str = Field(default="L", description="上市状态(L/D)")
    list_date: Optional[date] = Field(default=None, description="上市日期")

    quotes: List["ExternalStockQuote"] = Relationship(back_populates="stock")
    klines: List["ExternalStockKline"] = Relationship(back_populates="stock")

    class Config:
        populate_by_name = True


class ExternalStockQuote(SQLModel, table=True):
    __tablename__ = "external_stock_quotes"

    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="external_stock_basics.id", index=True)
    trade_date: date = Field(index=True)

    open: Optional[float] = Field(default=None, description="开盘价")
    high: Optional[float] = Field(default=None, description="最高价")
    low: Optional[float] = Field(default=None, description="最低价")
    close: Optional[float] = Field(default=None, description="收盘价")
    volume: Optional[float] = Field(default=None, description="成交量")
    amount: Optional[float] = Field(default=None, description="成交额")
    change: Optional[float] = Field(default=None, description="涨跌额")
    pct_chg: Optional[float] = Field(default=None, description="涨跌幅")
    turnover_rate: Optional[float] = Field(default=None, description="换手率")
    volume_ratio: Optional[float] = Field(default=None, description="量比")
    amplitude: Optional[float] = Field(default=None, description="振幅")
    market_cap: Optional[float] = Field(default=None, description="总市值")
    circ_market_cap: Optional[float] = Field(default=None, description="流通市值")

    stock: Optional[ExternalStockBasic] = Relationship(back_populates="quotes")

    class Config:
        populate_by_name = True


class ExternalStockKline(SQLModel, table=True):
    __tablename__ = "external_stock_klines"

    id: Optional[int] = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="external_stock_basics.id", index=True)
    trade_date: date = Field(index=True)

    open: Optional[float] = Field(default=None)
    high: Optional[float] = Field(default=None)
    low: Optional[float] = Field(default=None)
    close: Optional[float] = Field(default=None)
    volume: Optional[float] = Field(default=None)
    amount: Optional[float] = Field(default=None)
    change: Optional[float] = Field(default=None)
    pct_chg: Optional[float] = Field(default=None)
    turnover_rate: Optional[float] = Field(default=None)

    stock: Optional[ExternalStockBasic] = Relationship(back_populates="klines")

    class Config:
        populate_by_name = True


class ExternalSectorData(SQLModel, table=True):
    __tablename__ = "external_sector_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    sector_code: str = Field(index=True)
    sector_name: str = Field(index=True)
    trade_date: date = Field(index=True)

    change: Optional[float] = Field(default=None)
    turnover_rate: Optional[float] = Field(default=None)
    market_cap: Optional[float] = Field(default=None)
    avg_change: Optional[float] = Field(default=None)
    strength: Optional[int] = Field(default=None)
    trend: Optional[str] = Field(default=None)

    class Config:
        populate_by_name = True


class ExternalDragonListData(SQLModel, table=True):
    __tablename__ = "external_dragon_list_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True)
    code: str = Field(index=True)
    name: str
    list_type: str = Field(alias="listType")
    buy: Optional[float] = Field(default=None)
    sell: Optional[float] = Field(default=None)
    net: Optional[float] = Field(default=None)
    broker: Optional[str] = Field(default=None)
    reason: Optional[str] = Field(default=None)

    class Config:
        populate_by_name = True


class ExternalLimitData(SQLModel, table=True):
    __tablename__ = "external_limit_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(unique=True, index=True)

    limit_up_total: Optional[int] = Field(default=None)
    limit_up_yesterday: Optional[int] = Field(default=None)
    limit_up_new: Optional[int] = Field(default=None, alias="newHigh")
    limit_up_continuation: Optional[int] = Field(default=None)
    limit_down_total: Optional[int] = Field(default=None)

    class Config:
        populate_by_name = True


class ExternalCapitalFlowData(SQLModel, table=True):
    __tablename__ = "external_capital_flow_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True)
    sector: str = Field(index=True)
    flow_type: str = Field(alias="flowType")
    amount: Optional[float] = Field(default=None)
    stocks: Optional[str] = Field(default=None)

    class Config:
        populate_by_name = True


class ExternalNorthMoneyData(SQLModel, table=True):
    __tablename__ = "external_north_money_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(unique=True, index=True)

    inflow: Optional[float] = Field(default=None)
    outflow: Optional[float] = Field(default=None)
    net: Optional[float] = Field(default=None)

    class Config:
        populate_by_name = True


class ExternalSyncLog(SQLModel, table=True):
    __tablename__ = "external_sync_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    source: str = Field(index=True)
    table_name: str
    records_count: int = Field(default=0)
    start_time: datetime
    end_time: Optional[datetime] = Field(default=None)
    status: str = Field(default="running")
    error_message: Optional[str] = Field(default=None)

    class Config:
        populate_by_name = True
