from pydantic import BaseModel, ConfigDict
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
