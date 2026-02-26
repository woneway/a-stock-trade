from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Optional


class CandidateStock(BaseModel):
    code: str
    name: str
    buy_reason: str = ""
    sell_reason: str = ""
    priority: int = 0


class PrePlanBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    strategy_ids: Optional[str] = None
    selected_strategy: Optional[str] = None

    sentiment: Optional[str] = None
    external_signals: Optional[str] = None
    sectors: Optional[str] = None
    candidate_stocks: Optional[str] = None
    plan_basis: Optional[str] = None
    watch_indicators: Optional[str] = None
    watch_messages: Optional[str] = None

    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    entry_condition: Optional[str] = None
    exit_condition: Optional[str] = None

    status: str = "draft"

    plan_date: Optional[date] = None
    trade_date: Optional[date] = None


class PrePlanCreate(PrePlanBase):
    pass


class PrePlanUpdate(BaseModel):
    strategy_ids: Optional[str] = None
    selected_strategy: Optional[str] = None
    sentiment: Optional[str] = None
    external_signals: Optional[str] = None
    sectors: Optional[str] = None
    candidate_stocks: Optional[str] = None
    plan_basis: Optional[str] = None
    watch_indicators: Optional[str] = None
    watch_messages: Optional[str] = None
    stop_loss: Optional[float] = None
    position_size: Optional[float] = None
    entry_condition: Optional[str] = None
    exit_condition: Optional[str] = None
    status: Optional[str] = None
    plan_date: Optional[date] = None
    trade_date: Optional[date] = None


class PrePlanResponse(PrePlanBase):
    id: Optional[int] = None
    created_at: Optional[date] = None

    class Config:
        from_attributes = True


class PostReviewBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pre_plan_id: Optional[int] = None

    emotion_record: Optional[str] = None
    mistakes: Optional[str] = None
    lessons: Optional[str] = None
    trade_analysis: Optional[str] = None
    tomorrow_plan: Optional[str] = None

    planned_stocks: Optional[str] = None
    actual_trades_json: Optional[str] = None
    execution_rate: Optional[float] = None
    planned_pnl: Optional[float] = None
    unplanned_pnl: Optional[float] = None


class PostReviewCreate(PostReviewBase):
    trade_date: date


class PostReviewUpdate(BaseModel):
    pre_plan_id: Optional[int] = None
    emotion_record: Optional[str] = None
    mistakes: Optional[str] = None
    lessons: Optional[str] = None
    trade_analysis: Optional[str] = None
    tomorrow_plan: Optional[str] = None
    planned_stocks: Optional[str] = None
    actual_trades_json: Optional[str] = None
    execution_rate: Optional[float] = None
    planned_pnl: Optional[float] = None
    unplanned_pnl: Optional[float] = None


class PostReviewResponse(PostReviewBase):
    id: Optional[int] = None
    trade_date: date
    created_at: date

    class Config:
        from_attributes = True


class PostReviewAnalysis(BaseModel):
    planned_stocks: list[str] = []
    actual_traded_stocks: list[str] = []
    planned_executed: list[str] = []
    unplanned_executed: list[str] = []
    execution_rate: float = 0.0
    planned_pnl: float = 0.0
    unplanned_pnl: float = 0.0
    total_pnl: float = 0.0


class StrategyStats(BaseModel):
    strategy_name: str
    trade_count: int = 0
    win_count: int = 0
    loss_count: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    avg_pnl: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0


class IntelligentAnalysis(BaseModel):
    today_analysis: PostReviewAnalysis = PostReviewAnalysis()
    weekly_stats: dict = {}
    monthly_stats: dict = {}
    strategy_stats: list[StrategyStats] = []
    recommendations: list[str] = []


class HistoricalPlanBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    trade_date: Optional[date] = None
    pre_plan_id: Optional[int] = None
    post_review_id: Optional[int] = None
    status: Optional[str] = "completed"
    market_cycle: Optional[str] = None
    position_plan: Optional[str] = None
    planned_stock_count: Optional[int] = 0
    executed_stock_count: Optional[int] = 0
    execution_rate: Optional[float] = 0.0
    total_pnl: Optional[float] = 0.0


class HistoricalPlanCreate(HistoricalPlanBase):
    trade_date: date


class HistoricalPlanUpdate(BaseModel):
    trade_date: Optional[date] = None
    pre_plan_id: Optional[int] = None
    post_review_id: Optional[int] = None
    status: Optional[str] = None
    market_cycle: Optional[str] = None
    position_plan: Optional[str] = None
    planned_stock_count: Optional[int] = None
    executed_stock_count: Optional[int] = None
    execution_rate: Optional[float] = None
    total_pnl: Optional[float] = None


class HistoricalPlanResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: Optional[int] = None
    trade_date: Optional[date] = Field(default=None, alias="tradeDate")
    pre_plan_id: Optional[int] = Field(default=None, alias="prePlanId")
    post_review_id: Optional[int] = Field(default=None, alias="postReviewId")
    status: Optional[str] = "completed"
    market_cycle: Optional[str] = Field(default=None, alias="marketCycle")
    position_plan: Optional[str] = Field(default=None, alias="positionPlan")
    planned_stock_count: Optional[int] = Field(default=0, alias="plannedStockCount")
    executed_stock_count: Optional[int] = Field(default=0, alias="executedStockCount")
    execution_rate: Optional[float] = Field(default=0.0, alias="executionRate")
    total_pnl: Optional[float] = Field(default=0.0, alias="totalPnl")
    created_at: Optional[date] = Field(default=None, alias="createdAt")
    updated_at: Optional[date] = Field(default=None, alias="updatedAt")
