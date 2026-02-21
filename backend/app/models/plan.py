from datetime import date
from sqlmodel import Field, SQLModel
from typing import Optional


class PrePlan(SQLModel, table=True):
    __tablename__ = "pre_plans"

    id: Optional[int] = Field(default=None, primary_key=True)
    sentiment: str
    sectors: Optional[str] = None
    target_stocks: Optional[str] = Field(default=None, alias="targetStocks")
    plan_basis: Optional[str] = Field(default=None, alias="planBasis")
    trade_date: date = Field(index=True)
    created_at: date = Field(default_factory=date.today)

    class Config:
        populate_by_name = True


class PostReview(SQLModel, table=True):
    __tablename__ = "post_reviews"

    id: Optional[int] = Field(default=None, primary_key=True)
    emotion_record: Optional[str] = Field(default=None, alias="emotionRecord")
    mistakes: Optional[str] = None
    lessons: Optional[str] = None
    trade_analysis: Optional[str] = Field(default=None, alias="tradeAnalysis")
    tomorrow_plan: Optional[str] = Field(default=None, alias="tomorrowPlan")
    trade_date: date = Field(index=True)
    created_at: date = Field(default_factory=date.today)

    class Config:
        populate_by_name = True
