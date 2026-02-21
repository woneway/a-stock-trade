from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.models import TradingPlan

router = APIRouter()


class PlanCreate(BaseModel):
    stock_code: str
    stock_name: str
    stock_type: str = "stock"
    trade_mode: str
    buy_timing: Optional[str] = None
    validation_conditions: Optional[dict] = None
    target_price: float
    position_ratio: float
    stop_loss_price: Optional[float] = None
    stop_loss_ratio: Optional[float] = None
    take_profit_price: Optional[float] = None
    take_profit_ratio: Optional[float] = None
    hold_period: Optional[str] = None
    logic: Optional[str] = None
    plan_date: date


class PlanUpdate(BaseModel):
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    stock_type: Optional[str] = None
    trade_mode: Optional[str] = None
    buy_timing: Optional[str] = None
    validation_conditions: Optional[dict] = None
    target_price: Optional[float] = None
    position_ratio: Optional[float] = None
    stop_loss_price: Optional[float] = None
    stop_loss_ratio: Optional[float] = None
    take_profit_price: Optional[float] = None
    take_profit_ratio: Optional[float] = None
    hold_period: Optional[str] = None
    logic: Optional[str] = None
    status: Optional[str] = None
    execute_result: Optional[str] = None


class PlanResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    stock_type: str
    trade_mode: str
    buy_timing: Optional[str]
    validation_conditions: Optional[dict]
    target_price: float
    position_ratio: float
    stop_loss_price: Optional[float]
    stop_loss_ratio: Optional[float]
    take_profit_price: Optional[float]
    take_profit_ratio: Optional[float]
    hold_period: Optional[str]
    logic: Optional[str]
    status: str
    execute_result: Optional[str]
    plan_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/plans", response_model=List[PlanResponse])
def get_plans(
    status: Optional[str] = None,
    plan_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    query = db.query(TradingPlan)
    if status:
        query = query.filter(TradingPlan.status == status)
    if plan_date:
        query = query.filter(TradingPlan.plan_date == plan_date)
    return query.order_by(TradingPlan.created_at.desc()).all()


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(TradingPlan).filter(TradingPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    return plan


@router.post("/plans", response_model=PlanResponse)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    db_plan = TradingPlan(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.put("/plans/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, plan: PlanUpdate, db: Session = Depends(get_db)):
    db_plan = db.query(TradingPlan).filter(TradingPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    update_data = plan.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)

    db_plan.updated_at = datetime.now()
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = db.query(TradingPlan).filter(TradingPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    db.delete(db_plan)
    db.commit()
    return {"message": "计划已删除"}


@router.post("/plans/{plan_id}/execute")
def execute_plan(plan_id: int, execute_result: str, db: Session = Depends(get_db)):
    db_plan = db.query(TradingPlan).filter(TradingPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    db_plan.status = "executed"
    db_plan.execute_result = execute_result
    db_plan.updated_at = datetime.now()
    db.commit()
    return {"message": "计划已执行", "status": db_plan.status}


@router.post("/plans/{plan_id}/abandon")
def abandon_plan(plan_id: int, reason: Optional[str] = None, db: Session = Depends(get_db)):
    db_plan = db.query(TradingPlan).filter(TradingPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    db_plan.status = "abandoned"
    db_plan.execute_result = reason or "手动放弃"
    db_plan.updated_at = datetime.now()
    db.commit()
    return {"message": "计划已放弃", "status": db_plan.status}
