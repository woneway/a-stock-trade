from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.routers.backtest.engine_enhanced import EnhancedBacktestEngine


router = APIRouter(prefix="/api/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    initial_capital: float = 100000
    strategy_type: str = "ma_cross"
    # MA Cross params
    fast_period: Optional[int] = 10
    slow_period: Optional[int] = 20
    # RSI params
    rsi_period: Optional[int] = 14
    rsi_upper: Optional[int] = 70
    rsi_lower: Optional[int] = 30
    # MACD params
    macd_fast: Optional[int] = 12
    macd_slow: Optional[int] = 26
    macd_signal: Optional[int] = 9
    # Bollinger params
    bb_period: Optional[int] = 20
    bb_std: Optional[float] = 2.0
    # Stop loss/profit params
    stop_loss_pct: Optional[float] = 10
    stop_profit_pct: Optional[float] = 10


class BacktestResult(BaseModel):
    initial_capital: float
    final_value: float
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    best_trade: float
    worst_trade: float
    avg_trade: float
    trades: List[Dict]
    equity_curve: List[Dict]
    indicators: Dict


@router.post("/run", response_model=BacktestResult)
def run_backtest(request: BacktestRequest):
    """运行增强回测 - 返回详细交易记录和指标"""
    engine = EnhancedBacktestEngine(request.initial_capital)

    df = engine.get_kline_dataframe(
        request.stock_code,
        request.start_date,
        request.end_date
    )

    if df is None or df.empty or len(df) < 10:
        raise HTTPException(
            status_code=404,
            detail=f"未找到股票 {request.stock_code} 的足够K线数据 (需要至少10条)"
        )

    strategy_map = {
        "ma_cross": lambda: engine.run_ma_cross(
            df, request.fast_period or 10, request.slow_period or 20
        ),
        "rsi": lambda: engine.run_rsi(
            df, request.rsi_period or 14, request.rsi_upper or 70, request.rsi_lower or 30
        ),
        "macd": lambda: engine.run_macd(
            df, request.macd_fast or 12, request.macd_slow or 26, request.macd_signal or 9
        ),
        "bollinger": lambda: engine.run_bollinger(
            df, request.bb_period or 20, request.bb_std or 2.0
        ),
        "simple_trend": lambda: engine.run_simple_trend(df),
        "stop_loss_profit": lambda: engine.run_stop_loss_profit(
            df, request.stop_loss_pct or 10, request.stop_profit_pct or 10
        ),
    }

    strategy_func = strategy_map.get(request.strategy_type)
    if not strategy_func:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的策略类型: {request.strategy_type}"
        )

    result = strategy_func()
    return BacktestResult(**result)


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
