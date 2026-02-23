from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class WatchStock(SQLModel, table=True):
    __tablename__ = "watch_stocks"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    name: str
    price: Optional[float] = None
    change: Optional[float] = None
    strategy: str
    status: str = Field(default="observing")
    signal: Optional[str] = None
    signal_reason: Optional[str] = None
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)
