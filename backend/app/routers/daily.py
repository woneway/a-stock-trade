from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date, timedelta
from pydantic import BaseModel

from app.database import get_db
from app.models.daily import Plan


router = APIRouter(prefix="/api/daily", tags=["daily"])


class PlanCreate(BaseModel):
    type: str = "plan"
    trade_date: date
    content: str = ""
    template: Optional[str] = None
    tags: Optional[str] = None
    related_id: Optional[int] = None
    stock_count: Optional[int] = 0
    execution_rate: Optional[float] = 0.0
    pnl: Optional[float] = 0.0


class PlanUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    stock_count: Optional[int] = None
    execution_rate: Optional[float] = None
    pnl: Optional[float] = None
    tags: Optional[str] = None


class PlanResponse(BaseModel):
    id: int
    type: str
    trade_date: date
    status: str
    template: Optional[str]
    content: Optional[str]
    related_id: Optional[int]
    stock_count: int
    execution_rate: float
    pnl: float
    tags: Optional[str]
    created_at: date
    updated_at: date

    # 关联的计划/复盘
    related_plan: Optional[dict] = None


@router.get("/plans", response_model=List[PlanResponse])
def get_plans(
    db: Session = Depends(get_db),
    type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """获取计划/复盘列表"""
    statement = select(Plan).order_by(Plan.trade_date.desc()).limit(limit)

    if type:
        statement = statement.where(Plan.type == type)
    if start_date:
        statement = statement.where(Plan.trade_date >= start_date)
    if end_date:
        statement = statement.where(Plan.trade_date <= end_date)

    plans = db.exec(statement).all()

    # 转换结果并添加关联数据
    result = []
    for p in plans:
        plan_dict = p.model_dump()
        # 获取关联的计划/复盘
        if p.related_id:
            related = db.get(Plan, p.related_id)
            if related:
                plan_dict['related_plan'] = {
                    'id': related.id,
                    'type': related.type,
                    'content': related.content,
                    'trade_date': related.trade_date
                }
        result.append(plan_dict)

    return result


@router.get("/plans/today")
def get_today_plan(db: Session = Depends(get_db)):
    """获取今日计划和复盘"""
    today = date.today()

    # 获取今日计划
    plan = db.exec(
        select(Plan).where(
            Plan.trade_date == today,
            Plan.type == "plan"
        )
    ).first()

    # 获取今日复盘
    review = db.exec(
        select(Plan).where(
            Plan.trade_date == today,
            Plan.type == "review"
        )
    ).first()

    return {
        "plan": plan.model_dump() if plan else None,
        "review": review.model_dump() if review else None
    }


@router.get("/plans/{item_id}", response_model=PlanResponse)
def get_plan(item_id: int, db: Session = Depends(get_db)):
    """获取单个计划/复盘"""
    plan = db.get(Plan, item_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Not found")

    result = plan.model_dump()
    if plan.related_id:
        related = db.get(Plan, plan.related_id)
        if related:
            result['related_plan'] = {
                'id': related.id,
                'type': related.type,
                'content': related.content,
                'trade_date': related.trade_date
            }

    return result


@router.post("/plans", response_model=PlanResponse)
def create_plan(item: PlanCreate, db: Session = Depends(get_db)):
    """创建计划或复盘"""
    db_item = Plan(
        type=item.type,
        trade_date=item.trade_date,
        content=item.content,
        template=item.template,
        tags=item.tags,
        related_id=item.related_id,
        stock_count=item.stock_count or 0,
        execution_rate=item.execution_rate or 0.0,
        pnl=item.pnl or 0.0,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/plans/{item_id}", response_model=PlanResponse)
def update_plan(item_id: int, item: PlanUpdate, db: Session = Depends(get_db)):
    """更新计划或复盘"""
    db_item = db.get(Plan, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Not found")

    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)

    db_item.updated_at = date.today()
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/plans/{item_id}")
def delete_plan(item_id: int, db: Session = Depends(get_db)):
    """删除计划或复盘"""
    item = db.get(Plan, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"ok": True}


@router.post("/plans/{item_id}/review")
def create_review_from_plan(item_id: int, content: str, db: Session = Depends(get_db)):
    """基于计划创建复盘"""
    plan = db.get(Plan, item_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    review = Plan(
        type="review",
        trade_date=plan.trade_date,
        content=content,
        related_id=plan.id,
        template=plan.template,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
