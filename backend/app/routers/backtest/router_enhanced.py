"""
增强回测 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.backtest_engine import BacktestEngine

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run")
def run_backtest(
    stock_code: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    initial_capital: float = 100000,
    strategy_type: str = "ma_cross",
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
    stop_loss_pct: float = 10,
    stop_profit_pct: float = 10,
):
    """运行增强回测 - 返回详细交易记录和指标"""
    engine = BacktestEngine(initial_capital)

    df = engine.get_kline_dataframe(
        stock_code,
        start_date,
        end_date
    )

    if df is None or df.empty or len(df) < 10:
        raise HTTPException(
            status_code=404,
            detail=f"未找到股票 {stock_code} 的足够K线数据 (需要至少10条)"
        )

    strategy_map = {
        "ma_cross": lambda: engine.run_ma_cross(df, fast_period or 10, slow_period or 20),
        "rsi": lambda: engine.run_rsi(df, rsi_period or 14, rsi_upper or 70, rsi_lower or 30),
        "macd": lambda: engine.run_macd(df, macd_fast or 12, macd_slow or 26, macd_signal or 9),
        "bollinger": lambda: engine.run_bollinger(df, bb_period or 20, bb_std or 2.0),
        "simple_trend": lambda: engine.run_simple_trend(df),
        "stop_loss_profit": lambda: engine.run_stop_loss_profit(df, stop_loss_pct or 10, stop_profit_pct or 10),
    }

    strategy_func = strategy_map.get(strategy_type)
    if not strategy_func:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的策略类型: {strategy_type}"
        )

    return strategy_func()


@router.get("/strategies")
def get_available_strategies():
    """获取可用的策略列表"""
    return [
        {
            "id": "simple_trend",
            "name": "简单趋势",
            "description": "阳线买入，阴线卖出",
            "params": []
        },
        {
            "id": "stop_loss_profit",
            "name": "止盈止损",
            "description": "固定止盈止损比例",
            "params": [
                {"name": "stop_loss_pct", "label": "止损比例(%)", "default": 10, "min": 1, "max": 30},
                {"name": "stop_profit_pct", "label": "止盈比例(%)", "default": 10, "min": 1, "max": 50},
            ]
        },
        {
            "id": "ma_cross",
            "name": "双均线交叉",
            "description": "快速均线上穿慢速均线买入，下穿卖出",
            "params": [
                {"name": "fast_period", "label": "快速均线周期", "default": 10, "min": 5, "max": 50},
                {"name": "slow_period", "label": "慢速均线周期", "default": 20, "min": 10, "max": 200},
            ]
        },
        {
            "id": "rsi",
            "name": "RSI超买超卖",
            "description": "RSI低于下界买入，高于上界卖出",
            "params": [
                {"name": "rsi_period", "label": "RSI周期", "default": 14, "min": 5, "max": 30},
                {"name": "rsi_upper", "label": "超买阈值", "default": 70, "min": 50, "max": 90},
                {"name": "rsi_lower", "label": "超卖阈值", "default": 30, "min": 10, "max": 50},
            ]
        },
        {
            "id": "macd",
            "name": "MACD",
            "description": "MACD柱状图上穿0轴买入，下穿卖出",
            "params": [
                {"name": "macd_fast", "label": "快线周期", "default": 12, "min": 5, "max": 30},
                {"name": "macd_slow", "label": "慢线周期", "default": 26, "min": 15, "max": 50},
                {"name": "macd_signal", "label": "信号线周期", "default": 9, "min": 5, "max": 20},
            ]
        },
        {
            "id": "bollinger",
            "name": "布林带",
            "description": "价格跌破下轨买入，突破上轨卖出",
            "params": [
                {"name": "bb_period", "label": "布林带周期", "default": 20, "min": 10, "max": 50},
                {"name": "bb_std", "label": "标准差倍数", "default": 2.0, "min": 1.5, "max": 3.0},
            ]
        },
    ]
