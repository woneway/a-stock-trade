from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"

    id: Optional[int] = Field(default=None, primary_key=True)
    stock_code: str = Field(index=True, alias="stockCode")
    stock_name: str = Field(alias="stockName")
    alert_type: str = Field(alias="alertType")
    target_price: float = Field(alias="targetPrice")
    current_price: Optional[float] = Field(default=0, alias="currentPrice")
    triggered: bool = Field(default=False)
    message: Optional[str] = None
    created_at: date = Field(default_factory=date.today, alias="createdAt")
    triggered_at: Optional[date] = Field(default=None, alias="triggeredAt")

    class Config:
        populate_by_name = True
