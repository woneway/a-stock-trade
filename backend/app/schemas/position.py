from pydantic import BaseModel
from datetime import date
from typing import Optional


class PositionBase(BaseModel):
    stock_code: str
    stock_name: str
    quantity: int
    available_quantity: int = 0
    cost_price: float
    current_price: float = 0
    market_value: float = 0
    profit_amount: float = 0
    profit_ratio: float = 0
    status: str = "holding"
    opened_at: date


class PositionCreate(PositionBase):
    sell_target: Optional[float] = None
    stop_loss: Optional[float] = None
    trade_plan: Optional[str] = None
    holding_reason: Optional[str] = None


class PositionUpdate(BaseModel):
    quantity: Optional[int] = None
    available_quantity: Optional[int] = None
    cost_price: Optional[float] = None
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    profit_amount: Optional[float] = None
    profit_ratio: Optional[float] = None
    status: Optional[str] = None
    sell_target: Optional[float] = None
    stop_loss: Optional[float] = None
    trade_plan: Optional[str] = None
    holding_reason: Optional[str] = None


class PositionResponse(PositionBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date
    sell_target: Optional[float] = None
    stop_loss: Optional[float] = None
    trade_plan: Optional[str] = None
    holding_reason: Optional[str] = None

    class Config:
        from_attributes = True
