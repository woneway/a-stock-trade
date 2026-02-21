from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import date

from app.database import engine
from app.models.plan import PrePlan, PostReview
from app.schemas.plan import (
    PrePlanCreate,
    PrePlanUpdate,
    PrePlanResponse,
    PostReviewCreate,
    PostReviewUpdate,
    PostReviewResponse,
)


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/plan", tags=["plan"])


@router.get("/pre", response_model=PrePlanResponse)
def get_pre_plan(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(PrePlan).where(PrePlan.trade_date == trade_date)
    result = db.exec(statement).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return result


@router.post("/pre", response_model=PrePlanResponse)
def create_pre_plan(item: PrePlanCreate, db: Session = Depends(get_db)):
    existing = db.exec(
        select(PrePlan).where(PrePlan.trade_date == item.trade_date)
    ).first()
    
    if existing:
        for key, value in item.model_dump().items():
            if value is not None:
                setattr(existing, key, value)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    db_item = PrePlan.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/pre", response_model=PrePlanResponse)
def update_pre_plan(item: PrePlanUpdate, db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    
    db_item = db.exec(
        select(PrePlan).where(PrePlan.trade_date == trade_date)
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Pre plan not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/post", response_model=PostReviewResponse)
def get_post_review(db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    statement = select(PostReview).where(PostReview.trade_date == trade_date)
    result = db.exec(statement).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return result


@router.post("/post", response_model=PostReviewResponse)
def create_post_review(item: PostReviewCreate, db: Session = Depends(get_db)):
    existing = db.exec(
        select(PostReview).where(PostReview.trade_date == item.trade_date)
    ).first()
    
    if existing:
        for key, value in item.model_dump().items():
            if value is not None:
                setattr(existing, key, value)
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    db_item = PostReview.model_validate(item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/post", response_model=PostReviewResponse)
def update_post_review(item: PostReviewUpdate, db: Session = Depends(get_db), trade_date: date = None):
    if trade_date is None:
        trade_date = date.today()
    
    db_item = db.exec(
        select(PostReview).where(PostReview.trade_date == trade_date)
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Post review not found")
    
    item_data = item.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
