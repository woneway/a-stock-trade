from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.routers.backtest.engine_enhanced import EnhancedBacktestEngine
from app.routers.backtest.optimizer import ParameterOptimizer


router = APIRouter(prefix="/api/optimizer", tags=["optimizer"])


# 策略参数模板
STRATEGY_PARAM_GRIDS = {
    "ma_cross": {
        "fast_period": [5, 7, 10, 12, 15, 20],
        "slow_period": [15, 20, 25, 30, 40, 50, 60],
    },
    "rsi": {
        "rsi_period": [7, 10, 14, 21, 28],
        "rsi_upper": [60, 65, 70, 75, 80],
        "rsi_lower": [20, 25, 30, 35, 40],
    },
    "macd": {
        "macd_fast": [8, 10, 12, 15],
        "macd_slow": [20, 24, 26, 30],
        "macd_signal": [6, 8, 9, 11],
    },
    "bollinger": {
        "bb_period": [10, 15, 20, 25, 30],
        "bb_std": [1.5, 1.8, 2.0, 2.2, 2.5],
    },
    "stop_loss_profit": {
        "stop_loss_pct": [5, 7, 10, 12, 15],
        "stop_profit_pct": [5, 7, 10, 15, 20],
    },
}


class OptimizeRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    strategy_type: str
    initial_capital: float = 100000
    method: str = "grid"
    n_iter: Optional[int] = 50
    objective: str = "sharpe_ratio"
    param_overrides: Optional[Dict[str, List[Any]]] = None


class OptimizeResult(BaseModel):
    best_params: Dict[str, Any]
    best_metrics: Dict[str, float]
    total_combinations: int
    objective: str
    top_10: List[Dict[str, Any]]


@router.post("/run", response_model=OptimizeResult)
def run_optimization(request: OptimizeRequest):
    """运行参数优化"""
    if request.strategy_type not in STRATEGY_PARAM_GRIDS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的策略类型: {request.strategy_type}. 支持: {list(STRATEGY_PARAM_GRIDS.keys())}"
        )

    engine = EnhancedBacktestEngine(request.initial_capital)

    df = engine.get_kline_dataframe(
        request.stock_code,
        request.start_date,
        request.end_date
    )

    if df is None or df.empty or len(df) < 50:
        raise HTTPException(
            status_code=404,
            detail=f"未找到股票 {request.stock_code} 的足够K线数据 (需要至少50条)"
        )

    param_grid = STRATEGY_PARAM_GRIDS[request.strategy_type].copy()
    if request.param_overrides:
        param_grid.update(request.param_overrides)

    # 映射策略类型到回测函数
    strategy_map = {
        "ma_cross": lambda df, **p: engine.run_ma_cross(df, p.get('fast_period', 10), p.get('slow_period', 20)),
        "rsi": lambda df, **p: engine.run_rsi(df, p.get('rsi_period', 14), p.get('rsi_upper', 70), p.get('rsi_lower', 30)),
        "macd": lambda df, **p: engine.run_macd(df, p.get('macd_fast', 12), p.get('macd_slow', 26), p.get('macd_signal', 9)),
        "bollinger": lambda df, **p: engine.run_bollinger(df, p.get('bb_period', 20), p.get('bb_std', 2.0)),
        "stop_loss_profit": lambda df, **p: engine.run_stop_loss_profit(df, p.get('stop_loss_pct', 10), p.get('stop_profit_pct', 10)),
    }

    backtest_func = strategy_map.get(request.strategy_type)
    if not backtest_func:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的策略类型: {request.strategy_type}"
        )

    optimizer = ParameterOptimizer(
        param_grid=param_grid,
        objective=request.objective,
        maximize=request.objective != "max_drawdown"
    )

    optimizer.optimize(
        backtest_func=backtest_func,
        df=df,
        method=request.method,
        n_iter=request.n_iter or 50,
        initial_capital=request.initial_capital
    )

    summary = optimizer.summary()

    return OptimizeResult(
        best_params=summary["best_params"],
        best_metrics=summary["best_metrics"],
        total_combinations=summary["total_combinations"],
        objective=summary["objective"],
        top_10=summary["top_10"]
    )


@router.get("/param-grids")
def get_param_grids():
    """获取策略参数模板"""
    return STRATEGY_PARAM_GRIDS


@router.get("/objectives")
def get_objectives():
    """获取可用的优化目标"""
    return [
        {"id": "sharpe_ratio", "name": "夏普比率", "description": "风险调整后收益，越高越好"},
        {"id": "total_return", "name": "总收益率", "description": "策略总收益，越高越好"},
        {"id": "max_drawdown", "name": "最大回撤", "description": "最大回撤幅度，越小越好"},
        {"id": "win_rate", "name": "胜率", "description": "盈利交易占比，越高越好"},
    ]
