from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class PrePlan(SQLModel, table=True):
    __tablename__ = "pre_plans"

    id: Optional[int] = Field(default=None, primary_key=True)

    strategy_ids: Optional[str] = Field(default=None, alias="strategyIds")
    selected_strategy: Optional[str] = Field(default=None, alias="selectedStrategy")

    sentiment: Optional[str] = None
    external_signals: Optional[str] = Field(default=None, alias="externalSignals")

    sectors: Optional[str] = None

    candidate_stocks: Optional[str] = Field(default=None, alias="candidateStocks")

    plan_basis: Optional[str] = Field(default=None, alias="planBasis")

    watch_indicators: Optional[str] = Field(default=None, alias="watchIndicators")
    watch_messages: Optional[str] = Field(default=None, alias="watchMessages")

    stop_loss: Optional[float] = Field(default=None, alias="stopLoss")
    position_size: Optional[float] = Field(default=None, alias="positionSize")
    entry_condition: Optional[str] = Field(default=None, alias="entryCondition")
    exit_condition: Optional[str] = Field(default=None, alias="exitCondition")

    status: str = Field(default="draft", alias="status")

    plan_date: date = Field(index=True, alias="planDate")
    trade_date: date = Field(index=True, alias="tradeDate")

    created_at: date = Field(default_factory=date.today, alias="createdAt")

    class Config:
        populate_by_name = True


class PostReview(SQLModel, table=True):
    __tablename__ = "post_reviews"

    id: Optional[int] = Field(default=None, primary_key=True)

    pre_plan_id: Optional[int] = Field(default=None, foreign_key="pre_plans.id", alias="prePlanId")

    emotion_record: Optional[str] = Field(default=None, alias="emotionRecord")
    mistakes: Optional[str] = None
    lessons: Optional[str] = None
    trade_analysis: Optional[str] = Field(default=None, alias="tradeAnalysis")
    tomorrow_plan: Optional[str] = Field(default=None, alias="tomorrowPlan")

    planned_stocks: Optional[str] = Field(default=None, alias="plannedStocks")
    actual_trades_json: Optional[str] = Field(default=None, alias="actualTradesJson")
    execution_rate: Optional[float] = Field(default=None, alias="executionRate")
    planned_pnl: Optional[float] = Field(default=None, alias="plannedPnl")
    unplanned_pnl: Optional[float] = Field(default=None, alias="unplannedPnl")

    trade_date: date = Field(index=True)
    created_at: date = Field(default_factory=date.today)

    class Config:
        populate_by_name = True


class HistoricalPlan(SQLModel, table=True):
    __tablename__ = "historical_plans"

    id: Optional[int] = Field(default=None, primary_key=True)

    trade_date: date = Field(index=True, alias="tradeDate")

    pre_plan_id: Optional[int] = Field(default=None, foreign_key="pre_plans.id", alias="prePlanId")
    post_review_id: Optional[int] = Field(default=None, foreign_key="post_reviews.id", alias="postReviewId")

    status: str = Field(default="completed", alias="status")
    market_cycle: Optional[str] = Field(default=None, alias="marketCycle")
    position_plan: Optional[str] = Field(default=None, alias="positionPlan")

    planned_stock_count: Optional[int] = Field(default=0, alias="plannedStockCount")
    executed_stock_count: Optional[int] = Field(default=0, alias="executedStockCount")
    execution_rate: Optional[float] = Field(default=0.0, alias="executionRate")

    total_pnl: Optional[float] = Field(default=0.0, alias="totalPnl")

    created_at: date = Field(default_factory=date.today, alias="createdAt")
    updated_at: date = Field(default_factory=date.today, alias="updatedAt")

    class Config:
        populate_by_name = True
