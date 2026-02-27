"""
成交记录 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, datetime

from app.services.trade_service import TradeService

router = APIRouter(prefix="/api/trades", tags=["成交记录"])


@router.get("")
def get_trades(
    stock_code: Optional[str] = None,
    trade_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100,
    offset: int = 0,
):
    """获取成交记录列表"""
    return TradeService.list(
        stock_code=stock_code,
        trade_type=trade_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@router.get("/{trade_id}")
def get_trade(trade_id: int):
    """获取单条成交记录"""
    trade = TradeService.get(trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail="成交记录不存在")
    return trade


@router.post("")
def create_trade(
    stock_code: str,
    stock_name: Optional[str] = None,
    trade_type: str = Query(...),
    price: float = Query(...),
    quantity: int = Query(...),
    amount: float = Query(...),
    fee: float = 0,
    trade_date: date = Query(...),
    trade_time: Optional[datetime] = None,
    order_id: Optional[int] = None,
    position_id: Optional[int] = None,
    pnl: Optional[float] = None,
    pnl_percent: Optional[float] = None,
    notes: Optional[str] = None,
):
    """记录成交"""
    return TradeService.create(
        stock_code=stock_code,
        stock_name=stock_name,
        trade_type=trade_type,
        price=price,
        quantity=quantity,
        amount=amount,
        fee=fee,
        trade_date=trade_date,
        trade_time=trade_time,
        order_id=order_id,
        position_id=position_id,
        pnl=pnl,
        pnl_percent=pnl_percent,
        notes=notes,
    )


@router.get("/stats/summary")
def get_trades_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """获取成交统计"""
    return TradeService.summary(start_date=start_date, end_date=end_date)
