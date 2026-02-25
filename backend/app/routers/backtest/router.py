from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import Optional, List
from datetime import date, timedelta
from pydantic import BaseModel

from app.database import engine
from app.routers.backtest.engine import BacktestEngine, get_kline_data


def get_db():
    with Session(engine) as session:
        yield session


router = APIRouter(prefix="/api/backtest", tags=["backtest"])


class BacktestRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    initial_capital: float = 100000
    strategy_type: str = "ma_cross"


class BacktestResult(BaseModel):
    initial_capital: float
    final_value: float
    total_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float


@router.post("/run", response_model=BacktestResult)
def run_backtest(
    request: BacktestRequest,
    db: Session = Depends(get_db)
):
    """运行回测"""
    klines = get_kline_data(
        db,
        request.stock_code,
        request.start_date,
        request.end_date
    )

    if not klines:
        raise HTTPException(
            status_code=404,
            detail=f"未找到股票 {request.stock_code} 的K线数据"
        )

    engine = BacktestEngine(request.initial_capital)

    for kline in klines:
        if not kline.close:
            continue

        if len(engine.positions) == 0:
            engine.buy(
                request.stock_code,
                kline.close,
                100,
                kline.trade_date
            )
        else:
            engine.sell(
                request.stock_code,
                kline.close,
                100,
                kline.trade_date
            )

    results = engine.get_results()
    return BacktestResult(**results)


@router.get("/stocks")
def get_backtest_stocks(
    db: Session = Depends(get_db),
    limit: int = 50
):
    """获取可回测的股票列表"""
    from app.models.external_data import StockBasic
    from sqlmodel import select

    stocks = db.exec(
        select(StockBasic).where(
            StockBasic.list_status == "L"
        ).limit(limit)
    ).all()

    return [
        {
            "code": s.code,
            "name": s.name,
            "market": s.market,
        }
        for s in stocks
    ]


@router.get("/klines/{stock_code}")
def get_backtest_klines(
    stock_code: str,
    db: Session = Depends(get_db),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 500
):
    """获取回测用K线数据"""
    if not start_date:
        start_date = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    klines = get_kline_data(db, stock_code, start_date, end_date)

    return [
        {
            "date": k.trade_date,
            "open": k.open,
            "high": k.high,
            "low": k.low,
            "close": k.close,
            "volume": k.volume,
            "pct_chg": k.pct_chg,
        }
        for k in klines[:limit]
    ]
