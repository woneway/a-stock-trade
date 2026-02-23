from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Account, RiskConfig, NotificationConfig, AppConfig

router = APIRouter()


class AccountUpdate(BaseModel):
    total_assets: Optional[float] = None
    available_cash: Optional[float] = None
    market_value: Optional[float] = None
    today_profit: Optional[float] = None
    today_profit_ratio: Optional[float] = None
    total_profit: Optional[float] = None
    total_profit_ratio: Optional[float] = None


class AccountResponse(BaseModel):
    id: int
    total_assets: float
    available_cash: float
    market_value: float
    today_profit: float
    today_profit_ratio: float
    total_profit: float
    total_profit_ratio: float
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskConfigUpdate(BaseModel):
    max_position_ratio: Optional[float] = None
    daily_loss_limit: Optional[float] = None
    default_stop_loss: Optional[float] = None
    default_take_profit: Optional[float] = None
    max_positions: Optional[int] = None


class RiskConfigResponse(BaseModel):
    id: int
    max_position_ratio: float
    daily_loss_limit: float
    default_stop_loss: float
    default_take_profit: float
    max_positions: int
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationConfigUpdate(BaseModel):
    signal_notify: Optional[bool] = None
    trade_notify: Optional[bool] = None
    stop_loss_notify: Optional[bool] = None


class NotificationConfigResponse(BaseModel):
    id: int
    signal_notify: bool
    trade_notify: bool
    stop_loss_notify: bool
    updated_at: datetime

    class Config:
        from_attributes = True


class AppConfigUpdate(BaseModel):
    theme: Optional[str] = None


class AppConfigResponse(BaseModel):
    id: int
    theme: str
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/account", response_model=AccountResponse)
def get_account(db: Session = Depends(get_db)):
    account = db.query(Account).first()
    if not account:
        account = Account()
        db.add(account)
        db.commit()
        db.refresh(account)
    return account


@router.put("/account", response_model=AccountResponse)
def update_account(account_update: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).first()
    if not account:
        account = Account()
        db.add(account)
        db.commit()
        db.refresh(account)

    update_data = account_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)

    account.updated_at = datetime.now()
    db.commit()
    db.refresh(account)
    return account


@router.get("/risk-config", response_model=RiskConfigResponse)
def get_risk_config(db: Session = Depends(get_db)):
    config = db.query(RiskConfig).first()
    if not config:
        config = RiskConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("/risk-config", response_model=RiskConfigResponse)
def update_risk_config(config_update: RiskConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(RiskConfig).first()
    if not config:
        config = RiskConfig()
        db.add(config)
        db.commit()
        db.refresh(config)

    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    config.updated_at = datetime.now()
    db.commit()
    db.refresh(config)
    return config


@router.get("/notification-config", response_model=NotificationConfigResponse)
def get_notification_config(db: Session = Depends(get_db)):
    config = db.query(NotificationConfig).first()
    if not config:
        config = NotificationConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("/notification-config", response_model=NotificationConfigResponse)
def update_notification_config(config_update: NotificationConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(NotificationConfig).first()
    if not config:
        config = NotificationConfig()
        db.add(config)
        db.commit()
        db.refresh(config)

    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    config.updated_at = datetime.now()
    db.commit()
    db.refresh(config)
    return config


@router.get("/app-config", response_model=AppConfigResponse)
def get_app_config(db: Session = Depends(get_db)):
    config = db.query(AppConfig).first()
    if not config:
        config = AppConfig()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.put("/app-config", response_model=AppConfigResponse)
def update_app_config(config_update: AppConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(AppConfig).first()
    if not config:
        config = AppConfig()
        db.add(config)
        db.commit()
        db.refresh(config)

    update_data = config_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config, key, value)

    config.updated_at = datetime.now()
    db.commit()
    db.refresh(config)
    return config


@router.get("/all-settings")
def get_all_settings(db: Session = Depends(get_db)):
    account = db.query(Account).first()
    if not account:
        account = Account()
        db.add(account)
        db.commit()
        db.refresh(account)

    risk_config = db.query(RiskConfig).first()
    if not risk_config:
        risk_config = RiskConfig()
        db.add(risk_config)
        db.commit()
        db.refresh(risk_config)

    notification_config = db.query(NotificationConfig).first()
    if not notification_config:
        notification_config = NotificationConfig()
        db.add(notification_config)
        db.commit()
        db.refresh(notification_config)

    app_config = db.query(AppConfig).first()
    if not app_config:
        app_config = AppConfig()
        db.add(app_config)
        db.commit()
        db.refresh(app_config)

    return {
        "account": account,
        "risk_config": risk_config,
        "notification_config": notification_config,
        "app_config": app_config
    }
