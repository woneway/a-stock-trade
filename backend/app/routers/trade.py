from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List
from datetime import date

from app.database import engine
from app.models.trade import Trade
from app.models.plan import PrePlan
from app.schemas.trade import TradeCreate, TradeResponse, TradeSummary


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/trades", tags=["trades"])


def _convert_action(action: str) -> str:
    if action == "buy":
        return "买入"
    elif action == "sell":
        return "卖出"
    return action


def _convert_to_action(trade_type: str) -> str:
    if trade_type == "买入":
        return "buy"
    elif trade_type == "卖出":
        return "sell"
    return trade_type


@router.get("", response_model=List[TradeResponse])
def get_trades(db: Session = Depends(get_db), trade_date: date = None):
    statement = select(Trade).order_by(Trade.trade_date.desc())
    if trade_date:
        statement = statement.where(Trade.trade_date == trade_date)
    results = db.exec(statement).all()
    return [
        TradeResponse(
            stock_code=t.code,
            stock_name=t.name,
            trade_type=_convert_action(t.action),
            price=t.price,
            quantity=t.quantity,
            amount=t.amount,
            fee=t.fee,
            reason=t.reason,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            pnl=t.pnl,
            pnl_percent=t.pnl_percent,
            trade_date=t.trade_date,
            id=t.id,
            pre_plan_id=t.pre_plan_id,
            is_planned=t.is_planned,
            plan_target_price=t.plan_target_price,
        )
        for t in results
    ]


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
        action=_convert_to_action(item.trade_type),
        price=item.price,
        quantity=item.quantity,
        amount=item.amount,
        fee=item.fee,
        reason=item.reason,
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
    return TradeResponse(
        stock_code=db_item.code,
        stock_name=db_item.name,
        trade_type=_convert_action(db_item.action),
        price=db_item.price,
        quantity=db_item.quantity,
        amount=db_item.amount,
        fee=db_item.fee,
        reason=db_item.reason,
        entry_price=db_item.entry_price,
        exit_price=db_item.exit_price,
        pnl=db_item.pnl,
        pnl_percent=db_item.pnl_percent,
        trade_date=db_item.trade_date,
        id=db_item.id,
        pre_plan_id=db_item.pre_plan_id,
        is_planned=db_item.is_planned,
        plan_target_price=db_item.plan_target_price,
    )


@router.get("/summary", response_model=TradeSummary)
def get_trade_summary(db: Session = Depends(get_db), trade_date: date = None):
    statement = select(Trade)
    if trade_date:
        statement = statement.where(Trade.trade_date == trade_date)

    trades = db.exec(statement).all()

    total_trades = len(trades)
    total_fee = sum(t.fee for t in trades)
    total_pnl = sum(t.pnl if t.pnl else 0 for t in trades)

    return TradeSummary(
        total_trades=total_trades,
        total_fee=total_fee,
        total_pnl=total_pnl,
    )


@router.get("/{item_id}", response_model=TradeResponse)
def get_trade(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Trade, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Trade not found")
    return TradeResponse(
        stock_code=item.code,
        stock_name=item.name,
        trade_type=_convert_action(item.action),
        price=item.price,
        quantity=item.quantity,
        amount=item.amount,
        fee=item.fee,
        reason=item.reason,
        entry_price=item.entry_price,
        exit_price=item.exit_price,
        pnl=item.pnl,
        pnl_percent=item.pnl_percent,
        trade_date=item.trade_date,
        id=item.id,
        pre_plan_id=item.pre_plan_id,
        is_planned=item.is_planned,
        plan_target_price=item.plan_target_price,
    )
