from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date

from app.database import engine
from app.models.trade import Trade
from app.models.plan import PrePlan
from app.models.position import Position
from app.schemas.trade import TradeCreate, TradeResponse, TradeSummary
from app.services.trade_service import TradeService


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.get("", response_model=List[TradeResponse])
def get_trades(db: Session = Depends(get_db), trade_date: date = None):
    statement = select(Trade).order_by(Trade.trade_date.desc())
    if trade_date:
        statement = statement.where(Trade.trade_date == trade_date)
    results = db.exec(statement).all()
    return [TradeService.to_response(t) for t in results]


@router.post("", response_model=TradeResponse)
def create_trade(item: TradeCreate, db: Session = Depends(get_db)):
    pre_plan_id = item.pre_plan_id
    is_planned = False

    if pre_plan_id:
        pre_plan = db.get(PrePlan, pre_plan_id)
        if pre_plan and pre_plan.target_stocks:
            planned_stocks = [s.strip() for s in pre_plan.target_stocks.split(",") if s.strip()]
            if item.stock_code in planned_stocks:
                is_planned = True

    db_item = Trade(
        code=item.stock_code,
        name=item.stock_name,
        action=TradeService.convert_to_action(item.trade_type),
        price=item.price,
        quantity=item.quantity,
        amount=item.amount,
        fee=item.fee,
        reason=item.reason,
        trade_time=item.trade_time,
        entry_price=item.entry_price,
        exit_price=item.exit_price,
        pnl=item.pnl,
        pnl_percent=item.pnl_percent,
        trade_date=item.trade_date,
        pre_plan_id=pre_plan_id,
        is_planned=is_planned,
        plan_target_price=item.plan_target_price,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # 自动更新持仓
    if db_item.action == "buy":
        statement = select(Position).where(
            Position.code == item.stock_code,
            Position.status == "holding"
        )
        existing_positions = db.exec(statement).all()
        if existing_positions:
            pos = existing_positions[0]
            total_quantity = pos.quantity + item.quantity
            new_avg_cost = (pos.avg_cost * pos.quantity + item.price * item.quantity) / total_quantity
            pos.quantity = total_quantity
            pos.avg_cost = new_avg_cost
            pos.current_price = item.price
            pos.updated_at = date.today()
        else:
            new_position = Position(
                code=item.stock_code,
                name=item.stock_name,
                quantity=item.quantity,
                avg_cost=item.price,
                current_price=item.price,
                market_value=item.price * item.quantity,
                status="holding",
                entry_date=item.trade_date,
            )
            db.add(new_position)
        db.commit()
    elif db_item.action == "sell":
        statement = select(Position).where(
            Position.code == item.stock_code,
            Position.status == "holding"
        )
        existing_positions = db.exec(statement).all()
        if existing_positions:
            pos = existing_positions[0]
            pos.quantity = pos.quantity - item.quantity
            pos.current_price = item.price
            pos.updated_at = date.today()
            if pos.quantity <= 0:
                pos.status = "closed"
                pos.quantity = 0
            db.commit()

    return TradeService.to_response(db_item)


@router.get("/summary", response_model=TradeSummary)
def get_trade_summary(db: Session = Depends(get_db), start_date: date = None, end_date: date = None):
    statement = select(Trade)
    if start_date:
        statement = statement.where(Trade.trade_date >= start_date)
    if end_date:
        statement = statement.where(Trade.trade_date <= end_date)

    trades = db.exec(statement).all()
    return TradeService.calculate_summary(trades)


@router.get("/{item_id}", response_model=TradeResponse)
def get_trade(item_id: int, db: Session = Depends(get_db)):
    item = TradeService.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Trade not found")
    return TradeService.to_response(item)
