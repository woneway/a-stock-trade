"""
成交记录 Service
"""
from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Session, select

from app.database import engine
from app.models.trading import Trade


class TradeService:
    """成交记录服务"""

    @staticmethod
    def list(
        stock_code: Optional[str] = None,
        trade_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Trade]:
        """获取成交记录列表"""
        with Session(engine) as session:
            query = select(Trade)
            if stock_code:
                query = query.where(Trade.stock_code == stock_code)
            if trade_type:
                query = query.where(Trade.trade_type == trade_type)
            if start_date:
                query = query.where(Trade.trade_date >= start_date)
            if end_date:
                query = query.where(Trade.trade_date <= end_date)

            query = query.order_by(Trade.trade_date.desc(), Trade.trade_time.desc()).offset(offset).limit(limit)
            return session.exec(query).all()

    @staticmethod
    def get(trade_id: int) -> Optional[Trade]:
        """获取单条成交记录"""
        with Session(engine) as session:
            return session.get(Trade, trade_id)

    @staticmethod
    def create(
        stock_code: str,
        stock_name: Optional[str],
        trade_type: str,
        price: float,
        quantity: int,
        amount: float,
        fee: float,
        trade_date: date,
        trade_time: Optional[datetime],
        order_id: Optional[int],
        position_id: Optional[int],
        pnl: Optional[float],
        pnl_percent: Optional[float],
        notes: Optional[str]
    ) -> Trade:
        """记录成交"""
        with Session(engine) as session:
            db_trade = Trade(
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
            session.add(db_trade)
            session.commit()
            session.refresh(db_trade)
            return db_trade

    @staticmethod
    def summary(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """获取成交统计"""
        with Session(engine) as session:
            query = select(Trade)
            if start_date:
                query = query.where(Trade.trade_date >= start_date)
            if end_date:
                query = query.where(Trade.trade_date <= end_date)

            trades = session.exec(query).all()

            buy_count = sum(1 for t in trades if t.trade_type == "buy")
            sell_count = sum(1 for t in trades if t.trade_type == "sell")
            buy_amount = sum(t.amount for t in trades if t.trade_type == "buy")
            sell_amount = sum(t.amount for t in trades if t.trade_type == "sell")
            total_fee = sum(t.fee for t in trades)
            total_pnl = sum(t.pnl or 0 for t in trades)

            return {
                "total_trades": len(trades),
                "buy_count": buy_count,
                "sell_count": sell_count,
                "buy_amount": buy_amount,
                "sell_amount": sell_amount,
                "total_fee": total_fee,
                "total_pnl": total_pnl,
            }
