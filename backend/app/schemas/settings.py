from pydantic import BaseModel
from datetime import date
from typing import Optional


class AccountSettingsBase(BaseModel):
    account_name: str = "默认账户"
    initial_capital: float = 100000
    current_capital: float = 100000


class AccountSettingsCreate(AccountSettingsBase):
    pass


class AccountSettingsUpdate(BaseModel):
    account_name: Optional[str] = None
    initial_capital: Optional[float] = None
    current_capital: Optional[float] = None


class AccountSettingsResponse(AccountSettingsBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class RiskConfigBase(BaseModel):
    stop_loss_ratio: float = 7.0
    take_profit_ratio: float = 15.0
    max_position_ratio: float = 20.0
    max_single_stock: float = 20.0
    max_trades_per_day: int = 5


class RiskConfigCreate(RiskConfigBase):
    pass


class RiskConfigUpdate(BaseModel):
    stop_loss_ratio: Optional[float] = None
    take_profit_ratio: Optional[float] = None
    max_position_ratio: Optional[float] = None
    max_single_stock: Optional[float] = None
    max_trades_per_day: Optional[int] = None


class RiskConfigResponse(RiskConfigBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class NotificationConfigBase(BaseModel):
    enable_price_alert: bool = True
    enable_trade_alert: bool = True
    enable_daily_summary: bool = True
    alert_threshold: float = 5.0


class NotificationConfigCreate(NotificationConfigBase):
    pass


class NotificationConfigUpdate(BaseModel):
    enable_price_alert: Optional[bool] = None
    enable_trade_alert: Optional[bool] = None
    enable_daily_summary: Optional[bool] = None
    alert_threshold: Optional[float] = None


class NotificationConfigResponse(NotificationConfigBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
