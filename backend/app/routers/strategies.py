"""
策略管理 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel
from sqlmodel import Session, select, func

from app.database import engine
from app.models.trading import Strategy

router = APIRouter(prefix="/api/strategies", tags=["策略管理"])


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: str = "custom"
    code: Optional[str] = None
    params_definition: str = "[]"
    is_builtin: bool = False
    is_active: bool = True


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    strategy_type: Optional[str] = None
    code: Optional[str] = None
    params_definition: Optional[str] = None
    is_active: Optional[bool] = None


class StrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    strategy_type: str
    code: Optional[str]
    params_definition: str
    is_builtin: bool
    is_active: bool
    created_at: date
    updated_at: date


@router.get("", response_model=List[StrategyResponse])
def get_strategies(
    strategy_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
):
    """获取策略列表"""
    with Session(engine) as session:
        query = select(Strategy)
        if strategy_type:
            query = query.where(Strategy.strategy_type == strategy_type)
        if is_active is not None:
            query = query.where(Strategy.is_active == is_active)
        query = query.order_by(Strategy.created_at.desc()).offset(offset).limit(limit)
        return session.exec(query).all()


@router.get("/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: int):
    """获取单个策略"""
    with Session(engine) as session:
        strategy = session.get(Strategy, strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        return strategy


@router.post("", response_model=StrategyResponse)
def create_strategy(strategy: StrategyCreate):
    """创建策略"""
    with Session(engine) as session:
        # 检查名称是否已存在
        existing = session.exec(select(Strategy).where(Strategy.name == strategy.name)).first()
        if existing:
            raise HTTPException(status_code=400, detail="策略名称已存在")

        db_strategy = Strategy(**strategy.model_dump())
        session.add(db_strategy)
        session.commit()
        session.refresh(db_strategy)
        return db_strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(strategy_id: int, strategy: StrategyUpdate):
    """更新策略"""
    with Session(engine) as session:
        db_strategy = session.get(Strategy, strategy_id)
        if not db_strategy:
            raise HTTPException(status_code=404, detail="策略不存在")

        update_data = strategy.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_strategy, key, value)

        db_strategy.updated_at = date.today()
        session.add(db_strategy)
        session.commit()
        session.refresh(db_strategy)
        return db_strategy


@router.delete("/{strategy_id}")
def delete_strategy(strategy_id: int):
    """删除策略"""
    with Session(engine) as session:
        strategy = session.get(Strategy, strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        if strategy.is_builtin:
            raise HTTPException(status_code=400, detail="内置策略不能删除")
        session.delete(strategy)
        session.commit()
        return {"status": "deleted", "id": strategy_id}


@router.put("/{strategy_id}/toggle")
def toggle_strategy(strategy_id: int):
    """启用/禁用策略"""
    with Session(engine) as session:
        strategy = session.get(Strategy, strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")

        strategy.is_active = not strategy.is_active
        strategy.updated_at = date.today()
        session.add(strategy)
        session.commit()
        return {"status": "toggled", "is_active": strategy.is_active}
