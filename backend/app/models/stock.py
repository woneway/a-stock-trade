from datetime import date, datetime
from sqlmodel import Field, SQLModel
from typing import Optional


class Stock(SQLModel, table=True):
    __tablename__ = "stocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    name: str
    sector: Optional[str] = Field(default=None, index=True)

    # 行情数据
    price: Optional[float] = Field(default=None, alias="price")
    change: Optional[float] = Field(default=None, alias="change")
    turnover_rate: Optional[float] = Field(default=None, alias="turnoverRate")
    volume_ratio: Optional[float] = Field(default=None, alias="volumeRatio")
    market_cap: Optional[float] = Field(default=None, alias="marketCap")
    amplitude: Optional[float] = Field(default=None, alias="amplitude")

    # 涨停相关
    limit_consecutive: Optional[int] = Field(default=0, alias="limitConsecutive")
    is_limit_up: bool = Field(default=False, alias="isLimitUp")
    is_limit_down: bool = Field(default=False, alias="isLimitDown")

    # 其他
    trade_date: Optional[date] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Config:
        populate_by_name = True
