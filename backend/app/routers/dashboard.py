from fastapi import APIRouter
from sqlmodel import Session, select, func
from datetime import date

from app.database import engine
from app.models.trade import Trade
from app.models.position import Position
from app.models.plan import PrePlan, PostReview
from app.models.watch_stock import WatchStock


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary():
    with Session(engine) as db:
        today = date.today()
        
        plans_count = db.exec(select(func.count(PrePlan.id)).where(PrePlan.trade_date == today)).first() or 0
        
        positions_count = db.exec(select(func.count(Position.id)).where(Position.status == "holding")).first() or 0
        
        trades_today = db.exec(select(Trade).where(Trade.trade_date == today)).all()
        trades_count = len(trades_today)
        
        win_count = 0
        total_pnl = 0
        for t in trades_today:
            if t.pnl and t.pnl > 0:
                win_count += 1
            total_pnl += t.pnl if t.pnl else 0
        
        win_rate = (win_count / trades_count * 100) if trades_count > 0 else 0
        
        return {
            "today_plans": plans_count,
            "positions": positions_count,
            "today_trades": trades_count,
            "win_rate": round(win_rate, 2),
            "total_pnl": total_pnl,
            "date": today.isoformat(),
        }
