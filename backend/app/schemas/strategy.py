from pydantic import BaseModel
from datetime import date
from typing import Optional


class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    entry_condition: Optional[str] = None
    exit_condition: Optional[str] = None
    stop_loss: float = 7.0
    position_size: float = 20.0
    is_active: bool = True


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    entry_condition: Optional[str] = None
    exit_condition: Optional[str] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    is_active: Optional[bool] = None


class StrategyResponse(StrategyBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
