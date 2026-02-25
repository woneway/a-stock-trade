from typing import Optional, List
from datetime import date
from sqlmodel import Session, select, func
from app.models.trade import Trade


class TradeService:
    """交易服务"""

    @staticmethod
    def get_all(session: Session, limit: int = 100) -> List[Trade]:
        """获取所有交易记录"""
        return session.exec(select(Trade).limit(limit)).all()

    @staticmethod
    def get_by_id(session: Session, trade_id: int) -> Optional[Trade]:
        """根据ID获取交易记录"""
        return session.exec(select(Trade).where(Trade.id == trade_id)).first()

    @staticmethod
    def get_by_date(session: Session, trade_date: date) -> List[Trade]:
        """获取指定日期的交易记录"""
        return session.exec(
            select(Trade).where(Trade.trade_date == trade_date)
        ).all()

    @staticmethod
    def get_by_position(session: Session, position_id: int) -> List[Trade]:
        """获取指定持仓的交易记录"""
        return session.exec(
            select(Trade).where(Trade.position_id == position_id)
        ).all()

    @staticmethod
    def get_summary(session: Session) -> dict:
        """获取交易统计"""
        total_trades = session.exec(select(func.count(Trade.id))).first() or 0
        total_buy = session.exec(
            select(func.count(Trade.id)).where(Trade.trade_type == "buy")
        ).first() or 0
        total_sell = session.exec(
            select(func.count(Trade.id)).where(Trade.trade_type == "sell")
        ).first() or 0

        return {
            "total_trades": total_trades,
            "total_buy": total_buy,
            "total_sell": total_sell,
        }

    @staticmethod
    def calculate_pnl(session: Session, trade_date: date = None) -> float:
        """计算盈亏"""
        query = select(Trade)
        if trade_date:
            query = query.where(Trade.trade_date == trade_date)

        trades = session.exec(query).all()
        total_pnl = sum(t.pnl or 0 for t in trades)
        return total_pnl
