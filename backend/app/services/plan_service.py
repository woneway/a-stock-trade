from typing import Optional, List
from datetime import date
from sqlmodel import Session, select
from app.models.plan import Plan


class PlanService:
    """计划服务"""

    @staticmethod
    def get_pre_plan(session: Session, trade_date: date) -> Optional[Plan]:
        """获取盘前计划"""
        return session.exec(
            select(Plan).where(
                Plan.plan_date == trade_date,
                Plan.plan_type == "pre"
            )
        ).first()

    @staticmethod
    def get_post_plan(session: Session, trade_date: date) -> Optional[Plan]:
        """获取盘后计划"""
        return session.exec(
            select(Plan).where(
                Plan.plan_date == trade_date,
                Plan.plan_type == "post"
            )
        ).first()

    @staticmethod
    def get_by_date_range(
        session: Session,
        start_date: date,
        end_date: date
    ) -> List[Plan]:
        """获取日期范围内的计划"""
        return session.exec(
            select(Plan).where(
                Plan.plan_date >= start_date,
                Plan.plan_date <= end_date
            )
        ).all()

    @staticmethod
    def get_all_plans(session: Session, limit: int = 100) -> List[Plan]:
        """获取所有计划"""
        return session.exec(
            select(Plan).order_by(Plan.plan_date.desc()).limit(limit)
        ).all()

    @staticmethod
    def get_by_type(session: Session, plan_type: str) -> List[Plan]:
        """根据类型获取计划"""
        return session.exec(
            select(Plan).where(Plan.plan_type == plan_type)
        ).all()
