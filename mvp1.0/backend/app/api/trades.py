from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Trade, Position, Account

router = APIRouter()


class TradeCreate(BaseModel):
    stock_code: str
    stock_name: str
    trade_type: str
    quantity: int
    price: float
    amount: float
    fee: float = 0
    stamp_duty: float = 0
    reason: Optional[str] = None  # 卖出原因
    stop_loss_price: Optional[float] = None
    take_profit_1_price: Optional[float] = None
    take_profit_2_price: Optional[float] = None
    position_id: Optional[int] = None
    plan_id: Optional[int] = None
    trade_date: date
    trade_time: Optional[str] = None
    notes: Optional[str] = None


class TradeUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[float] = None
    amount: Optional[float] = None
    fee: Optional[float] = None
    stamp_duty: Optional[float] = None
    reason: Optional[str] = None
    stop_loss_price: Optional[float] = None
    take_profit_1_price: Optional[float] = None
    take_profit_2_price: Optional[float] = None
    trade_time: Optional[str] = None
    notes: Optional[str] = None


class TradeResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    trade_type: str
    quantity: int
    price: float
    amount: float
    fee: float
    stamp_duty: float
    reason: Optional[str]
    stop_loss_price: Optional[float]
    take_profit_1_price: Optional[float]
    take_profit_2_price: Optional[float]
    position_id: Optional[int]
    plan_id: Optional[int]
    trade_date: date
    trade_time: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/trades", response_model=List[TradeResponse])
def get_trades(
    trade_type: Optional[str] = None,
    stock_code: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Trade)
    if trade_type:
        query = query.filter(Trade.trade_type == trade_type)
    if stock_code:
        query = query.filter(Trade.stock_code == stock_code)
    if start_date:
        query = query.filter(Trade.trade_date >= start_date)
    if end_date:
        query = query.filter(Trade.trade_date <= end_date)
    return query.order_by(Trade.trade_date.desc(), Trade.created_at.desc()).all()


@router.get("/trades/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int, db: Session = Depends(get_db)):
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="交易记录不存在")
    return trade


@router.post("/trades", response_model=TradeResponse)
def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    db_trade = Trade(**trade.model_dump())
    db.add(db_trade)

    if trade.position_id:
        position = db.query(Position).filter(Position.id == trade.position_id).first()
        if position:
            if trade.trade_type == "buy":
                position.quantity += trade.quantity
                position.available_quantity += trade.quantity
            elif trade.trade_type == "sell":
                position.quantity -= trade.quantity
                position.available_quantity -= trade.quantity

    db.commit()
    db.refresh(db_trade)
    return db_trade


@router.put("/trades/{trade_id}", response_model=TradeResponse)
def update_trade(trade_id: int, trade: TradeUpdate, db: Session = Depends(get_db)):
    db_trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="交易记录不存在")

    update_data = trade.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_trade, key, value)

    db.commit()
    db.refresh(db_trade)
    return db_trade


@router.delete("/trades/{trade_id}")
def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    db_trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="交易记录不存在")

    db.delete(db_trade)
    db.commit()
    return {"message": "交易记录已删除"}


@router.get("/trades/statistics/summary")
def get_trade_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Trade)
    if start_date:
        query = query.filter(Trade.trade_date >= start_date)
    if end_date:
        query = query.filter(Trade.trade_date <= end_date)

    trades = query.all()

    buy_count = sum(1 for t in trades if t.trade_type == "buy")
    sell_count = sum(1 for t in trades if t.trade_type == "sell")
    total_buy_amount = sum(t.amount for t in trades if t.trade_type == "buy")
    total_sell_amount = sum(t.amount for t in trades if t.trade_type == "sell")
    total_fees = sum(t.fee + t.stamp_duty for t in trades)

    return {
        "total_trades": len(trades),
        "buy_count": buy_count,
        "sell_count": sell_count,
        "total_buy_amount": total_buy_amount,
        "total_sell_amount": total_sell_amount,
        "total_fees": total_fees,
        "net_profit": total_sell_amount - total_buy_amount - total_fees
    }
