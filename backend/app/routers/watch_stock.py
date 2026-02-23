from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date

from app.database import engine
from app.models.watch_stock import WatchStock
from app.schemas.watch_stock import WatchStockCreate, WatchStockUpdate, WatchStockResponse


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/watch-stocks", tags=["watch-stocks"])
router_alias = APIRouter(prefix="/api/watch-stock", tags=["watch-stocks"])


@router.get("", response_model=List[WatchStockResponse])
def get_watch_stocks(db: Session = Depends(get_db)):
    statement = select(WatchStock).order_by(WatchStock.created_at.desc())
    return db.exec(statement).all()


@router.post("", response_model=WatchStockResponse)
def create_watch_stock(item: WatchStockCreate, db: Session = Depends(get_db)):
    db_item = WatchStock.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=WatchStockResponse)
def get_watch_stock(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WatchStock, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Watch stock not found")
    return item


@router.put("/{item_id}", response_model=WatchStockResponse)
def update_watch_stock(item_id: int, item: WatchStockUpdate, db: Session = Depends(get_db)):
    db_item = db.get(WatchStock, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Watch stock not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    db_item.updated_at = date.today()
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_watch_stock(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WatchStock, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Watch stock not found")
    db.delete(item)
    db.commit()
    return {"ok": True}


@router_alias.get("", response_model=List[WatchStockResponse])
def get_watch_stocks_alias(db: Session = Depends(get_db)):
    statement = select(WatchStock).order_by(WatchStock.created_at.desc())
    return db.exec(statement).all()


@router_alias.post("", response_model=WatchStockResponse)
def create_watch_stock_alias(item: WatchStockCreate, db: Session = Depends(get_db)):
    db_item = WatchStock.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router_alias.get("/{item_id}", response_model=WatchStockResponse)
def get_watch_stock_alias(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WatchStock, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Watch stock not found")
    return item


@router_alias.put("/{item_id}", response_model=WatchStockResponse)
def update_watch_stock_alias(item_id: int, item: WatchStockUpdate, db: Session = Depends(get_db)):
    db_item = db.get(WatchStock, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Watch stock not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    db_item.updated_at = date.today()
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router_alias.delete("/{item_id}")
def delete_watch_stock_alias(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WatchStock, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Watch stock not found")
    db.delete(item)
    db.commit()
    return {"ok": True}
