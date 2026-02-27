"""
回测策略 API
"""
import json
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import date

from app.services.backtest_strategy_service import BacktestStrategyService

router = APIRouter(prefix="/api/backtest/strategies", tags=["backtest-strategies"])


@router.get("")
def get_strategies(
    strategy_type: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """获取回测策略列表"""
    return BacktestStrategyService.list(
        strategy_type=strategy_type,
        is_active=is_active
    )


@router.get("/list")
def list_strategies():
    """获取自定义策略列表 (简化版)"""
    return BacktestStrategyService.list()


@router.post("")
def create_strategy(
    name: str = Query(...),
    description: Optional[str] = None,
    code: str = Query(...),
    strategy_type: str = "custom",
    params_definition: Optional[str] = None,
    is_builtin: bool = False,
    is_active: bool = True,
):
    """创建新的回测策略"""
    params = None
    if params_definition:
        try:
            params = json.loads(params_definition)
        except:
            pass

    try:
        return BacktestStrategyService.create(
            name=name,
            description=description,
            code=code,
            strategy_type=strategy_type,
            params_definition=params,
            is_builtin=is_builtin,
            is_active=is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{item_id}")
def get_strategy(item_id: int):
    """获取单个策略详情"""
    item = BacktestStrategyService.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return item


@router.put("/{item_id}")
def update_strategy(item_id: int, **kwargs):
    """更新策略"""
    try:
        item = BacktestStrategyService.update(item_id, **kwargs)
        if not item:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{item_id}")
def delete_strategy(item_id: int):
    """删除策略"""
    try:
        success = BacktestStrategyService.delete(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Strategy not found")
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/parse-params")
def parse_code_params(code: str = Query(...)):
    """解析策略代码，提取参数定义"""
    return BacktestStrategyService.parse_code_params(code)


@router.post("/init-builtin")
def init_builtin_strategies():
    """初始化内置策略"""
    count = BacktestStrategyService.init_builtin_strategies()
    return {"ok": True, "added": count}
