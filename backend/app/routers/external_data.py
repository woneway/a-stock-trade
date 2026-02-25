from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from datetime import date, datetime
from typing import Optional, List

from app.database import engine
from app.models.external_data import StockBasic, StockQuote, StockKline


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/external", tags=["external-data"])


@router.get("/stocks")
def get_external_stocks(
    db: Session = Depends(get_db),
    market: str = None,
    limit: int = 100,
    offset: int = 0
):
    """获取股票基本信息列表"""
    statement = select(StockBasic)
    if market:
        statement = statement.where(StockBasic.market == market)
    statement = statement.offset(offset).limit(limit)
    return db.exec(statement).all()


@router.get("/stocks/{code}")
def get_external_stock(code: str, db: Session = Depends(get_db)):
    """获取单个股票基本信息"""
    stock = db.exec(select(StockBasic).where(StockBasic.code == code)).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.get("/stocks/{code}/quotes")
def get_stock_quotes(
    code: str,
    db: Session = Depends(get_db),
    trade_date: str = None,
    limit: int = 100
):
    """获取股票行情数据"""
    stock = db.exec(select(StockBasic).where(StockBasic.code == code)).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    statement = select(StockQuote).where(StockQuote.stock_id == stock.id)
    if trade_date:
        statement = statement.where(StockQuote.trade_date == trade_date)
    statement = statement.order_by(StockQuote.trade_date.desc()).limit(limit)
    return db.exec(statement).all()


@router.get("/stocks/{code}/klines")
def get_stock_klines(
    code: str,
    db: Session = Depends(get_db),
    start_date: str = None,
    end_date: str = None,
    limit: int = 500
):
    """获取股票K线数据用于回测"""
    stock = db.exec(select(StockBasic).where(StockBasic.code == code)).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    statement = select(StockKline).where(StockKline.stock_id == stock.id)
    if start_date:
        statement = statement.where(StockKline.trade_date >= start_date)
    if end_date:
        statement = statement.where(StockKline.trade_date <= end_date)
    statement = statement.order_by(StockKline.trade_date.asc()).limit(limit)
    return db.exec(statement).all()


@router.get("/quotes/today")
def get_today_quotes(
    db: Session = Depends(get_db),
    market: str = None,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "pct_chg",
    order: str = "desc"
):
    """获取今日行情排行"""
    today = date.today()

    statement = select(StockQuote, StockBasic).join(
        StockBasic, StockQuote.stock_id == StockBasic.id
    ).where(StockQuote.trade_date == today)

    if market:
        statement = statement.where(StockBasic.market == market)

    if sort_by == "pct_chg":
        if order == "desc":
            statement = statement.order_by(StockQuote.pct_chg.desc())
        else:
            statement = statement.order_by(StockQuote.pct_chg.asc())
    elif sort_by == "turnover_rate":
        if order == "desc":
            statement = statement.order_by(StockQuote.turnover_rate.desc())
        else:
            statement = statement.order_by(StockQuote.turnover_rate.asc())
    elif sort_by == "volume":
        if order == "desc":
            statement = statement.order_by(StockQuote.volume.desc())
        else:
            statement = statement.order_by(StockQuote.volume.asc())

    statement = statement.offset(offset).limit(limit)

    results = db.exec(statement).all()
    return [
        {
            **quote.model_dump(),
            "stock": stock.model_dump()
        }
        for quote, stock in results
    ]


@router.get("/quotes/limit-up")
def get_limit_up_quotes(
    db: Session = Depends(get_db),
    trade_date: str = None,
    limit: int = 100
):
    """获取涨停股票"""
    if trade_date:
        target_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
    else:
        target_date = date.today()

    statement = select(StockQuote, StockBasic).join(
        StockBasic, StockQuote.stock_id == StockBasic.id
    ).where(
        StockQuote.trade_date == target_date,
        StockQuote.pct_chg >= 9.9
    ).order_by(StockQuote.pct_chg.desc()).limit(limit)

    results = db.exec(statement).all()
    return [
        {
            **quote.model_dump(),
            "stock": stock.model_dump()
        }
        for quote, stock in results
    ]


@router.get("/stats")
def get_data_stats(db: Session = Depends(get_db)):
    """获取数据统计"""
    stock_basic_count = db.exec(select(func.count(StockBasic.id))).first() or 0
    stock_quote_count = db.exec(select(func.count(StockQuote.id))).first() or 0
    stock_kline_count = db.exec(select(func.count(StockKline.id))).first() or 0

    latest_quote_date = db.exec(
        select(func.max(StockQuote.trade_date))
    ).first()

    latest_kline_date = db.exec(
        select(func.max(StockKline.trade_date))
    ).first()

    return {
        "stock_basic_count": stock_basic_count,
        "stock_quote_count": stock_quote_count,
        "stock_kline_count": stock_kline_count,
        "latest_quote_date": latest_quote_date,
        "latest_kline_date": latest_kline_date
    }
