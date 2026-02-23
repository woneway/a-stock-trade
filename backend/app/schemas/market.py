from pydantic import BaseModel
from datetime import date
from typing import Optional


class MarketIndexBase(BaseModel):
    index_name: str
    points: float
    change: float
    support: float
    resistance: float


class MarketIndexCreate(MarketIndexBase):
    trade_date: date


class MarketIndexResponse(MarketIndexBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class LimitUpDataBase(BaseModel):
    total: int
    yesterday: int
    new_high: int
    continuation: int


class LimitUpDataCreate(LimitUpDataBase):
    trade_date: date


class LimitUpDataResponse(LimitUpDataBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class DragonListItemBase(BaseModel):
    code: str
    name: str
    reason: str
    institution: str
    list_type: str


class DragonListItemCreate(DragonListItemBase):
    trade_date: date


class DragonListItemResponse(DragonListItemBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class CapitalFlowBase(BaseModel):
    sector: str
    amount: float
    flow_type: str
    stocks: Optional[str] = None


class CapitalFlowCreate(CapitalFlowBase):
    trade_date: date


class CapitalFlowResponse(CapitalFlowBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class NorthMoneyBase(BaseModel):
    inflow: float
    outflow: float
    net: float


class NorthMoneyCreate(NorthMoneyBase):
    trade_date: date


class NorthMoneyResponse(NorthMoneyBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class SectorStrengthBase(BaseModel):
    name: str
    strength: int
    trend: str
    avg_change: float


class SectorStrengthCreate(SectorStrengthBase):
    trade_date: date


class SectorStrengthResponse(SectorStrengthBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class NewsBase(BaseModel):
    news_type: str
    content: str


class NewsCreate(NewsBase):
    created_at: date


class NewsResponse(NewsBase):
    id: Optional[int] = None
    created_at: date

    class Config:
        from_attributes = True


class SentimentPhaseBase(BaseModel):
    phase: str
    description: str
    advice: str


class SentimentPhaseCreate(SentimentPhaseBase):
    trade_date: date


class SentimentPhaseResponse(SentimentPhaseBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class TurnoverRankBase(BaseModel):
    code: str
    name: str
    turnover_rate: float
    amount: float
    change: float
    sector: Optional[str] = None


class TurnoverRankCreate(TurnoverRankBase):
    trade_date: date


class TurnoverRankResponse(TurnoverRankBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class LimitDownDataBase(BaseModel):
    total: int
    sector: str
    stocks: Optional[str] = None


class LimitDownDataCreate(LimitDownDataBase):
    trade_date: date


class LimitDownDataResponse(LimitDownDataBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True


class BoardPromotionBase(BaseModel):
    sector: str
    first_board: int
    second_board: int
    success_rate: float


class BoardPromotionCreate(BoardPromotionBase):
    trade_date: date


class BoardPromotionResponse(BoardPromotionBase):
    id: Optional[int] = None
    trade_date: date

    class Config:
        from_attributes = True
