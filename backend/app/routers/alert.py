from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date

from app.database import engine
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
def get_alerts(db: Session = Depends(get_db), triggered: bool = None):
    statement = select(Alert).order_by(Alert.created_at.desc())
    if triggered is not None:
        statement = statement.where(Alert.triggered == triggered)
    return db.exec(statement).all()


@router.post("", response_model=AlertResponse)
def create_alert(item: AlertCreate, db: Session = Depends(get_db)):
    db_item = Alert.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=AlertResponse)
def get_alert(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Alert, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Alert not found")
    return item


@router.put("/{item_id}", response_model=AlertResponse)
def update_alert(item_id: int, item: AlertUpdate, db: Session = Depends(get_db)):
    db_item = db.get(Alert, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_alert(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Alert, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(item)
    db.commit()
    return {"ok": True}


@router.post("/{item_id}/trigger")
def trigger_alert(item_id: int, current_price: float, db: Session = Depends(get_db)):
    item = db.get(Alert, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    item.triggered = True
    item.current_price = current_price
    item.triggered_at = date.today()
    
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
