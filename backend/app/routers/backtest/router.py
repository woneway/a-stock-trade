"""
回测 API
"""
import json
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, timedelta
from sqlmodel import Session, select

from app.database import engine
from app.services.backtest_engine import BacktestEngine
from app.models.backtest_strategy import BacktestStrategy
from app.models.external_data import ExternalStockBasic

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run")
def run_backtest(
    stock_code: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    initial_capital: float = 100000,
    strategy_type: str = "ma_cross",
    strategy_id: Optional[int] = None,
    strategy_params: Optional[str] = None,
    fast_period: int = 10,
    slow_period: int = 20,
    rsi_period: int = 14,
    rsi_upper: int = 70,
    rsi_lower: int = 30,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    bb_period: int = 20,
    bb_std: float = 2.0,
):
    """运行回测"""
    engine = BacktestEngine(initial_capital)

    df = engine.get_kline_dataframe(
        stock_code,
        start_date,
        end_date
    )

    if df is None or df.empty or len(df) < 10:
        raise HTTPException(
            status_code=404,
            detail=f"未找到股票 {stock_code} 的足够K线数据。请先通过数据同步功能获取K线数据，或检查网络连接后重试。"
        )

    # 解析 strategy_params
    params = None
    if strategy_params:
        try:
            params = json.loads(strategy_params)
        except:
            pass

    # 检查是否是自定义策略
    if strategy_id:
        with Session(engine) as session:
            strategy = session.get(BacktestStrategy, strategy_id)
            if not strategy:
                raise HTTPException(status_code=404, detail="策略不存在")

            if not strategy.is_active:
                raise HTTPException(status_code=400, detail="策略已停用")

            # 获取参数
            final_params = params or {}
            if not final_params and strategy.params_definition:
                try:
                    param_defs = json.loads(strategy.params_definition)
                    for param in param_defs:
                        param_name = param.get("name")
                        if param_name and param.get("default") is not None:
                            final_params[param_name] = param.get("default")
                except:
                    pass

            result = engine.run_custom_strategy(df, strategy.code, final_params)
            return result

    # 内置策略
    strategy_map = {
        "ma_cross": lambda: engine.run_ma_cross(df, fast_period or 10, slow_period or 20),
        "rsi": lambda: engine.run_rsi(df, rsi_period or 14, rsi_upper or 70, rsi_lower or 30),
        "macd": lambda: engine.run_macd(df, macd_fast or 12, macd_slow or 26, macd_signal or 9),
        "bollinger": lambda: engine.run_bollinger(df, bb_period or 20, bb_std or 2.0),
    }

    strategy_func = strategy_map.get(strategy_type)
    if not strategy_func:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的策略类型: {strategy_type}"
        )

    return strategy_func()


@router.get("/stocks")
def get_backtest_stocks(limit: int = 50):
    """获取可回测的股票列表"""
    with Session(engine) as session:
        stocks = session.exec(
            select(ExternalStockBasic).where(
                ExternalStockBasic.list_status == "L"
            ).limit(limit)
        ).all()

        return [
            {
                "code": s.code,
                "name": s.name,
                "market": s.market,
            }
            for s in stocks
        ]


@router.get("/strategies")
def get_available_strategies():
    """获取可用的策略列表 (包括内置和自定义)"""

    # 内置策略
    builtin_strategies = [
        {
            "id": "ma_cross",
            "name": "双均线交叉",
            "description": "快速均线上穿慢速均线买入，下穿卖出",
            "strategy_type": "builtin",
            "params": [
                {"name": "fast_period", "label": "快速均线周期", "default": 10, "min": 5, "max": 50, "type": "int"},
                {"name": "slow_period", "label": "慢速均线周期", "default": 20, "min": 10, "max": 200, "type": "int"},
            ]
        },
        {
            "id": "rsi",
            "name": "RSI超买超卖",
            "description": "RSI低于下界买入，高于上界卖出",
            "strategy_type": "builtin",
            "params": [
                {"name": "rsi_period", "label": "RSI周期", "default": 14, "min": 5, "max": 30, "type": "int"},
                {"name": "rsi_upper", "label": "超买阈值", "default": 70, "min": 50, "max": 90, "type": "int"},
                {"name": "rsi_lower", "label": "超卖阈值", "default": 30, "min": 10, "max": 50, "type": "int"},
            ]
        },
        {
            "id": "macd",
            "name": "MACD",
            "description": "MACD柱状图上穿0轴买入，下穿卖出",
            "strategy_type": "builtin",
            "params": [
                {"name": "macd_fast", "label": "快线周期", "default": 12, "min": 5, "max": 30, "type": "int"},
                {"name": "macd_slow", "label": "慢线周期", "default": 26, "min": 15, "max": 50, "type": "int"},
                {"name": "macd_signal", "label": "信号线周期", "default": 9, "min": 5, "max": 20, "type": "int"},
            ]
        },
        {
            "id": "bollinger",
            "name": "布林带",
            "description": "价格跌破下轨买入，突破上轨卖出",
            "strategy_type": "builtin",
            "params": [
                {"name": "bb_period", "label": "布林带周期", "default": 20, "min": 10, "max": 50, "type": "int"},
                {"name": "bb_std", "label": "标准差倍数", "default": 2.0, "min": 1.5, "max": 3.0, "type": "float"},
            ]
        },
    ]

    # 从数据库获取自定义策略
    with Session(engine) as session:
        custom_strategies = session.exec(
            select(BacktestStrategy).where(BacktestStrategy.is_active == True)
        ).all()

        custom_list = []
        for s in custom_strategies:
            try:
                params = json.loads(s.params_definition or "[]")
            except:
                params = []

            custom_list.append({
                "id": str(s.id),
                "name": s.name,
                "description": s.description or "",
                "strategy_type": s.strategy_type,
                "params": params,
                "is_builtin": s.is_builtin,
            })

    return {
        "builtin": builtin_strategies,
        "custom": custom_list,
        "all": builtin_strategies + custom_list,
    }
