"""
成交记录 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel
from sqlmodel import Session, select, func

from app.database import engine
from app.models.trading import Trade

router = APIRouter(prefix="/api/trades", tags=["成交记录"])


class TradeCreate(BaseModel):
    stock_code: str
    stock_name: Optional[str] = None
    trade_type: str  # buy/sell
    price: float
    quantity: int
    amount: float
    fee: float = 0
    trade_date: date
    trade_time: Optional[datetime] = None
    order_id: Optional[int] = None
    position_id: Optional[int] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    notes: Optional[str] = None


class TradeResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: Optional[str]
    trade_type: str
    price: float
    quantity: int
    amount: float
    fee: float
    trade_date: date
    trade_time: Optional[datetime]
    order_id: Optional[int]
    position_id: Optional[int]
    pnl: Optional[float]
    pnl_percent: Optional[float]
    notes: Optional[str]
    created_at: datetime


@router.get("", response_model=List[TradeResponse])
def get_trades(
    stock_code: Optional[str] = None,
    trade_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
):
    """获取成交记录列表"""
    with Session(engine) as session:
        query = select(Trade)
        if stock_code:
            query = query.where(Trade.stock_code == stock_code)
        if trade_type:
            query = query.where(Trade.trade_type == trade_type)
        if start_date:
            query = query.where(Trade.trade_date >= start_date)
        if end_date:
            query = query.where(Trade.trade_date <= end_date)

        query = query.order_by(Trade.trade_date.desc(), Trade.trade_time.desc()).offset(offset).limit(limit)
        return session.exec(query).all()


@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade(trade_id: int):
    """获取单条成交记录"""
    with Session(engine) as session:
        trade = session.get(Trade, trade_id)
        if not trade:
            raise HTTPException(status_code=404, detail="成交记录不存在")
        return trade


@router.post("", response_model=TradeResponse)
def create_trade(trade: TradeCreate):
    """记录成交"""
    with Session(engine) as session:
        db_trade = Trade(**trade.model_dump())
        session.add(db_trade)
        session.commit()
        session.refresh(db_trade)
        return db_trade


@router.get("/stats/summary")
def get_trades_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """获取成交统计"""
    with Session(engine) as session:
        query = select(Trade)
        if start_date:
            query = query.where(Trade.trade_date >= start_date)
        if end_date:
            query = query.where(Trade.trade_date <= end_date)

        trades = session.exec(query).all()

        buy_count = sum(1 for t in trades if t.trade_type == "buy")
        sell_count = sum(1 for t in trades if t.trade_type == "sell")
        buy_amount = sum(t.amount for t in trades if t.trade_type == "buy")
        sell_amount = sum(t.amount for t in trades if t.trade_type == "sell")
        total_fee = sum(t.fee for t in trades)
        total_pnl = sum(t.pnl or 0 for t in trades)

        return {
            "total_trades": len(trades),
            "buy_count": buy_count,
            "sell_count": sell_count,
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "total_fee": total_fee,
            "total_pnl": total_pnl,
        }
