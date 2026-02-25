from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Any
from datetime import date, datetime
import json
from pydantic import BaseModel
from app.database import get_db
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, JSON

router = APIRouter()


def to_json(value: Any) -> str:
    """将值转换为JSON字符串"""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def from_json(value: Any) -> Any:
    """将JSON字符串转换为Python对象"""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def convert_review_row(row) -> dict:
    """将数据库行转换为字典，处理JSON字段"""
    if row is None:
        return None
    result = dict(row._mapping) if hasattr(row, '_mapping') else dict(row)
    # 转换JSON字段
    json_fields = ['limit_up_stocks', 'broken_stocks', 'yesterday_limit_up_performance',
                   'hot_sectors', 'main_sectors', 'tomorrow_strategy']
    for field in json_fields:
        if field in result:
            result[field] = from_json(result[field])
    # 处理datetime字段
    if result.get('created_at') is None:
        result['created_at'] = datetime.now()
    if result.get('updated_at') is None:
        result['updated_at'] = datetime.now()
    return result


class DailyReviewCreate(BaseModel):
    review_date: date
    limit_up_stocks: Optional[List[dict]] = None
    broken_stocks: Optional[List[dict]] = None
    yesterday_limit_up_performance: Optional[List[dict]] = None
    hot_sectors: Optional[List[str]] = None

    # 新增字段 - 第一阶段
    market_cycle: Optional[str] = None  # 情绪周期
    position_advice: Optional[str] = None  # 仓位建议
    risk_warning: Optional[str] = None  # 风险警示

    # 扩展字段 - 第二阶段
    broken_plate_ratio: Optional[float] = None  # 炸板率
    highest_board: Optional[int] = None  # 最高连板
    up_count: Optional[int] = None  # 上涨家数
    turnover: Optional[float] = None  # 成交额(亿)
    above_20ma: Optional[bool] = None  # 大盘是否在20日线
    index_trend: Optional[str] = None  # 指数趋势
    main_sectors: Optional[List[str]] = None  # 主流板块

    tomorrow_strategy: Optional[dict] = None
    notes: Optional[str] = None


class DailyReviewUpdate(BaseModel):
    limit_up_stocks: Optional[List[dict]] = None
    broken_stocks: Optional[List[dict]] = None
    yesterday_limit_up_performance: Optional[List[dict]] = None
    hot_sectors: Optional[List[str]] = None
    market_cycle: Optional[str] = None
    position_advice: Optional[str] = None
    risk_warning: Optional[str] = None
    broken_plate_ratio: Optional[float] = None
    highest_board: Optional[int] = None
    up_count: Optional[int] = None
    turnover: Optional[float] = None
    above_20ma: Optional[bool] = None
    index_trend: Optional[str] = None
    main_sectors: Optional[List[str]] = None
    tomorrow_strategy: Optional[dict] = None
    notes: Optional[str] = None


class DailyReviewResponse(BaseModel):
    id: int
    review_date: date
    limit_up_stocks: Optional[List[dict]]
    broken_stocks: Optional[List[dict]]
    yesterday_limit_up_performance: Optional[List[dict]]
    hot_sectors: Optional[List[str]]
    market_cycle: Optional[str]
    position_advice: Optional[str]
    risk_warning: Optional[str]
    broken_plate_ratio: Optional[float]
    highest_board: Optional[int]
    up_count: Optional[int]
    turnover: Optional[float]
    above_20ma: Optional[bool]
    index_trend: Optional[str]
    main_sectors: Optional[List[str]]
    tomorrow_strategy: Optional[dict]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class DailyReviewListItem(BaseModel):
    """复盘列表简要信息"""
    id: int
    review_date: date
    market_cycle: Optional[str]
    position_advice: Optional[str]
    risk_warning: Optional[str]
    hot_sectors: Optional[List[str]]
    up_count: Optional[int]
    turnover: Optional[float]
    created_at: datetime

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
        Column('market_cycle', String(20)),
        Column('position_advice', String(20)),
        Column('risk_warning', String(200)),
        Column('broken_plate_ratio', Float),
        Column('highest_board', Integer),
        Column('up_count', Integer),
        Column('turnover', Float),
        Column('above_20ma', String(10)),
        Column('index_trend', String(20)),
        Column('main_sectors', JSON),
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
    Column('market_cycle', String(20)),
    Column('position_advice', String(20)),
    Column('risk_warning', String(200)),
    Column('broken_plate_ratio', Float),
    Column('highest_board', Integer),
    Column('up_count', Integer),
    Column('turnover', Float),
    Column('above_20ma', String(10)),
    Column('index_trend', String(20)),
    Column('main_sectors', JSON),
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
    market_cycle: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取复盘列表，支持日期范围筛选和分页"""
    query = "SELECT * FROM daily_reviews WHERE 1=1"
    params = {}

    if review_date:
        query += " AND review_date = :review_date"
        params["review_date"] = review_date
    if market_cycle:
        query += " AND market_cycle = :market_cycle"
        params["market_cycle"] = market_cycle
    if start_date:
        query += " AND review_date >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND review_date <= :end_date"
        params["end_date"] = end_date

    query += " ORDER BY review_date DESC"

    # 分页
    offset = (page - 1) * page_size
    query += f" LIMIT {page_size} OFFSET {offset}"

    results = db.execute(text(query), params).fetchall()
    return [convert_review_row(r) for r in results]


@router.get("/reviews/count")
def get_reviews_count(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取复盘总数"""
    query = "SELECT COUNT(*) as total FROM daily_reviews WHERE 1=1"
    params = {}

    if start_date:
        query += " AND review_date >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND review_date <= :end_date"
        params["end_date"] = end_date

    result = db.execute(text(query), params).fetchone()
    return {"total": result.total}


@router.get("/reviews/{review_id}", response_model=DailyReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM daily_reviews WHERE id = :id"),
        {"id": review_id}
    ).fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="复盘记录不存在")
    return convert_review_row(result)


@router.post("/reviews", response_model=DailyReviewResponse)
def create_review(review: DailyReviewCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        text("SELECT * FROM daily_reviews WHERE review_date = :review_date"),
        {"review_date": review.review_date}
    ).fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="该日期的复盘已存在")

    result = db.execute(
        text("""
        INSERT INTO daily_reviews
        (review_date, limit_up_stocks, broken_stocks, yesterday_limit_up_performance,
         hot_sectors, market_cycle, tomorrow_strategy, notes)
        VALUES (:review_date, :limit_up_stocks, :broken_stocks, :yesterday_limit_up_performance,
                :hot_sectors, :market_cycle, :tomorrow_strategy, :notes)
        """),
        {
            "review_date": review.review_date,
            "limit_up_stocks": to_json(review.limit_up_stocks),
            "broken_stocks": to_json(review.broken_stocks),
            "yesterday_limit_up_performance": to_json(review.yesterday_limit_up_performance),
            "hot_sectors": to_json(review.hot_sectors),
            "market_cycle": review.market_cycle,
            "tomorrow_strategy": to_json(review.tomorrow_strategy),
            "notes": review.notes
        }
    )
    db.commit()

    new_review = db.execute(
        text("SELECT * FROM daily_reviews WHERE id = :id"),
        {"id": result.lastrowid}
    ).fetchone()
    return convert_review_row(new_review)


@router.put("/reviews/{review_id}", response_model=DailyReviewResponse)
def update_review(review_id: int, review: DailyReviewUpdate, db: Session = Depends(get_db)):
    existing = db.execute(
        text("SELECT * FROM daily_reviews WHERE id = :id"),
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
        text(f"UPDATE daily_reviews SET {set_clause}, updated_at = NOW() WHERE id = :id"),
        update_data
    )
    db.commit()

    updated = db.execute(
        text("SELECT * FROM daily_reviews WHERE id = :id"),
        {"id": review_id}
    ).fetchone()
    return convert_review_row(updated)


@router.get("/reviews/latest")
def get_latest_review(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM daily_reviews ORDER BY review_date DESC LIMIT 1")
    ).fetchone()
    if not result:
        return {"message": "暂无复盘记录"}
    return convert_review_row(result)


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

    results = db.execute(text(query), params).fetchall()
    return results


@router.post("/target-pool", response_model=TargetStockPoolResponse)
def add_to_target_pool(stock: TargetStockPoolCreate, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
        INSERT INTO target_stock_pool
        (stock_code, stock_name, sector, reason, priority, review_date)
        VALUES (:stock_code, :stock_name, :sector, :reason, :priority, :review_date)
        """),
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
        text("SELECT * FROM target_stock_pool WHERE id = :id"),
        {"id": result.lastrowid}
    ).fetchone()
    return new_stock


@router.delete("/target-pool/{stock_id}")
def remove_from_target_pool(stock_id: int, db: Session = Depends(get_db)):
    existing = db.execute(
        text("SELECT * FROM target_stock_pool WHERE id = :id"),
        {"id": stock_id}
    ).fetchone()

    if not existing:
        raise HTTPException(status_code=404, detail="目标股不存在")

    db.execute(text("DELETE FROM target_stock_pool WHERE id = :id"), {"id": stock_id})
    db.commit()
    return {"message": "已从目标股池移除"}
