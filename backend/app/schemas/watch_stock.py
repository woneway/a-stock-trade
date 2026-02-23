from pydantic import BaseModel
from datetime import date
from typing import Optional


class WatchStockBase(BaseModel):
    code: str
    name: str
    price: Optional[float] = None
    change: Optional[float] = None
    strategy: str
    status: str = "observing"
    signal: Optional[str] = None
    signal_reason: Optional[str] = None


class WatchStockCreate(WatchStockBase):
    pass


class WatchStockUpdate(BaseModel):
    price: Optional[float] = None
    change: Optional[float] = None
    strategy: Optional[str] = None
    status: Optional[str] = None
    signal: Optional[str] = None
    signal_reason: Optional[str] = None


class WatchStockResponse(WatchStockBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
