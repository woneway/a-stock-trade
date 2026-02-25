from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.models import Strategy

router = APIRouter()


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trade_mode: Optional[str] = None
    entry_conditions: Optional[dict] = None
    exit_conditions: Optional[dict] = None
    stop_loss_ratio: Optional[float] = -5
    take_profit_ratio: Optional[float] = 10
    max_position_ratio: Optional[float] = 20
    scenario_handling: Optional[dict] = None
    discipline: Optional[dict] = None
    is_active: Optional[bool] = True
    is_template: Optional[bool] = False


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trade_mode: Optional[str] = None
    entry_conditions: Optional[dict] = None
    exit_conditions: Optional[dict] = None
    stop_loss_ratio: Optional[float] = None
    take_profit_ratio: Optional[float] = None
    max_position_ratio: Optional[float] = None
    scenario_handling: Optional[dict] = None
    discipline: Optional[dict] = None
    is_active: Optional[bool] = None
    is_template: Optional[bool] = None


class StrategyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    trade_mode: Optional[str]
    entry_conditions: Optional[dict]
    exit_conditions: Optional[dict]
    stop_loss_ratio: float
    take_profit_ratio: float
    max_position_ratio: float
    scenario_handling: Optional[dict]
    discipline: Optional[dict]
    is_active: bool
    is_template: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/strategies", response_model=List[StrategyResponse])
def get_strategies(
    is_active: Optional[bool] = None,
    is_template: Optional[bool] = None,
    trade_mode: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取策略列表"""
    query = db.query(Strategy)
    if is_active is not None:
        query = query.filter(Strategy.is_active == is_active)
    if is_template is not None:
        query = query.filter(Strategy.is_template == is_template)
    if trade_mode:
        query = query.filter(Strategy.trade_mode == trade_mode)
    return query.order_by(Strategy.created_at.desc()).all()


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """获取单个策略详情"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    return strategy


@router.post("/strategies", response_model=StrategyResponse)
def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """创建新策略"""
    db_strategy = Strategy(**strategy.model_dump())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
def update_strategy(strategy_id: int, strategy: StrategyUpdate, db: Session = Depends(get_db)):
    """更新策略"""
    db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    update_data = strategy.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_strategy, key, value)

    db_strategy.updated_at = datetime.now()
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.delete("/strategies/{strategy_id}")
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """删除策略"""
    db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="策略不存在")

    db.delete(db_strategy)
    db.commit()
    return {"message": "策略已删除"}


@router.post("/strategies/{strategy_id}/copy", response_model=StrategyResponse)
def copy_strategy(strategy_id: int, new_name: Optional[str] = None, db: Session = Depends(get_db)):
    """复制策略"""
    original = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="策略不存在")

    copy_data = {
        "name": new_name or f"{original.name} (副本)",
        "description": original.description,
        "trade_mode": original.trade_mode,
        "entry_conditions": original.entry_conditions,
        "exit_conditions": original.exit_conditions,
        "stop_loss_ratio": original.stop_loss_ratio,
        "take_profit_ratio": original.take_profit_ratio,
        "max_position_ratio": original.max_position_ratio,
        "scenario_handling": original.scenario_handling,
        "discipline": original.discipline,
        "is_active": True,
        "is_template": False,
    }

    db_strategy = Strategy(**copy_data)
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.get("/strategies/modes/list")
def get_trade_modes(db: Session = Depends(get_db)):
    """获取所有交易模式类型"""
    modes = db.query(Strategy.trade_mode).distinct().filter(
        Strategy.trade_mode.isnot(None)
    ).all()
    return [m[0] for m in modes if m[0]]
