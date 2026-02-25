from typing import Optional, List
from sqlmodel import Session, select
from app.models.position import Position


class PositionService:
    """持仓服务"""

    @staticmethod
    def get_all(session: Session) -> List[Position]:
        """获取所有持仓"""
        return session.exec(select(Position)).all()

    @staticmethod
    def get_active(session: Session) -> List[Position]:
        """获取活跃持仓"""
        return session.exec(
            select(Position).where(Position.status == "open")
        ).all()

    @staticmethod
    def get_by_id(session: Session, position_id: int) -> Optional[Position]:
        """根据ID获取持仓"""
        return session.exec(
            select(Position).where(Position.id == position_id)
        ).first()

    @staticmethod
    def get_by_stock(session: Session, stock_code: str) -> List[Position]:
        """获取指定股票的持仓"""
        return session.exec(
            select(Position).where(Position.stock_code == stock_code)
        ).all()

    @staticmethod
    def get_by_strategy(session: Session, strategy_id: int) -> List[Position]:
        """获取指定策略的持仓"""
        return session.exec(
            select(Position).where(Position.strategy_id == strategy_id)
        ).all()

    @staticmethod
    def calculate_total_value(session: Session) -> float:
        """计算总持仓市值"""
        positions = PositionService.get_active(session)
        return sum(p.market_value or 0 for p in positions)

    @staticmethod
    def calculate_total_pnl(session: Session) -> float:
        """计算总盈亏"""
        positions = PositionService.get_active(session)
        return sum(p.pnl or 0 for p in positions)
