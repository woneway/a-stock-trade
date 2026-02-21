from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class Strategy(SQLModel, table=True):
    __tablename__ = "strategies"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    entry_condition: Optional[str] = Field(alias="entryCondition")
    exit_condition: Optional[str] = Field(alias="exitCondition")
    stop_loss: float = Field(default=7.0, alias="stopLoss")
    position_size: float = Field(default=20.0, alias="positionSize")
    is_active: bool = Field(default=True, alias="isActive")
    created_at: date = Field(default_factory=date.today, alias="createdAt")
    updated_at: date = Field(default_factory=date.today, alias="updatedAt")

    class Config:
        populate_by_name = True
