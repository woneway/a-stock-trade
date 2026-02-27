"""
计划与复盘 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date

from app.services.daily_service import DailyService

router = APIRouter(prefix="/api/daily", tags=["daily"])


@router.get("/plans")
def get_plans(
    type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
):
    """获取计划/复盘列表"""
    plans = DailyService.list(
        type=type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )

    # 转换结果并添加关联数据
    result = []
    for p in plans:
        plan_dict = p.model_dump()
        # 获取关联的计划/复盘
        if p.related_id:
            related = DailyService.get(p.related_id)
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
def get_today_plan():
    """获取今日计划和复盘"""
    return DailyService.get_today()


@router.get("/plans/{item_id}")
def get_plan(item_id: int):
    """获取单个计划/复盘"""
    result = DailyService.get_with_related(item_id)
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result


@router.post("/plans")
def create_plan(
    type: str = "plan",
    trade_date: date = Query(...),
    content: str = "",
    template: Optional[str] = None,
    tags: Optional[str] = None,
    related_id: Optional[int] = None,
    stock_count: int = 0,
    execution_rate: float = 0.0,
    pnl: float = 0.0,
):
    """创建计划或复盘"""
    return DailyService.create(
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


@router.put("/plans/{item_id}")
def update_plan(item_id: int, **kwargs):
    """更新计划或复盘"""
    plan = DailyService.update(item_id, **kwargs)
    if not plan:
        raise HTTPException(status_code=404, detail="Not found")
    return plan


@router.delete("/plans/{item_id}")
def delete_plan(item_id: int):
    """删除计划或复盘"""
    success = DailyService.delete(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@router.post("/plans/{item_id}/review")
def create_review_from_plan(item_id: int, content: str):
    """基于计划创建复盘"""
    review = DailyService.create_review_from_plan(item_id, content)
    if not review:
        raise HTTPException(status_code=404, detail="Plan not found")
    return review
