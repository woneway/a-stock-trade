from typing import Optional, List
from sqlmodel import Session, select
from app.models.strategy import Strategy


class StrategyService:
    """策略服务"""

    @staticmethod
    def get_all(session: Session) -> List[Strategy]:
        """获取所有策略"""
        return session.exec(select(Strategy)).all()

    @staticmethod
    def get_active(session: Session) -> List[Strategy]:
        """获取活跃策略"""
        return session.exec(
            select(Strategy).where(Strategy.is_active == True)
        ).all()

    @staticmethod
    def get_by_id(session: Session, strategy_id: int) -> Optional[Strategy]:
        """根据ID获取策略"""
        return session.exec(
            select(Strategy).where(Strategy.id == strategy_id)
        ).first()

    @staticmethod
    def get_by_name(session: Session, name: str) -> Optional[Strategy]:
        """根据名称获取策略"""
        return session.exec(
            select(Strategy).where(Strategy.name == name)
        ).first()

    @staticmethod
    def get_by_trade_mode(session: Session, trade_mode: str) -> List[Strategy]:
        """根据交易模式获取策略"""
        return session.exec(
            select(Strategy).where(Strategy.trade_mode == trade_mode)
        ).all()

    @staticmethod
    def search(session: Session, keyword: str) -> List[Strategy]:
        """搜索策略"""
        return session.exec(
            select(Strategy).where(Strategy.name.contains(keyword))
        ).all()
