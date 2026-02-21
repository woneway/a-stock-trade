from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List
from datetime import date

from app.database import engine
from app.models.trade import Trade
from app.schemas.trade import TradeCreate, TradeResponse, TradeSummary


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.get("", response_model=List[TradeResponse])
def get_trades(db: Session = Depends(get_db), trade_date: date = None):
    statement = select(Trade).order_by(Trade.trade_date.desc())
    if trade_date:
        statement = statement.where(Trade.trade_date == trade_date)
    return db.exec(statement).all()


@router.post("", response_model=TradeResponse)
def create_trade(item: TradeCreate, db: Session = Depends(get_db)):
    db_item = Trade.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/summary", response_model=TradeSummary)
def get_trade_summary(db: Session = Depends(get_db), trade_date: date = None):
    statement = select(Trade)
    if trade_date:
        statement = statement.where(Trade.trade_date == trade_date)
    
    trades = db.exec(statement).all()
    
    total_trades = len(trades)
    total_fee = sum(t.fee for t in trades)
    total_pnl = sum(t.pnl if t.pnl else 0 for t in trades)
    
    return TradeSummary(
        total_trades=total_trades,
        total_fee=total_fee,
        total_pnl=total_pnl,
    )


@router.get("/{item_id}", response_model=TradeResponse)
def get_trade(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Trade, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Trade not found")
    return item
