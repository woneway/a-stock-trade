from typing import Optional, List
from datetime import date
from sqlmodel import Session, select
from app.models.plan import PrePlan, PostReview, HistoricalPlan


class PlanService:
    """计划服务"""

    @staticmethod
    def get_pre_plan(session: Session, trade_date: date) -> Optional[PrePlan]:
        """获取盘前计划"""
        return session.exec(
            select(PrePlan).where(
                PrePlan.trade_date == trade_date
            )
        ).first()

    @staticmethod
    def get_post_plan(session: Session, trade_date: date) -> Optional[PostReview]:
        """获取盘后计划"""
        return session.exec(
            select(PostReview).where(
                PostReview.trade_date == trade_date
            )
        ).first()

    @staticmethod
    def get_by_date_range(
        session: Session,
        start_date: date,
        end_date: date
    ) -> List[HistoricalPlan]:
        """获取日期范围内的历史计划"""
        return session.exec(
            select(HistoricalPlan).where(
                HistoricalPlan.trade_date >= start_date,
                HistoricalPlan.trade_date <= end_date
            )
        ).all()

    @staticmethod
    def get_all_plans(session: Session, limit: int = 100) -> List[HistoricalPlan]:
        """获取所有历史计划"""
        return session.exec(
            select(HistoricalPlan).order_by(HistoricalPlan.trade_date.desc()).limit(limit)
        ).all()
