from datetime import date, time
from sqlmodel import Field, SQLModel
from typing import Optional


class Trade(SQLModel, table=True):
    __tablename__ = "trades"

    id: Optional[int] = Field(default=None, primary_key=True)

    pre_plan_id: Optional[int] = Field(default=None, foreign_key="pre_plans.id", alias="prePlanId")

    code: str = Field(index=True)
    name: str
    action: str
    price: float
    quantity: int
    amount: float
    fee: float
    reason: str
    trade_time: Optional[str] = Field(default=None, alias="tradeTime")

    entry_price: Optional[float] = Field(default=None, alias="entryPrice")
    exit_price: Optional[float] = Field(default=None, alias="exitPrice")
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = Field(default=None, alias="pnlPercent")

    is_planned: bool = Field(default=False, alias="isPlanned")
    plan_target_price: Optional[float] = Field(default=None, alias="planTargetPrice")

    trade_date: date = Field(index=True)

    class Config:
        populate_by_name = True
