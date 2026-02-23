from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional


class StrategyBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: Optional[str] = None
    stock_selection_logic: Optional[str] = None
    watch_signals: Optional[str] = None
    entry_condition: Optional[str] = None
    exit_condition: Optional[str] = None
    position_condition: Optional[str] = None
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
    take_profit_1: Optional[float] = 7.0
    take_profit_2: Optional[float] = 15.0
    trailing_stop: Optional[float] = 5.0
    max_daily_loss: Optional[float] = -5.0
    max_positions: Optional[int] = 3
    min_single_position: Optional[float] = 10.0
    max_single_position: Optional[float] = 25.0
    win_rate_target: Optional[float] = None
    profit_factor_target: Optional[float] = None
    max_drawdown_target: Optional[float] = None
    stop_loss: float = 6.0
    position_size: float = 20.0
    is_active: bool = True
    iteration_history: Optional[str] = None


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stock_selection_logic: Optional[str] = None
    watch_signals: Optional[str] = None
    entry_condition: Optional[str] = None
    exit_condition: Optional[str] = None
    position_condition: Optional[str] = None
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
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    trailing_stop: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_positions: Optional[int] = None
    min_single_position: Optional[float] = None
    max_single_position: Optional[float] = None
    win_rate_target: Optional[float] = None
    profit_factor_target: Optional[float] = None
    max_drawdown_target: Optional[float] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    is_active: Optional[bool] = None
    iteration_history: Optional[str] = None


class StrategyResponse(StrategyBase):
    id: Optional[int] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
