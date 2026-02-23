from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Position, Account

router = APIRouter()


class PositionCreate(BaseModel):
    stock_code: str
    stock_name: str
    quantity: int
    available_quantity: int
    cost_price: float
    current_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    plan_id: Optional[int] = None
    opened_at: date


class PositionUpdate(BaseModel):
    quantity: Optional[int] = None
    available_quantity: Optional[int] = None
    cost_price: Optional[float] = None
    current_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    status: Optional[str] = None


class PositionResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    quantity: int
    available_quantity: int
    cost_price: float
    current_price: Optional[float]
    profit_amount: Optional[float]
    profit_ratio: Optional[float]
    stop_loss_price: Optional[float]
    take_profit_price: Optional[float]
    plan_id: Optional[int]
    status: str
    opened_at: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


def calculate_profit(position: Position) -> tuple:
    if position.current_price is None:
        return None, None
    profit_amount = (position.current_price - position.cost_price) * position.quantity
    profit_ratio = (position.current_price - position.cost_price) / position.cost_price * 100
    return profit_amount, profit_ratio


@router.get("/positions", response_model=List[PositionResponse])
def get_positions(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Position)
    if status:
        query = query.filter(Position.status == status)
    positions = query.order_by(Position.created_at.desc()).all()

    for pos in positions:
        pos.profit_amount, pos.profit_ratio = calculate_profit(pos)

    return positions


@router.get("/positions/{position_id}", response_model=PositionResponse)
def get_position(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="持仓不存在")

    position.profit_amount, position.profit_ratio = calculate_profit(position)
    return position


@router.post("/positions", response_model=PositionResponse)
def create_position(position: PositionCreate, db: Session = Depends(get_db)):
    db_position = Position(**position.model_dump())
    db_position.status = "holding"
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


@router.put("/positions/{position_id}", response_model=PositionResponse)
def update_position(position_id: int, position: PositionUpdate, db: Session = Depends(get_db)):
    db_position = db.query(Position).filter(Position.id == position_id).first()
    if not db_position:
        raise HTTPException(status_code=404, detail="持仓不存在")

    update_data = position.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_position, key, value)

    db_position.updated_at = datetime.now()
    db_position.profit_amount, db_position.profit_ratio = calculate_profit(db_position)

    db.commit()
    db.refresh(db_position)
    return db_position


@router.delete("/positions/{position_id}")
def delete_position(position_id: int, db: Session = Depends(get_db)):
    db_position = db.query(Position).filter(Position.id == position_id).first()
    if not db_position:
        raise HTTPException(status_code=404, detail="持仓不存在")

    db.delete(db_position)
    db.commit()
    return {"message": "持仓已删除"}


@router.post("/positions/{position_id}/close")
def close_position(position_id: int, db: Session = Depends(get_db)):
    db_position = db.query(Position).filter(Position.id == position_id).first()
    if not db_position:
        raise HTTPException(status_code=404, detail="持仓不存在")

    db_position.status = "closed"
    db_position.updated_at = datetime.now()
    db.commit()
    return {"message": "持仓已平仓", "status": db_position.status}


@router.put("/positions/{position_id}/update-price")
def update_position_price(
    position_id: int,
    current_price: float,
    db: Session = Depends(get_db)
):
    db_position = db.query(Position).filter(Position.id == position_id).first()
    if not db_position:
        raise HTTPException(status_code=404, detail="持仓不存在")

    db_position.current_price = current_price
    db_position.profit_amount, db_position.profit_ratio = calculate_profit(db_position)
    db_position.updated_at = datetime.now()
    db.commit()
    return {
        "message": "价格已更新",
        "current_price": current_price,
        "profit_amount": db_position.profit_amount,
        "profit_ratio": db_position.profit_ratio
    }
