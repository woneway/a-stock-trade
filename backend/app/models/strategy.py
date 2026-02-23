from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class Strategy(SQLModel, table=True):
    __tablename__ = "strategies"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None

    stock_selection_logic: Optional[str] = Field(default=None, alias="stockSelectionLogic")
    watch_signals: Optional[str] = Field(default=None, alias="watchSignals")
    entry_condition: Optional[str] = Field(default=None, alias="entryCondition")
    exit_condition: Optional[str] = Field(default=None, alias="exitCondition")
    position_condition: Optional[str] = Field(default=None, alias="positionCondition")

    min_turnover_rate: Optional[float] = Field(default=None, alias="minTurnoverRate")
    max_turnover_rate: Optional[float] = Field(default=None, alias="maxTurnoverRate")
    min_volume_ratio: Optional[float] = Field(default=None, alias="minVolumeRatio")
    max_volume_ratio: Optional[float] = Field(default=None, alias="maxVolumeRatio")
    min_market_cap: Optional[float] = Field(default=None, alias="minMarketCap")
    max_market_cap: Optional[float] = Field(default=None, alias="maxMarketCap")
    min_price: Optional[float] = Field(default=None, alias="minPrice")
    max_price: Optional[float] = Field(default=None, alias="maxPrice")
    limit_up_days: Optional[int] = Field(default=None, alias="limitUpDays")
    min_amplitude: Optional[float] = Field(default=None, alias="minAmplitude")
    max_amplitude: Optional[float] = Field(default=None, alias="maxAmplitude")
    ma_days: Optional[str] = Field(default=None, alias="maDays")
    volume_ma_days: Optional[int] = Field(default=None, alias="volumeMaDays")

    min_consecutive_limit: Optional[int] = Field(default=None, alias="minConsecutiveLimit")
    min_circulating_market_cap: Optional[float] = Field(default=None, alias="minCirculatingMarketCap")
    max_circulating_market_cap: Optional[float] = Field(default=None, alias="maxCirculatingMarketCap")

    theme_type: Optional[str] = Field(default=None, alias="themeType")
    sentiment_cycle: Optional[str] = Field(default=None, alias="sentimentCycle")
    market_condition: Optional[str] = Field(default=None, alias="marketCondition")

    take_profit_1: Optional[float] = Field(default=7.0, alias="takeProfit1")
    take_profit_2: Optional[float] = Field(default=15.0, alias="takeProfit2")
    trailing_stop: Optional[float] = Field(default=5.0, alias="trailingStop")
    max_daily_loss: Optional[float] = Field(default=-5.0, alias="maxDailyLoss")

    max_positions: Optional[int] = Field(default=3, alias="maxPositions")
    min_single_position: Optional[float] = Field(default=10.0, alias="minSinglePosition")
    max_single_position: Optional[float] = Field(default=25.0, alias="maxSinglePosition")

    win_rate_target: Optional[float] = Field(default=None, alias="winRateTarget")
    profit_factor_target: Optional[float] = Field(default=None, alias="profitFactorTarget")
    max_drawdown_target: Optional[float] = Field(default=None, alias="maxDrawdownTarget")

    stop_loss: float = Field(default=6.0, alias="stopLoss")
    position_size: float = Field(default=20.0, alias="positionSize")
    is_active: bool = Field(default=True, alias="isActive")

    iteration_history: Optional[str] = Field(default=None, alias="iterationHistory")

    created_at: date = Field(default_factory=date.today, alias="createdAt")
    updated_at: date = Field(default_factory=date.today, alias="updatedAt")

    class Config:
        populate_by_name = True
