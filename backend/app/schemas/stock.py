from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional


class StockBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    name: str
    sector: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    turnover_rate: Optional[float] = None
    volume_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    amplitude: Optional[float] = None
    limit_consecutive: Optional[int] = 0
    is_limit_up: bool = False
    is_limit_down: bool = False
    trade_date: Optional[date] = None


class StockCreate(StockBase):
    pass


class StockUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    sector: Optional[str] = None
    price: Optional[float] = None
    change: Optional[float] = None
    turnover_rate: Optional[float] = None
    volume_ratio: Optional[float] = None
    market_cap: Optional[float] = None
    amplitude: Optional[float] = None
    limit_consecutive: Optional[int] = None
    is_limit_up: Optional[bool] = None
    is_limit_down: Optional[bool] = None
    trade_date: Optional[date] = None


class StockResponse(StockBase):
    id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 批量导入
class StockImport(BaseModel):
    stocks: list[StockCreate]
