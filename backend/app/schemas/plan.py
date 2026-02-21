from pydantic import BaseModel
from datetime import date
from typing import Optional


class PrePlanBase(BaseModel):
    sentiment: str
    sectors: Optional[str] = None
    target_stocks: Optional[str] = None
    plan_basis: Optional[str] = None


class PrePlanCreate(PrePlanBase):
    trade_date: date


class PrePlanUpdate(BaseModel):
    sentiment: Optional[str] = None
    sectors: Optional[str] = None
    target_stocks: Optional[str] = None
    plan_basis: Optional[str] = None


class PrePlanResponse(PrePlanBase):
    id: Optional[int] = None
    trade_date: date
    created_at: date

    class Config:
        from_attributes = True


class PostReviewBase(BaseModel):
    emotion_record: Optional[str] = None
    mistakes: Optional[str] = None
    lessons: Optional[str] = None
    trade_analysis: Optional[str] = None
    tomorrow_plan: Optional[str] = None


class PostReviewCreate(PostReviewBase):
    trade_date: date


class PostReviewUpdate(BaseModel):
    emotion_record: Optional[str] = None
    mistakes: Optional[str] = None
    lessons: Optional[str] = None
    trade_analysis: Optional[str] = None
    tomorrow_plan: Optional[str] = None


class PostReviewResponse(PostReviewBase):
    id: Optional[int] = None
    trade_date: date
    created_at: date

    class Config:
        from_attributes = True
