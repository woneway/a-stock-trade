from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional, Dict, Any


class ScenarioHandling(BaseModel):
    break_up: Optional[str] = None
    high_open_down: Optional[str] = None
    volume_stagnant: Optional[str] = None
    news_impact: Optional[str] = None
    dragon_first_yin: Optional[str] = None
    sector_divide: Optional[str] = None


class Discipline(BaseModel):
    only_mode: Optional[bool] = True
    no_forcing: Optional[bool] = True
    cut_loss: Optional[bool] = True
    ignore_rumors: Optional[bool] = False
    stay_focused: Optional[bool] = True
    notes: Optional[str] = None


class StrategyBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: Optional[str] = None

    # 1. 模式定位
    trade_mode: Optional[str] = None
    mode_description: Optional[str] = None

    # 2. 情绪周期仓位
    position_rising: Optional[float] = 50.0
    position_consolidation: Optional[float] = 30.0
    position_decline: Optional[float] = 10.0
    position_chaos: Optional[float] = 20.0

    # 3. 选股标准
    stock_selection_logic: Optional[str] = None
    watch_signals: Optional[str] = None

    # 4. 介入时机
    entry_condition: Optional[str] = None
    timing_pattern: Optional[str] = None

    # 5. 卖出策略
    exit_condition: Optional[str] = None
    position_condition: Optional[str] = None

    # 量化选股条件
    min_turnover_rate: Optional[float] = None
    max_turnover_rate: Optional[float] = None
    min_volume_ratio: Optional[float] = None
    max_volume_ratio: Optional[float] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit_up_days: Optional[int] = None
    min_amplitude: Optional[float] = None
    max_amplitude: Optional[float] = None
    ma_days: Optional[str] = None
    volume_ma_days: Optional[int] = None
    min_consecutive_limit: Optional[int] = None
    min_circulating_market_cap: Optional[float] = None
    max_circulating_market_cap: Optional[float] = None
    theme_type: Optional[str] = None
    sentiment_cycle: Optional[str] = None
    market_condition: Optional[str] = None

    # 止盈止损
    take_profit_1: Optional[float] = 7.0
    take_profit_2: Optional[float] = 15.0
    trailing_stop: Optional[float] = 5.0
    max_daily_loss: Optional[float] = -5.0

    # 仓位管理
    max_positions: Optional[int] = 3
    min_single_position: Optional[float] = 10.0
    max_single_position: Optional[float] = 25.0

    # 效果目标
    win_rate_target: Optional[float] = None
    profit_factor_target: Optional[float] = None
    max_drawdown_target: Optional[float] = None

    stop_loss: float = 6.0
    position_size: float = 20.0
    is_active: bool = True

    # 7. 场景应对
    scenario_handling: Optional[Dict[str, Any]] = None

    # 8. 执行纪律
    discipline: Optional[Dict[str, Any]] = None

    iteration_history: Optional[str] = None


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    # 1. 模式定位
    trade_mode: Optional[str] = None
    mode_description: Optional[str] = None

    # 2. 情绪周期仓位
    position_rising: Optional[float] = None
    position_consolidation: Optional[float] = None
    position_decline: Optional[float] = None
    position_chaos: Optional[float] = None

    # 3. 选股标准
    stock_selection_logic: Optional[str] = None
    watch_signals: Optional[str] = None

    # 4. 介入时机
    entry_condition: Optional[str] = None
    timing_pattern: Optional[str] = None

    # 5. 卖出策略
    exit_condition: Optional[str] = None
    position_condition: Optional[str] = None

    # 量化选股条件
    min_turnover_rate: Optional[float] = None
    max_turnover_rate: Optional[float] = None
    min_volume_ratio: Optional[float] = None
    max_volume_ratio: Optional[float] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit_up_days: Optional[int] = None
    min_amplitude: Optional[float] = None
    max_amplitude: Optional[float] = None
    ma_days: Optional[str] = None
    volume_ma_days: Optional[int] = None
    min_consecutive_limit: Optional[int] = None
    min_circulating_market_cap: Optional[float] = None
    max_circulating_market_cap: Optional[float] = None
    theme_type: Optional[str] = None
    sentiment_cycle: Optional[str] = None
    market_condition: Optional[str] = None

    # 止盈止损
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    trailing_stop: Optional[float] = None
    max_daily_loss: Optional[float] = None

    # 仓位管理
    max_positions: Optional[int] = None
    min_single_position: Optional[float] = None
    max_single_position: Optional[float] = None

    # 效果目标
    win_rate_target: Optional[float] = None
    profit_factor_target: Optional[float] = None
    max_drawdown_target: Optional[float] = None

    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    is_active: Optional[bool] = None

    # 7. 场景应对
    scenario_handling: Optional[Dict[str, Any]] = None

    # 8. 执行纪律
    discipline: Optional[Dict[str, Any]] = None

    iteration_history: Optional[str] = None


class StrategyResponse(StrategyBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
