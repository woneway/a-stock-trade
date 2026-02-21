from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class Trade(SQLModel, table=True):
    __tablename__ = "trades"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    name: str
    action: str
    price: float
    quantity: int
    amount: float
    fee: float
    reason: str
    entry_price: Optional[float] = Field(default=None, alias="entryPrice")
    exit_price: Optional[float] = Field(default=None, alias="exitPrice")
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = Field(default=None, alias="pnlPercent")
    trade_date: date = Field(index=True)

    class Config:
        populate_by_name = True
