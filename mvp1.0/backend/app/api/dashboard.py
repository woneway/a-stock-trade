from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models.models import TradingPlan, Position, Account, RiskConfig, NotificationConfig, AppConfig, Trade

router = APIRouter()


@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    account = db.query(Account).first()
    if not account:
        account = Account()
        db.add(account)
        db.commit()
        db.refresh(account)

    positions = db.query(Position).filter(Position.status == "holding").all()

    return {
        "total_assets": account.total_assets,
        "available_cash": account.available_cash,
        "market_value": account.market_value,
        "today_profit": account.today_profit,
        "today_profit_ratio": account.today_profit_ratio,
        "total_profit": account.total_profit,
        "total_profit_ratio": account.total_profit_ratio,
        "position_count": len(positions)
    }


@router.get("/dashboard/today-plans")
def get_today_plans(db: Session = Depends(get_db)):
    today = date.today()
    plans = db.query(TradingPlan).filter(TradingPlan.plan_date == today).all()
    return {"plans": plans}


@router.get("/dashboard/positions-summary")
def get_positions_summary(db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.status == "holding").all()
    return {
        "positions": [
            {
                "id": p.id,
                "stock_code": p.stock_code,
                "stock_name": p.stock_name,
                "profit_amount": p.profit_amount,
                "profit_ratio": p.profit_ratio,
                "stop_loss_price": p.stop_loss_price,
                "is_stop_loss": p.current_price and p.stop_loss_price and p.current_price <= p.stop_loss_price
            }
            for p in positions
        ]
    }


@router.get("/dashboard/signals")
def get_signals(db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.status == "holding").all()
    signals = []

    for p in positions:
        if p.current_price and p.stop_loss_price and p.current_price <= p.stop_loss_price:
            signals.append({
                "type": "stop_loss",
                "message": f"{p.stock_name}触及止损价{p.stop_loss_price}元",
                "stock_code": p.stock_code
            })
        if p.current_price and p.take_profit_price and p.current_price >= p.take_profit_price:
            signals.append({
                "type": "take_profit",
                "message": f"{p.stock_name}触发止盈条件{p.take_profit_price}元",
                "stock_code": p.stock_code
            })

    return {"signals": signals}
