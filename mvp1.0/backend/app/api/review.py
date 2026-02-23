from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.database import get_db
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, JSON

router = APIRouter()


class DailyReviewCreate(BaseModel):
    review_date: date
    limit_up_stocks: Optional[List[dict]] = None
    broken_stocks: Optional[List[dict]] = None
    yesterday_limit_up_performance: Optional[List[dict]] = None
    hot_sectors: Optional[List[str]] = None
    sentiment_cycle: Optional[str] = None
    tomorrow_strategy: Optional[dict] = None
    notes: Optional[str] = None


class DailyReviewUpdate(BaseModel):
    limit_up_stocks: Optional[List[dict]] = None
    broken_stocks: Optional[List[dict]] = None
    yesterday_limit_up_performance: Optional[List[dict]] = None
    hot_sectors: Optional[List[str]] = None
    sentiment_cycle: Optional[str] = None
    tomorrow_strategy: Optional[dict] = None
    notes: Optional[str] = None


class DailyReviewResponse(BaseModel):
    id: int
    review_date: date
    limit_up_stocks: Optional[List[dict]]
    broken_stocks: Optional[List[dict]]
    yesterday_limit_up_performance: Optional[List[dict]]
    hot_sectors: Optional[List[str]]
    sentiment_cycle: Optional[str]
    tomorrow_strategy: Optional[dict]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TargetStockPoolCreate(BaseModel):
    stock_code: str
    stock_name: str
    sector: Optional[str] = None
    reason: Optional[str] = None
    priority: Optional[str] = "normal"
    review_date: date


class TargetStockPoolResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    sector: Optional[str]
    reason: Optional[str]
    priority: str
    review_date: date
    created_at: datetime

    class Config:
        from_attributes = True


def create_tables():
    from app.database import Base, engine
    from sqlalchemy import Table, MetaData

    metadata = MetaData()

    review_table = Table('daily_reviews', metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('review_date', Date, nullable=False, unique=True),
        Column('limit_up_stocks', JSON),
        Column('broken_stocks', JSON),
        Column('yesterday_limit_up_performance', JSON),
        Column('hot_sectors', JSON),
        Column('sentiment_cycle', String(20)),
        Column('tomorrow_strategy', JSON),
        Column('notes', Text),
        Column('created_at', DateTime, default=datetime.now),
        Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now)
    )

    target_pool_table = Table('target_stock_pool', metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('stock_code', String(10), nullable=False),
        Column('stock_name', String(50), nullable=False),
        Column('sector', String(50)),
        Column('reason', Text),
        Column('priority', String(20), default="normal"),
        Column('review_date', Date, nullable=False),
        Column('created_at', DateTime, default=datetime.now)
    )

    metadata.create_all(bind=engine)


from sqlalchemy import Table, MetaData
from app.database import Base, engine

metadata = MetaData()

daily_reviews_table = Table('daily_reviews', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('review_date', Date, nullable=False, unique=True),
    Column('limit_up_stocks', JSON),
    Column('broken_stocks', JSON),
    Column('yesterday_limit_up_performance', JSON),
    Column('hot_sectors', JSON),
    Column('sentiment_cycle', String(20)),
    Column('tomorrow_strategy', JSON),
    Column('notes', Text),
    Column('created_at', DateTime, default=datetime.now),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now)
)

target_stock_pool_table = Table('target_stock_pool', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('stock_code', String(10), nullable=False),
    Column('stock_name', String(50), nullable=False),
    Column('sector', String(50)),
    Column('reason', Text),
    Column('priority', String(20), default="normal"),
    Column('review_date', Date, nullable=False),
    Column('created_at', DateTime, default=datetime.now)
)

metadata.create_all(bind=engine)


@router.get("/reviews", response_model=List[DailyReviewResponse])
def get_reviews(
    review_date: Optional[date] = None,
    sentiment_cycle: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.execute(
        "SELECT * FROM daily_reviews ORDER BY review_date DESC"
    ).fetchall()

    results = []
    for row in query:
        if (review_date and row.review_date != review_date) or \
           (sentiment_cycle and row.sentiment_cycle != sentiment_cycle):
            continue
        results.append(row)

    return results


@router.get("/reviews/{review_id}", response_model=DailyReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        "SELECT * FROM daily_reviews WHERE id = :id",
        {"id": review_id}
    ).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="复盘记录不存在")
    return result


@router.post("/reviews", response_model=DailyReviewResponse)
def create_review(review: DailyReviewCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        "SELECT * FROM daily_reviews WHERE review_date = :review_date",
        {"review_date": review.review_date}
    ).fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="该日期的复盘已存在")

    result = db.execute(
        """
        INSERT INTO daily_reviews
        (review_date, limit_up_stocks, broken_stocks, yesterday_limit_up_performance,
         hot_sectors, sentiment_cycle, tomorrow_strategy, notes)
        VALUES (:review_date, :limit_up_stocks, :broken_stocks, :yesterday_limit_up_performance,
                :hot_sectors, :sentiment_cycle, :tomorrow_strategy, :notes)
        """,
        {
            "review_date": review.review_date,
            "limit_up_stocks": review.limit_up_stocks,
            "broken_stocks": review.broken_stocks,
            "yesterday_limit_up_performance": review.yesterday_limit_up_performance,
            "hot_sectors": review.hot_sectors,
            "sentiment_cycle": review.sentiment_cycle,
            "tomorrow_strategy": review.tomorrow_strategy,
            "notes": review.notes
        }
    )
    db.commit()

    new_review = db.execute(
        "SELECT * FROM daily_reviews WHERE id = :id",
        {"id": result.lastrowid}
    ).fetchone()
    return new_review


@router.put("/reviews/{review_id}", response_model=DailyReviewResponse)
def update_review(review_id: int, review: DailyReviewUpdate, db: Session = Depends(get_db)):
    existing = db.execute(
        "SELECT * FROM daily_reviews WHERE id = :id",
        {"id": review_id}
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="复盘记录不存在")

    update_data = {k: v for k, v in review.model_dump().items() if v is not None}
    if not update_data:
        return existing

    set_clause = ", ".join([f"{k} = :{k}" for k in update_data.keys()])
    update_data["id"] = review_id

    db.execute(
        f"UPDATE daily_reviews SET {set_clause}, updated_at = NOW() WHERE id = :id",
        update_data
    )
    db.commit()

    updated = db.execute(
        "SELECT * FROM daily_reviews WHERE id = :id",
        {"id": review_id}
    ).fetchone()
    return updated


@router.get("/reviews/latest")
def get_latest_review(db: Session = Depends(get_db)):
    result = db.execute(
        "SELECT * FROM daily_reviews ORDER BY review_date DESC LIMIT 1"
    ).fetchone()
    if not result:
        return {"message": "暂无复盘记录"}
    return result


@router.get("/target-pool", response_model=List[TargetStockPoolResponse])
def get_target_pool(
    review_date: Optional[date] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = "SELECT * FROM target_stock_pool WHERE 1=1"
    params = {}

    if review_date:
        query += " AND review_date = :review_date"
        params["review_date"] = review_date
    if priority:
        query += " AND priority = :priority"
        params["priority"] = priority

    query += " ORDER BY created_at DESC"

    results = db.execute(query, params).fetchall()
    return results


@router.post("/target-pool", response_model=TargetStockPoolResponse)
def add_to_target_pool(stock: TargetStockPoolCreate, db: Session = Depends(get_db)):
    result = db.execute(
        """
        INSERT INTO target_stock_pool
        (stock_code, stock_name, sector, reason, priority, review_date)
        VALUES (:stock_code, :stock_name, :sector, :reason, :priority, :review_date)
        """,
        {
            "stock_code": stock.stock_code,
            "stock_name": stock.stock_name,
            "sector": stock.sector,
            "reason": stock.reason,
            "priority": stock.priority,
            "review_date": stock.review_date
        }
    )
    db.commit()

    new_stock = db.execute(
        "SELECT * FROM target_stock_pool WHERE id = :id",
        {"id": result.lastrowid}
    ).fetchone()
    return new_stock


@router.delete("/target-pool/{stock_id}")
def remove_from_target_pool(stock_id: int, db: Session = Depends(get_db)):
    existing = db.execute(
        "SELECT * FROM target_stock_pool WHERE id = :id",
        {"id": stock_id}
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="目标股不存在")

    db.execute("DELETE FROM target_stock_pool WHERE id = :id", {"id": stock_id})
    db.commit()
    return {"message": "已从目标股池移除"}
