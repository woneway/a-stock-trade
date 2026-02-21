from pydantic import BaseModel
from datetime import date
from typing import Optional


class PositionBase(BaseModel):
    code: str
    name: str
    quantity: int
    avg_cost: float
    current_price: float = 0
    market_value: float = 0
    profit_loss: float = 0
    profit_ratio: float = 0
    status: str = "holding"
    entry_date: date


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    quantity: Optional[int] = None
    avg_cost: Optional[float] = None
    current_price: Optional[float] = None
    market_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_ratio: Optional[float] = None
    status: Optional[str] = None


class PositionResponse(PositionBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
