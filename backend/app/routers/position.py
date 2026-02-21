from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date

from app.database import engine
from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/positions", tags=["positions"])


@router.get("", response_model=List[PositionResponse])
def get_positions(db: Session = Depends(get_db), status: str = None):
    statement = select(Position).order_by(Position.entry_date.desc())
    if status:
        statement = statement.where(Position.status == status)
    return db.exec(statement).all()


@router.post("", response_model=PositionResponse)
def create_position(item: PositionCreate, db: Session = Depends(get_db)):
    db_item = Position.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=PositionResponse)
def get_position(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Position, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    return item


@router.put("/{item_id}", response_model=PositionResponse)
def update_position(item_id: int, item: PositionUpdate, db: Session = Depends(get_db)):
    db_item = db.get(Position, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Position not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    db_item.updated_at = date.today()
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_position(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Position, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(item)
    db.commit()
    return {"ok": True}


@router.post("/{item_id}/close")
def close_position(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Position, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    item.status = "closed"
    item.updated_at = date.today()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
