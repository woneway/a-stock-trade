"""
策略信号 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import engine
from app.models.trading import StrategySignal

router = APIRouter(prefix="/api/signals", tags=["策略信号"])


class SignalCreate(BaseModel):
    strategy_id: int
    stock_code: str
    stock_name: Optional[str] = None
    signal_type: str  # buy/sell/hold
    signal_strength: float = 0
    confidence: float = 0
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    reason: Optional[str] = None


class SignalResponse(BaseModel):
    id: int
    strategy_id: int
    stock_code: str
    stock_name: Optional[str]
    signal_type: str
    signal_strength: float
    confidence: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    reason: Optional[str]
    created_at: datetime


@router.get("", response_model=List[SignalResponse])
def get_signals(
    strategy_id: Optional[int] = None,
    stock_code: Optional[str] = None,
    signal_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """获取信号列表"""
    with Session(engine) as session:
        query = select(StrategySignal)
        if strategy_id:
            query = query.where(StrategySignal.strategy_id == strategy_id)
        if stock_code:
            query = query.where(StrategySignal.stock_code == stock_code)
        if signal_type:
            query = query.where(StrategySignal.signal_type == signal_type)
        query = query.order_by(StrategySignal.created_at.desc()).offset(offset).limit(limit)
        return session.exec(query).all()


@router.get("/{signal_id}", response_model=SignalResponse)
def get_signal(signal_id: int):
    """获取单个信号"""
    with Session(engine) as session:
        signal = session.get(StrategySignal, signal_id)
        if not signal:
            raise HTTPException(status_code=404, detail="信号不存在")
        return signal


@router.post("", response_model=SignalResponse)
def create_signal(signal: SignalCreate):
    """创建信号"""
    with Session(engine) as session:
        db_signal = StrategySignal(**signal.model_dump())
        session.add(db_signal)
        session.commit()
        session.refresh(db_signal)
        return db_signal


@router.delete("/{signal_id}")
def delete_signal(signal_id: int):
    """删除信号"""
    with Session(engine) as session:
        signal = session.get(StrategySignal, signal_id)
        if not signal:
            raise HTTPException(status_code=404, detail="信号不存在")
        session.delete(signal)
        session.commit()
        return {"status": "deleted", "id": signal_id}
