from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date

from app.database import engine
from app.models.strategy import Strategy
from app.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("", response_model=List[StrategyResponse])
def get_strategies(db: Session = Depends(get_db), is_active: bool = None):
    statement = select(Strategy).order_by(Strategy.created_at.desc())
    if is_active is not None:
        statement = statement.where(Strategy.is_active == is_active)
    return db.exec(statement).all()


@router.post("", response_model=StrategyResponse)
def create_strategy(item: StrategyCreate, db: Session = Depends(get_db)):
    db_item = Strategy.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=StrategyResponse)
def get_strategy(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Strategy, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return item


@router.put("/{item_id}", response_model=StrategyResponse)
def update_strategy(item_id: int, item: StrategyUpdate, db: Session = Depends(get_db)):
    db_item = db.get(Strategy, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    db_item.updated_at = date.today()
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_strategy(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Strategy, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Strategy not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
