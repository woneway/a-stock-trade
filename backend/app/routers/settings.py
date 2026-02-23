from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date

from app.database import engine
from app.models.settings import AccountSettings, RiskConfig, NotificationConfig
from app.schemas.settings import (
    AccountSettingsCreate,
    AccountSettingsUpdate,
    AccountSettingsResponse,
    RiskConfigCreate,
    RiskConfigUpdate,
    RiskConfigResponse,
    NotificationConfigCreate,
    NotificationConfigUpdate,
    NotificationConfigResponse,
)


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/account", response_model=AccountSettingsResponse)
def get_account(db: Session = Depends(get_db)):
    result = db.exec(select(AccountSettings)).first()
    if not result:
        result = AccountSettings()
        db.add(result)
        db.commit()
        db.refresh(result)
    return result


@router.put("/account", response_model=AccountSettingsResponse)
def update_account(item: AccountSettingsUpdate, db: Session = Depends(get_db)):
    result = db.exec(select(AccountSettings)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Account not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(result, key, value)
    result.updated_at = date.today()
    
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/risk", response_model=RiskConfigResponse)
def get_risk_config(db: Session = Depends(get_db)):
    result = db.exec(select(RiskConfig)).first()
    if not result:
        result = RiskConfig()
        db.add(result)
        db.commit()
        db.refresh(result)
    return result


@router.put("/risk", response_model=RiskConfigResponse)
def update_risk_config(item: RiskConfigUpdate, db: Session = Depends(get_db)):
    result = db.exec(select(RiskConfig)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Risk config not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(result, key, value)
    result.updated_at = date.today()
    
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("/notification", response_model=NotificationConfigResponse)
def get_notification_config(db: Session = Depends(get_db)):
    result = db.exec(select(NotificationConfig)).first()
    if not result:
        result = NotificationConfig()
        db.add(result)
        db.commit()
        db.refresh(result)
    return result


@router.put("/notification", response_model=NotificationConfigResponse)
def update_notification_config(item: NotificationConfigUpdate, db: Session = Depends(get_db)):
    result = db.exec(select(NotificationConfig)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Notification config not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(result, key, value)
    result.updated_at = date.today()
    
    db.add(result)
    db.commit()
    db.refresh(result)
    return result
