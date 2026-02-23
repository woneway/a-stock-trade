from pydantic import BaseModel
from datetime import date
from typing import Optional


class TradeBase(BaseModel):
    stock_code: str
    stock_name: str
    trade_type: str
    price: float
    quantity: int
    amount: float
    fee: float
    reason: str
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None

    pre_plan_id: Optional[int] = None
    is_planned: Optional[bool] = False
    plan_target_price: Optional[float] = None


class TradeCreate(TradeBase):
    trade_date: date


class TradeResponse(TradeBase):
    trade_date: date
    id: Optional[int] = None

    class Config:
        from_attributes = True


class TradeSummary(BaseModel):
    total_trades: int
    total_fee: float
    total_pnl: float
