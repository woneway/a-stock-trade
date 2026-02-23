from pydantic import BaseModel
from datetime import date
from typing import Optional


class AlertBase(BaseModel):
    stock_code: str
    stock_name: str
    alert_type: str
    target_price: float
    current_price: float = 0
    triggered: bool = False
    message: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    current_price: Optional[float] = None
    triggered: Optional[bool] = None
    message: Optional[str] = None
    triggered_at: Optional[date] = None


class AlertResponse(AlertBase):
    id: Optional[int] = None
    created_at: date
    triggered_at: Optional[date] = None

    class Config:
        from_attributes = True
