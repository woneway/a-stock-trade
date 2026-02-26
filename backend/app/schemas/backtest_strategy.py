from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, List, Dict, Any


class StrategyParam(BaseModel):
    """策略参数定义"""
    name: str
    label: str
    default: Any
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    type: str = "int"  # int, float, bool


class BacktestStrategyBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: Optional[str] = None
    code: str
    strategy_type: str = "custom"
    params_definition: Optional[List[Dict[str, Any]]] = []
    is_builtin: bool = False
    is_active: bool = True


class BacktestStrategyCreate(BacktestStrategyBase):
    pass


class BacktestStrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    strategy_type: Optional[str] = None
    params_definition: Optional[List[Dict[str, Any]]] = None
    is_builtin: Optional[bool] = None
    is_active: Optional[bool] = None


class BacktestStrategyResponse(BacktestStrategyBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
