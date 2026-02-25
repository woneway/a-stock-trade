from typing import Optional, List
from sqlmodel import Session, select
from app.models.stock import Stock


class StockService:
    """股票服务"""

    @staticmethod
    def get_all(session: Session, limit: int = 100) -> List[Stock]:
        """获取所有股票"""
        return session.exec(select(Stock).limit(limit)).all()

    @staticmethod
    def get_by_code(session: Session, code: str) -> Optional[Stock]:
        """根据代码获取股票"""
        return session.exec(select(Stock).where(Stock.code == code)).first()

    @staticmethod
    def search(session: Session, keyword: str) -> List[Stock]:
        """搜索股票"""
        return session.exec(
            select(Stock).where(
                (Stock.name.contains(keyword)) | (Stock.code.contains(keyword))
            ).limit(20)
        ).all()

    @staticmethod
    def get_by_sector(session: Session, sector: str) -> List[Stock]:
        """根据板块获取股票"""
        return session.exec(
            select(Stock).where(Stock.sector == sector)
        ).all()

    @staticmethod
    def get_limit_up_stocks(session: Session) -> List[Stock]:
        """获取涨停股票"""
        return session.exec(
            select(Stock).where(Stock.is_limit_up == True)
        ).all()
