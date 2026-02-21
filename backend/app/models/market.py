from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class MarketIndex(SQLModel, table=True):
    __tablename__ = "market_indices"

    id: Optional[int] = Field(default=None, primary_key=True)
    index_name: str = Field(index=True)
    points: float
    change: float
    support: float
    resistance: float
    trade_date: date = Field(index=True)


class LimitUpData(SQLModel, table=True):
    __tablename__ = "limit_up_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    total: int
    yesterday: int
    new_high: int = Field(alias="newHigh")
    continuation: int
    trade_date: date = Field(index=True)

    class Config:
        populate_by_name = True


class DragonListItem(SQLModel, table=True):
    __tablename__ = "dragon_list"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    name: str
    reason: str
    institution: str
    list_type: str = Field(alias="listType")
    trade_date: date = Field(index=True)

    class Config:
        populate_by_name = True


class CapitalFlow(SQLModel, table=True):
    __tablename__ = "capital_flows"

    id: Optional[int] = Field(default=None, primary_key=True)
    sector: str
    amount: float
    flow_type: str = Field(alias="flowType")
    stocks: Optional[str] = None
    trade_date: date = Field(index=True)

    class Config:
        populate_by_name = True


class NorthMoney(SQLModel, table=True):
    __tablename__ = "north_money"

    id: Optional[int] = Field(default=None, primary_key=True)
    inflow: float
    outflow: float
    net: float
    trade_date: date = Field(index=True)


class SectorStrength(SQLModel, table=True):
    __tablename__ = "sector_strength"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    strength: int
    trend: str
    avg_change: float = Field(alias="avgChange")
    trade_date: date = Field(index=True)

    class Config:
        populate_by_name = True


class News(SQLModel, table=True):
    __tablename__ = "news"

    id: Optional[int] = Field(default=None, primary_key=True)
    news_type: str = Field(alias="newsType")
    content: str
    created_at: date = Field(index=True)

    class Config:
        populate_by_name = True


class SentimentPhase(SQLModel, table=True):
    __tablename__ = "sentiment_phases"

    id: Optional[int] = Field(default=None, primary_key=True)
    phase: str
    description: str
    advice: str
    trade_date: date = Field(index=True)
