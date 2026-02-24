from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class Position(SQLModel, table=True):
    __tablename__ = "positions"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    name: str
    quantity: int
    avg_cost: float = Field(alias="avgCost")
    current_price: Optional[float] = Field(default=0, alias="currentPrice")
    market_value: Optional[float] = Field(default=0, alias="marketValue")
    profit_loss: Optional[float] = Field(default=0, alias="profitLoss")
    profit_ratio: Optional[float] = Field(default=0, alias="profitRatio")
    status: str = Field(default="holding")
    entry_date: date = Field(default_factory=date.today, alias="entryDate")
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)
    sell_target: Optional[float] = Field(default=None, alias="sellTarget")
    stop_loss: Optional[float] = Field(default=None, alias="stopLoss")
    trade_plan: Optional[str] = Field(default=None, alias="tradePlan")
    holding_reason: Optional[str] = Field(default=None, alias="holdingReason")

    class Config:
        populate_by_name = True
