"""
持仓管理 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date, datetime

from app.services.position_service import PositionService

router = APIRouter(prefix="/api/positions", tags=["持仓管理"])


@router.get("")
def get_positions(
    stock_code: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """获取持仓列表"""
    positions = PositionService.list(
        stock_code=stock_code,
        status=status,
        limit=limit,
        offset=offset
    )

    # 计算市值和盈亏
    result = []
    for p in positions:
        p.market_value = p.quantity * p.current_price
        p.profit_amount = p.quantity * (p.current_price - p.cost_price)
        if p.cost_price > 0:
            p.profit_ratio = (p.current_price - p.cost_price) / p.cost_price
        result.append(p)
    return result


@router.get("/{position_id}")
def get_position(position_id: int):
    """获取单个持仓"""
    position = PositionService.get(position_id)
    if not position:
        raise HTTPException(status_code=404, detail="持仓不存在")
    return position


@router.post("")
def create_position(
    stock_code: str,
    stock_name: Optional[str] = None,
    quantity: int = Query(...),
    cost_price: float = Query(...),
    current_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    opened_at: date = Query(...),
):
    """添加持仓"""
    return PositionService.create(
        stock_code=stock_code,
        stock_name=stock_name,
        quantity=quantity,
        cost_price=cost_price,
        current_price=current_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        opened_at=opened_at,
    )


@router.put("/{position_id}")
def update_position(position_id: int, **kwargs):
    """更新持仓"""
    position = PositionService.update(position_id, **kwargs)
    if not position:
        raise HTTPException(status_code=404, detail="持仓不存在")
    return position


@router.delete("/{position_id}")
def delete_position(position_id: int):
    """删除持仓"""
    success = PositionService.delete(position_id)
    if not success:
        raise HTTPException(status_code=404, detail="持仓不存在")
    return {"status": "deleted", "id": position_id}


@router.put("/{position_id}/stop-loss")
def set_stop_loss(position_id: int, stop_loss: float):
    """设置止损"""
    position = PositionService.set_stop_loss(position_id, stop_loss)
    if not position:
        raise HTTPException(status_code=404, detail="持仓不存在")
    return {"status": "updated", "stop_loss": stop_loss}


@router.put("/{position_id}/take-profit")
def set_take_profit(position_id: int, take_profit: float):
    """设置止盈"""
    position = PositionService.set_take_profit(position_id, take_profit)
    if not position:
        raise HTTPException(status_code=404, detail="持仓不存在")
    return {"status": "updated", "take_profit": take_profit}


@router.post("/{position_id}/close")
def close_position(position_id: int, close_price: float):
    """平仓"""
    position = PositionService.close(position_id, close_price)
    if not position:
        raise HTTPException(status_code=404, detail="持仓不存在")
    return {"status": "closed", "position_id": position_id}


@router.get("/stats/summary")
def get_positions_summary():
    """获取持仓汇总"""
    return PositionService.summary()
