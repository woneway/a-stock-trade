from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from datetime import date

from app.database import engine
from app.models.position import Position
from app.models.trade import Trade
from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse
from app.services.position_service import PositionService


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/positions", tags=["positions"])


@router.get("", response_model=List[PositionResponse])
def get_positions(db: Session = Depends(get_db), status: str = None):
    statement = select(Position).order_by(Position.entry_date.desc())
    if status:
        statement = statement.where(Position.status == status)
    results = db.exec(statement).all()

    # 合并相同股票代码的持仓
    position_map = {}
    for p in results:
        key = (p.code, p.avg_cost)
        if key in position_map:
            existing = position_map[key]
            existing.quantity += p.quantity
            existing.avg_cost = (existing.avg_cost * existing.quantity + p.avg_cost * p.quantity) / (existing.quantity + p.quantity)
        else:
            position_map[key] = p

    return [PositionService.to_response(p) for p in position_map.values()]


@router.post("", response_model=PositionResponse)
def create_position(item: PositionCreate, db: Session = Depends(get_db)):
    db_item = Position(
        code=item.stock_code,
        name=item.stock_name,
        quantity=item.quantity,
        avg_cost=item.cost_price,
        current_price=item.current_price,
        market_value=item.market_value,
        profit_loss=item.profit_amount,
        profit_ratio=item.profit_ratio,
        status=item.status,
        entry_date=item.opened_at,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # 自动创建交易记录
    PositionService.create_trade(db, db_item, '买入', item.cost_price)

    return PositionService.to_response(db_item)


@router.get("/{item_id}", response_model=PositionResponse)
def get_position(item_id: int, db: Session = Depends(get_db)):
    item = PositionService.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    return PositionService.to_response(item)


@router.put("/{item_id}", response_model=PositionResponse)
def update_position(item_id: int, item: PositionUpdate, db: Session = Depends(get_db)):
    db_item = PositionService.get_by_id(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Position not found")

    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)

    PositionService.update_position(db, db_item)
    return PositionService.to_response(db_item)


@router.delete("/{item_id}")
def delete_position(item_id: int, db: Session = Depends(get_db)):
    if not PositionService.delete_position(db, item_id):
        raise HTTPException(status_code=404, detail="Position not found")
    return {"ok": True}


@router.post("/{item_id}/close")
def close_position(item_id: int, db: Session = Depends(get_db)):
    item = PositionService.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")

    current_price = item.current_price if item.current_price and item.current_price > 0 else item.avg_cost

    # 自动创建卖出交易记录
    PositionService.create_trade(db, item, '卖出', current_price)

    # 更新持仓状态
    item.status = "closed"
    PositionService.update_position(db, item)

    return PositionService.to_response(item)
