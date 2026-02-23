from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date
from typing import List, Optional

from app.database import engine
from app.models.market import (
    MarketIndex,
    LimitUpData,
    DragonListItem,
    CapitalFlow,
    NorthMoney,
    SectorStrength,
    News,
    SentimentPhase,
    TurnoverRank,
    LimitDownData,
    BoardPromotion,
)
from app.schemas.market import (
    MarketIndexCreate,
    MarketIndexResponse,
    LimitUpDataCreate,
    LimitUpDataResponse,
    DragonListItemCreate,
    DragonListItemResponse,
    CapitalFlowCreate,
    CapitalFlowResponse,
    NorthMoneyCreate,
    NorthMoneyResponse,
    SectorStrengthCreate,
    SectorStrengthResponse,
    NewsCreate,
    NewsResponse,
    SentimentPhaseCreate,
    SentimentPhaseResponse,
    TurnoverRankCreate,
    TurnoverRankResponse,
    LimitDownDataCreate,
    LimitDownDataResponse,
    BoardPromotionCreate,
    BoardPromotionResponse,
)


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/indices", response_model=List[MarketIndexResponse])
def get_market_indices(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(MarketIndex).where(MarketIndex.trade_date == trade_date)
    results = db.exec(statement).all()
    if not results:
        latest = db.exec(select(MarketIndex).order_by(MarketIndex.trade_date.desc()).limit(10)).all()
        return latest
    return results


@router.get("/limit-up", response_model=LimitUpDataResponse)
def get_limit_up_data(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(LimitUpData).where(LimitUpData.trade_date == trade_date)
    result = db.exec(statement).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return result


@router.get("/dragon-list", response_model=List[DragonListItemResponse])
def get_dragon_list(db: Session = Depends(get_db), trade_date: date = None, list_type: str = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(DragonListItem).where(DragonListItem.trade_date == trade_date)
    if list_type:
        statement = statement.where(DragonListItem.list_type == list_type)
    return db.exec(statement).all()


@router.get("/capital-flow", response_model=List[CapitalFlowResponse])
def get_capital_flow(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(CapitalFlow).where(CapitalFlow.trade_date == trade_date)
    return db.exec(statement).all()


@router.get("/north-money", response_model=NorthMoneyResponse)
def get_north_money(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(NorthMoney).where(NorthMoney.trade_date == trade_date)
    result = db.exec(statement).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return result


@router.get("/sector-strength", response_model=List[SectorStrengthResponse])
def get_sector_strength(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(SectorStrength).where(SectorStrength.trade_date == trade_date)
    return db.exec(statement).all()


@router.get("/news", response_model=List[NewsResponse])
def get_news(db: Session = Depends(get_db), limit: int = 10):
    statement = select(News).order_by(News.created_at.desc()).limit(limit)
    return db.exec(statement).all()


@router.get("/sentiment", response_model=SentimentPhaseResponse)
def get_sentiment(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(SentimentPhase).where(SentimentPhase.trade_date == trade_date)
    result = db.exec(statement).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return result


@router.post("/indices", response_model=MarketIndexResponse)
def create_market_index(item: MarketIndexCreate, db: Session = Depends(get_db)):
    db_item = MarketIndex.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.post("/sector-strength", response_model=SectorStrengthResponse)
def create_sector_strength(item: SectorStrengthCreate, db: Session = Depends(get_db)):
    db_item = SectorStrength.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.post("/sentiment", response_model=SentimentPhaseResponse)
def create_sentiment(item: SentimentPhaseCreate, db: Session = Depends(get_db)):
    existing = db.exec(
        select(SentimentPhase).where(SentimentPhase.trade_date == item.trade_date)
    ).first()
    if existing:
        for key, value in item.model_dump().items():
            if value is not None:
                setattr(existing, key, value)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    db_item = SentimentPhase.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/turnover-rank", response_model=List[TurnoverRankResponse])
def get_turnover_rank(db: Session = Depends(get_db), trade_date: date = None, limit: int = 10):
    if trade_date is None:
        trade_date = date.today()
    statement = (
        select(TurnoverRank)
        .where(TurnoverRank.trade_date == trade_date)
        .order_by(TurnoverRank.turnover_rate.desc())
        .limit(limit)
    )
    results = db.exec(statement).all()
    if not results:
        return []
    return results


@router.post("/turnover-rank", response_model=TurnoverRankResponse)
def create_turnover_rank(item: TurnoverRankCreate, db: Session = Depends(get_db)):
    db_item = TurnoverRank.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/limit-down", response_model=List[LimitDownDataResponse])
def get_limit_down_data(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(LimitDownData).where(LimitDownData.trade_date == trade_date)
    return db.exec(statement).all()


@router.post("/limit-down", response_model=LimitDownDataResponse)
def create_limit_down_data(item: LimitDownDataCreate, db: Session = Depends(get_db)):
    db_item = LimitDownData.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/board-promotion", response_model=List[BoardPromotionResponse])
def get_board_promotion(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = (
        select(BoardPromotion)
        .where(BoardPromotion.trade_date == trade_date)
        .order_by(BoardPromotion.success_rate.desc())
    )
    return db.exec(statement).all()


@router.post("/board-promotion", response_model=BoardPromotionResponse)
def create_board_promotion(item: BoardPromotionCreate, db: Session = Depends(get_db)):
    db_item = BoardPromotion.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
