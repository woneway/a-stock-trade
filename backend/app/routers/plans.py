"""
交易计划 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field
from sqlmodel import Session, select, func

from app.database import engine
from app.models.trading import TradingPlan

router = APIRouter(prefix="/api/plans", tags=["交易计划"])


# Pydantic 模型
class TradingPlanCreate(BaseModel):
    stock_code: str
    stock_name: Optional[str] = None
    plan_date: date
    target_price: Optional[float] = None
    quantity: Optional[int] = None
    strategy_type: str = "custom"
    trade_mode: Optional[str] = None
    stop_loss: Optional[float] = None
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    validation_conditions: Optional[str] = None
    reason: Optional[str] = None
    status: str = "draft"
    notes: Optional[str] = None


class TradingPlanUpdate(BaseModel):
    stock_name: Optional[str] = None
    target_price: Optional[float] = None
    quantity: Optional[int] = None
    strategy_type: Optional[str] = None
    trade_mode: Optional[str] = None
    stop_loss: Optional[float] = None
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    validation_conditions: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class TradingPlanResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: Optional[str]
    plan_date: date
    target_price: Optional[float]
    quantity: Optional[int]
    strategy_type: str
    trade_mode: Optional[str]
    stop_loss: Optional[float]
    take_profit_1: Optional[float]
    take_profit_2: Optional[float]
    validation_conditions: Optional[str]
    reason: Optional[str]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


# CRUD 端点
@router.get("", response_model=List[TradingPlanResponse])
def get_plans(
    stock_code: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    """获取交易计划列表"""
    with Session(engine) as session:
        query = select(TradingPlan)
        if stock_code:
            query = query.where(TradingPlan.stock_code == stock_code)
        if status:
            query = query.where(TradingPlan.status == status)
        query = query.order_by(TradingPlan.plan_date.desc()).offset(offset).limit(limit)
        plans = session.exec(query).all()
        return plans


@router.get("/{plan_id}", response_model=TradingPlanResponse)
def get_plan(plan_id: int):
    """获取单个交易计划"""
    with Session(engine) as session:
        plan = session.get(TradingPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="计划不存在")
        return plan


@router.post("", response_model=TradingPlanResponse)
def create_plan(plan: TradingPlanCreate):
    """创建交易计划"""
    with Session(engine) as session:
        db_plan = TradingPlan(**plan.model_dump())
        session.add(db_plan)
        session.commit()
        session.refresh(db_plan)
        return db_plan


@router.put("/{plan_id}", response_model=TradingPlanResponse)
def update_plan(plan_id: int, plan: TradingPlanUpdate):
    """更新交易计划"""
    with Session(engine) as session:
        db_plan = session.get(TradingPlan, plan_id)
        if not db_plan:
            raise HTTPException(status_code=404, detail="计划不存在")

        update_data = plan.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_plan, key, value)

        db_plan.updated_at = datetime.now()
        session.add(db_plan)
        session.commit()
        session.refresh(db_plan)
        return db_plan


@router.delete("/{plan_id}")
def delete_plan(plan_id: int):
    """删除交易计划"""
    with Session(engine) as session:
        plan = session.get(TradingPlan, plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="计划不存在")
        session.delete(plan)
        session.commit()
        return {"status": "deleted", "id": plan_id}


@router.get("/stats/summary")
def get_plans_summary():
    """获取计划统计"""
    with Session(engine) as session:
        total = session.exec(func.count(TradingPlan.id)).first() or 0
        draft = session.exec(func.count(TradingPlan.id)).where(TradingPlan.status == "draft").first() or 0
        executed = session.exec(func.count(TradingPlan.id)).where(TradingPlan.status == "executed").first() or 0
        abandoned = session.exec(func.count(TradingPlan.id)).where(TradingPlan.status == "abandoned").first() or 0

        return {
            "total": total,
            "draft": draft,
            "executed": executed,
            "abandoned": abandoned,
        }
