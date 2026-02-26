from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional, List, Dict, Any
from datetime import date, timedelta
from pydantic import BaseModel

from app.database import engine
from app.routers.backtest.engine_enhanced import EnhancedBacktestEngine as BacktestEngine


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    initial_capital: float = 100000
    strategy_type: str = "ma_cross"
    # 自定义策略ID (当使用自定义策略时)
    strategy_id: Optional[int] = None
    # 自定义策略参数 (当使用自定义策略时)
    strategy_params: Optional[Dict[str, Any]] = None
    fast_period: Optional[int] = 10
    slow_period: Optional[int] = 20
    rsi_period: Optional[int] = 14
    rsi_upper: Optional[int] = 70
    rsi_lower: Optional[int] = 30
    macd_fast: Optional[int] = 12
    macd_slow: Optional[int] = 26
    macd_signal: Optional[int] = 9
    bb_period: Optional[int] = 20
    bb_std: Optional[float] = 2.0


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


@router.post("/run", response_model=BacktestResult)
def run_backtest(
    request: BacktestRequest,
    db: Session = Depends(get_db)
):
    """运行回测"""
    engine = BacktestEngine(request.initial_capital)

    df = engine.get_kline_dataframe(
        db,
        request.stock_code,
        request.start_date,
        request.end_date
    )

    if df.empty or len(df) < 10:
        raise HTTPException(
            status_code=404,
            detail=f"未找到股票 {request.stock_code} 的足够K线数据。请先通过数据同步功能获取K线数据，或检查网络连接后重试。"
        )

    # 检查是否是自定义策略
    if request.strategy_id:
        # 从数据库获取自定义策略
        from app.models.backtest_strategy import BacktestStrategy

        strategy = db.get(BacktestStrategy, request.strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")

        if not strategy.is_active:
            raise HTTPException(status_code=400, detail="策略已停用")

        # 获取参数
        params = request.strategy_params or {}
        if not params and strategy.params_definition:
            # 从请求中提取参数
            for param in strategy.params_definition:
                param_name = param.get("name")
                if param_name:
                    # 尝试从请求中获取参数值
                    req_dict = request.model_dump()
                    if param_name in req_dict:
                        params[param_name] = req_dict[param_name]
                    elif param.get("default") is not None:
                        params[param_name] = param.get("default")

        result = engine.run_custom_strategy(df, strategy.code, params)
        return BacktestResult(**result)

    # 内置策略
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
    }

    strategy_func = strategy_map.get(request.strategy_type)
    if not strategy_func:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的策略类型: {request.strategy_type}"
        )

    result = strategy_func()
    return BacktestResult(**result)


@router.get("/stocks")
def get_backtest_stocks(
    db: Session = Depends(get_db),
    limit: int = 50
):
    """获取可回测的股票列表"""
    from app.models.external_data import StockBasic
    from sqlmodel import select

    stocks = db.exec(
        select(StockBasic).where(
            StockBasic.list_status == "L"
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


@router.get("/klines/{stock_code}")
def get_backtest_klines(
    stock_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 500
):
    """获取回测用K线数据"""
    from app.services.data_service import DataService

    if not start_date:
        start_date = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    df = DataService.get_kline_dataframe(stock_code, start_date, end_date)

    if df is None or df.empty:
        return []

    return df.head(limit).to_dict('records')


@router.get("/strategies")
def get_available_strategies(
    db: Session = Depends(get_db)
):
    """获取可用的策略列表 (包括内置和自定义)"""

    # 内置策略 (兼容旧格式)
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
    from app.models.backtest_strategy import BacktestStrategy
    import json as json_mod

    custom_strategies = db.exec(
        select(BacktestStrategy).where(BacktestStrategy.is_active == True)
    ).all()

    custom_list = []
    for s in custom_strategies:
        try:
            params = json_mod.loads(s.params_definition or "[]")
        except:
            params = []

        custom_list.append({
            "id": str(s.id),  # 使用字符串ID以区分内置策略
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
