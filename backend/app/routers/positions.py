"""
持仓管理 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel
from sqlmodel import Session, select, func

from app.database import engine
from app.models.trading import Position

router = APIRouter(prefix="/api/positions", tags=["持仓管理"])


class PositionCreate(BaseModel):
    stock_code: str
    stock_name: Optional[str] = None
    quantity: int
    cost_price: float
    current_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: date


class PositionUpdate(BaseModel):
    stock_name: Optional[str] = None
    quantity: Optional[int] = None
    current_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: Optional[str] = None


class PositionResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: Optional[str]
    quantity: int
    available_quantity: int
    cost_price: float
    current_price: float
    market_value: float
    profit_amount: float
    profit_ratio: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    status: str
    opened_at: date
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=List[PositionResponse])
def get_positions(
    stock_code: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """获取持仓列表"""
    with Session(engine) as session:
        query = select(Position)
        if stock_code:
            query = query.where(Position.stock_code == stock_code)
        if status:
            query = query.where(Position.status == status)
        query = query.order_by(Position.created_at.desc()).offset(offset).limit(limit)
        positions = session.exec(query).all()

        # 计算市值和盈亏
        result = []
        for p in positions:
            p.market_value = p.quantity * p.current_price
            p.profit_amount = p.quantity * (p.current_price - p.cost_price)
            if p.cost_price > 0:
                p.profit_ratio = (p.current_price - p.cost_price) / p.cost_price
            result.append(p)
        return result


@router.get("/{position_id}", response_model=PositionResponse)
def get_position(position_id: int):
    """获取单个持仓"""
    with Session(engine) as session:
        position = session.get(Position, position_id)
        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")
        return position


@router.post("", response_model=PositionResponse)
def create_position(position: PositionCreate):
    """添加持仓"""
    with Session(engine) as session:
        db_position = Position(
            **position.model_dump(),
            available_quantity=position.quantity,
            market_value=position.quantity * (position.current_price or position.cost_price),
            profit_amount=position.quantity * ((position.current_price or 0) - position.cost_price),
        )
        if position.current_price and position.cost_price > 0:
            db_position.profit_ratio = (position.current_price - position.cost_price) / position.cost_price

        session.add(db_position)
        session.commit()
        session.refresh(db_position)
        return db_position


@router.put("/{position_id}", response_model=PositionResponse)
def update_position(position_id: int, position: PositionUpdate):
    """更新持仓"""
    with Session(engine) as session:
        db_position = session.get(Position, position_id)
        if not db_position:
            raise HTTPException(status_code=404, detail="持仓不存在")

        update_data = position.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_position, key, value)

        db_position.updated_at = datetime.now()
        session.add(db_position)
        session.commit()
        session.refresh(db_position)
        return db_position


@router.delete("/{position_id}")
def delete_position(position_id: int):
    """删除持仓"""
    with Session(engine) as session:
        position = session.get(Position, position_id)
        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")
        session.delete(position)
        session.commit()
        return {"status": "deleted", "id": position_id}


@router.put("/{position_id}/stop-loss")
def set_stop_loss(position_id: int, stop_loss: float):
    """设置止损"""
    with Session(engine) as session:
        position = session.get(Position, position_id)
        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")
        position.stop_loss = stop_loss
        position.updated_at = datetime.now()
        session.add(position)
        session.commit()
        return {"status": "updated", "stop_loss": stop_loss}


@router.put("/{position_id}/take-profit")
def set_take_profit(position_id: int, take_profit: float):
    """设置止盈"""
    with Session(engine) as session:
        position = session.get(Position, position_id)
        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")
        position.take_profit = take_profit
        position.updated_at = datetime.now()
        session.add(position)
        session.commit()
        return {"status": "updated", "take_profit": take_profit}


@router.post("/{position_id}/close")
def close_position(position_id: int, close_price: float):
    """平仓"""
    with Session(engine) as session:
        position = session.get(Position, position_id)
        if not position:
            raise HTTPException(status_code=404, detail="持仓不存在")

        position.status = "sold"
        position.current_price = close_price
        position.profit_amount = position.quantity * (close_price - position.cost_price)
        if position.cost_price > 0:
            position.profit_ratio = (close_price - position.cost_price) / position.cost_price

        position.updated_at = datetime.now()
        session.add(position)
        session.commit()
        return {"status": "closed", "position_id": position_id}


@router.get("/stats/summary")
def get_positions_summary():
    """获取持仓汇总"""
    with Session(engine) as session:
        positions = session.exec(select(Position).where(Position.status == "holding")).all()

        total_value = sum(p.quantity * p.current_price for p in positions)
        total_cost = sum(p.quantity * p.cost_price for p in positions)
        total_profit = total_value - total_cost
        profit_ratio = (total_profit / total_cost * 100) if total_cost > 0 else 0

        return {
            "total_positions": len(positions),
            "total_value": total_value,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "profit_ratio": profit_ratio,
        }
