"""
计划/复盘 Service
"""
from typing import Optional, List
from datetime import date
from sqlmodel import Session, select

from app.database import engine
from app.models.daily import Plan


class DailyService:
    """计划/复盘服务"""

    @staticmethod
    def list(
        type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Plan]:
        """获取计划/复盘列表"""
        with Session(engine) as session:
            statement = select(Plan).order_by(Plan.trade_date.desc()).limit(limit)

            if type:
                statement = statement.where(Plan.type == type)
            if start_date:
                statement = statement.where(Plan.trade_date >= start_date)
            if end_date:
                statement = statement.where(Plan.trade_date <= end_date)

            return session.exec(statement).all()

    @staticmethod
    def get(plan_id: int) -> Optional[Plan]:
        """获取单个计划/复盘"""
        with Session(engine) as session:
            return session.get(Plan, plan_id)

    @staticmethod
    def get_with_related(plan_id: int) -> dict:
        """获取单个计划/复盘（含关联数据）"""
        with Session(engine) as session:
            plan = session.get(Plan, plan_id)
            if not plan:
                return None

            result = plan.model_dump()
            if plan.related_id:
                related = session.get(Plan, plan.related_id)
                if related:
                    result['related_plan'] = {
                        'id': related.id,
                        'type': related.type,
                        'content': related.content,
                        'trade_date': related.trade_date
                    }
            return result

    @staticmethod
    def create(
        type: str,
        trade_date: date,
        content: str,
        template: Optional[str],
        tags: Optional[str],
        related_id: Optional[int],
        stock_count: int,
        execution_rate: float,
        pnl: float,
    ) -> Plan:
        """创建计划或复盘"""
        with Session(engine) as session:
            db_item = Plan(
                type=type,
                trade_date=trade_date,
                content=content,
                template=template,
                tags=tags,
                related_id=related_id,
                stock_count=stock_count,
                execution_rate=execution_rate,
                pnl=pnl,
            )
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return db_item

    @staticmethod
    def update(plan_id: int, **kwargs) -> Optional[Plan]:
        """更新计划或复盘"""
        with Session(engine) as session:
            db_item = session.get(Plan, plan_id)
            if not db_item:
                return None

            for key, value in kwargs.items():
                if value is not None and hasattr(db_item, key):
                    setattr(db_item, key, value)

            db_item.updated_at = date.today()
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return db_item

    @staticmethod
    def delete(plan_id: int) -> bool:
        """删除计划或复盘"""
        with Session(engine) as session:
            item = session.get(Plan, plan_id)
            if not item:
                return False
            session.delete(item)
            session.commit()
            return True

    @staticmethod
    def get_today() -> dict:
        """获取今日计划和复盘"""
        with Session(engine) as session:
            today = date.today()

            plan = session.exec(
                select(Plan).where(
                    Plan.trade_date == today,
                    Plan.type == "plan"
                )
            ).first()

            review = session.exec(
                select(Plan).where(
                    Plan.trade_date == today,
                    Plan.type == "review"
                )
            ).first()

            return {
                "plan": plan.model_dump() if plan else None,
                "review": review.model_dump() if review else None
            }

    @staticmethod
    def create_review_from_plan(plan_id: int, content: str) -> Optional[Plan]:
        """基于计划创建复盘"""
        with Session(engine) as session:
            plan = session.get(Plan, plan_id)
            if not plan:
                return None

            review = Plan(
                type="review",
                trade_date=plan.trade_date,
                content=content,
                related_id=plan.id,
                template=plan.template,
            )
            session.add(review)
            session.commit()
            session.refresh(review)
            return review
