from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date

from app.database import engine
from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse


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
    
    position_map = {}
    for p in results:
        key = (p.code, p.avg_cost)
        if key in position_map:
            existing = position_map[key]
            existing.quantity += p.quantity
            existing.avg_cost = (existing.avg_cost * existing.quantity + p.avg_cost * p.quantity) / (existing.quantity + p.quantity)
        else:
            position_map[key] = p
    
    positions = []
    for p in position_map.values():
        if p.status and status and p.status != status:
            continue
        current_price = p.current_price if p.current_price and p.current_price > 0 else p.avg_cost
        market_value = p.quantity * current_price
        profit_loss = (current_price - p.avg_cost) * p.quantity
        profit_ratio = ((current_price - p.avg_cost) / p.avg_cost * 100) if p.avg_cost > 0 else 0
        positions.append(PositionResponse(
            stock_code=p.code,
            stock_name=p.name,
            quantity=p.quantity,
            available_quantity=p.quantity,
            cost_price=p.avg_cost,
            current_price=current_price,
            market_value=market_value,
            profit_amount=profit_loss,
            profit_ratio=profit_ratio,
            status=p.status,
            opened_at=p.entry_date,
            id=p.id,
            created_at=p.created_at,
            updated_at=p.updated_at,
            sell_target=p.sell_target,
            stop_loss=p.stop_loss,
            trade_plan=p.trade_plan,
            holding_reason=p.holding_reason,
        ))
    return positions


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
    return PositionResponse(
        stock_code=db_item.code,
        stock_name=db_item.name,
        quantity=db_item.quantity,
        available_quantity=db_item.quantity,
        cost_price=db_item.avg_cost,
        current_price=db_item.current_price,
        market_value=db_item.market_value,
        profit_amount=db_item.profit_loss,
        profit_ratio=db_item.profit_ratio,
        status=db_item.status,
        opened_at=db_item.entry_date,
        id=db_item.id,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at,
        sell_target=db_item.sell_target,
        stop_loss=db_item.stop_loss,
        trade_plan=db_item.trade_plan,
        holding_reason=db_item.holding_reason,
    )


@router.get("/{item_id}", response_model=PositionResponse)
def get_position(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Position, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    current_price = item.current_price if item.current_price and item.current_price > 0 else item.avg_cost
    market_value = item.quantity * current_price
    profit_loss = (current_price - item.avg_cost) * item.quantity
    profit_ratio = ((current_price - item.avg_cost) / item.avg_cost * 100) if item.avg_cost > 0 else 0
    return PositionResponse(
        stock_code=item.code,
        stock_name=item.name,
        quantity=item.quantity,
        available_quantity=item.quantity,
        cost_price=item.avg_cost,
        current_price=current_price,
        market_value=market_value,
        profit_amount=profit_loss,
        profit_ratio=profit_ratio,
        status=item.status,
        opened_at=item.entry_date,
        id=item.id,
        created_at=item.created_at,
        updated_at=item.updated_at,
        sell_target=item.sell_target,
        stop_loss=item.stop_loss,
        trade_plan=item.trade_plan,
        holding_reason=item.holding_reason,
    )


@router.put("/{item_id}", response_model=PositionResponse)
def update_position(item_id: int, item: PositionUpdate, db: Session = Depends(get_db)):
    db_item = db.get(Position, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Position not found")

    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    db_item.updated_at = date.today()

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    current_price = db_item.current_price if db_item.current_price and db_item.current_price > 0 else db_item.avg_cost
    market_value = db_item.quantity * current_price
    profit_loss = (current_price - db_item.avg_cost) * db_item.quantity
    profit_ratio = ((current_price - db_item.avg_cost) / db_item.avg_cost * 100) if db_item.avg_cost > 0 else 0
    return PositionResponse(
        stock_code=db_item.code,
        stock_name=db_item.name,
        quantity=db_item.quantity,
        available_quantity=db_item.quantity,
        cost_price=db_item.avg_cost,
        current_price=current_price,
        market_value=market_value,
        profit_amount=profit_loss,
        profit_ratio=profit_ratio,
        status=db_item.status,
        opened_at=db_item.entry_date,
        id=db_item.id,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at,
        sell_target=db_item.sell_target,
        stop_loss=db_item.stop_loss,
        trade_plan=db_item.trade_plan,
        holding_reason=db_item.holding_reason,
    )


@router.delete("/{item_id}")
def delete_position(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Position, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(item)
    db.commit()
    return {"ok": True}


@router.post("/{item_id}/close")
def close_position(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Position, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Position not found")
    item.status = "closed"
    item.updated_at = date.today()
    db.add(item)
    db.commit()
    db.refresh(item)
    current_price = item.current_price if item.current_price and item.current_price > 0 else item.avg_cost
    market_value = item.quantity * current_price
    profit_loss = (current_price - item.avg_cost) * item.quantity
    profit_ratio = ((current_price - item.avg_cost) / item.avg_cost * 100) if item.avg_cost > 0 else 0
    return PositionResponse(
        stock_code=item.code,
        stock_name=item.name,
        quantity=item.quantity,
        available_quantity=item.quantity,
        cost_price=item.avg_cost,
        current_price=current_price,
        market_value=market_value,
        profit_amount=profit_loss,
        profit_ratio=profit_ratio,
        status=item.status,
        opened_at=item.entry_date,
        id=item.id,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
