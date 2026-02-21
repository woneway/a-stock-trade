from pydantic import BaseModel
from datetime import date
from typing import Optional


class TradeBase(BaseModel):
    code: str
    name: str
    action: str
    price: float
    quantity: int
    amount: float
    fee: float
    reason: str
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None


class TradeCreate(TradeBase):
    trade_date: date


class TradeResponse(TradeBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class TradeSummary(BaseModel):
    total_trades: int
    total_fee: float
    total_pnl: float
