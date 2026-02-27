"""
策略迭代 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import engine
from app.models.trading import StrategyIteration

router = APIRouter(prefix="/api/iterations", tags=["策略迭代"])


class IterationCreate(BaseModel):
    strategy_id: int
    version: int
    changes: Optional[str] = None
    test_result: Optional[str] = None
    backtest_result_id: Optional[int] = None
    notes: Optional[str] = None


class IterationResponse(BaseModel):
    id: int
    strategy_id: int
    version: int
    changes: Optional[str]
    test_result: Optional[str]
    backtest_result_id: Optional[int]
    notes: Optional[str]
    created_at: datetime


@router.get("", response_model=List[IterationResponse])
def get_iterations(
    strategy_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
):
    """获取迭代列表"""
    with Session(engine) as session:
        query = select(StrategyIteration)
        if strategy_id:
            query = query.where(StrategyIteration.strategy_id == strategy_id)
        query = query.order_by(StrategyIteration.version.desc()).offset(offset).limit(limit)
        return session.exec(query).all()


@router.get("/{iteration_id}", response_model=IterationResponse)
def get_iteration(iteration_id: int):
    """获取单个迭代"""
    with Session(engine) as session:
        iteration = session.get(StrategyIteration, iteration_id)
        if not iteration:
            raise HTTPException(status_code=404, detail="迭代记录不存在")
        return iteration


@router.post("", response_model=IterationResponse)
def create_iteration(iteration: IterationCreate):
    """创建新版本"""
    with Session(engine) as session:
        db_iteration = StrategyIteration(**iteration.model_dump())
        session.add(db_iteration)
        session.commit()
        session.refresh(db_iteration)
        return db_iteration


@router.delete("/{iteration_id}")
def delete_iteration(iteration_id: int):
    """删除迭代记录"""
    with Session(engine) as session:
        iteration = session.get(StrategyIteration, iteration_id)
        if not iteration:
            raise HTTPException(status_code=404, detail="迭代记录不存在")
        session.delete(iteration)
        session.commit()
        return {"status": "deleted", "id": iteration_id}
