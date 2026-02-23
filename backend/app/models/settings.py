from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class AccountSettings(SQLModel, table=True):
    __tablename__ = "account_settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    account_name: str = Field(default="默认账户")
    initial_capital: float = Field(default=100000)
    current_capital: float = Field(default=100000)
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)


class RiskConfig(SQLModel, table=True):
    __tablename__ = "risk_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    stop_loss_ratio: float = Field(default=7.0)
    take_profit_ratio: float = Field(default=15.0)
    max_position_ratio: float = Field(default=20.0)
    max_single_stock: float = Field(default=20.0)
    max_trades_per_day: int = Field(default=5)
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)


class NotificationConfig(SQLModel, table=True):
    __tablename__ = "notification_config"

    id: Optional[int] = Field(default=None, primary_key=True)
    enable_price_alert: bool = Field(default=True)
    enable_trade_alert: bool = Field(default=True)
    enable_daily_summary: bool = Field(default=True)
    alert_threshold: float = Field(default=5.0)
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)
