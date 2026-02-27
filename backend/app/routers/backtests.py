"""
回测结果 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import engine
from app.models.trading import BacktestResult

router = APIRouter(prefix="/api/backtests", tags=["回测结果"])


class BacktestResultCreate(BaseModel):
    strategy_id: int
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float = 0
    annual_return: float = 0
    sharpe_ratio: float = 0
    max_drawdown: float = 0
    win_rate: float = 0
    total_trades: int = 0
    profit_trades: int = 0
    loss_trades: int = 0
    avg_profit: float = 0
    avg_loss: float = 0


class BacktestResultResponse(BaseModel):
    id: int
    strategy_id: int
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profit_trades: int
    loss_trades: int
    avg_profit: float
    avg_loss: float
    created_at: datetime


@router.get("", response_model=List[BacktestResultResponse])
def get_backtest_results(
    strategy_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
):
    """获取回测结果列表"""
    with Session(engine) as session:
        query = select(BacktestResult)
        if strategy_id:
            query = query.where(BacktestResult.strategy_id == strategy_id)
        query = query.order_by(BacktestResult.created_at.desc()).offset(offset).limit(limit)
        return session.exec(query).all()


@router.get("/{result_id}", response_model=BacktestResultResponse)
def get_backtest_result(result_id: int):
    """获取单个回测结果"""
    with Session(engine) as session:
        result = session.get(BacktestResult, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="回测结果不存在")
        return result


@router.post("", response_model=BacktestResultResponse)
def create_backtest_result(result: BacktestResultCreate):
    """保存回测结果"""
    with Session(engine) as session:
        db_result = BacktestResult(**result.model_dump())
        session.add(db_result)
        session.commit()
        session.refresh(db_result)
        return db_result


@router.delete("/{result_id}")
def delete_backtest_result(result_id: int):
    """删除回测结果"""
    with Session(engine) as session:
        result = session.get(BacktestResult, result_id)
        if not result:
            raise HTTPException(status_code=404, detail="回测结果不存在")
        session.delete(result)
        session.commit()
        return {"status": "deleted", "id": result_id}
