"""
统一数据API - 数据查询、同步
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from datetime import date, timedelta
from pydantic import BaseModel

from app.services.data_service import DataService, get_stock_list, DataCache

router = APIRouter(prefix="/api/data", tags=["data"])


class SyncRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str


@router.get("/stocks")
def get_stocks(market: Optional[str] = None, limit: int = 100):
    """获取股票列表"""
    stocks = get_stock_list()
    if market:
        stocks = [s for s in stocks if s['market'] == market]
    return stocks[:limit]


@router.get("/stocks/popular")
def get_popular_stocks():
    """获取热门股票列表"""
    return [
        {"code": "600519", "name": "贵州茅台", "market": "sh"},
        {"code": "000858", "name": "五粮液", "market": "sz"},
        {"code": "601318", "name": "中国平安", "market": "sh"},
        {"code": "600036", "name": "招商银行", "market": "sh"},
        {"code": "000001", "name": "平安银行", "market": "sz"},
        {"code": "300750", "name": "宁德时代", "market": "sz"},
        {"code": "002594", "name": "比亚迪", "market": "sz"},
        {"code": "600900", "name": "长江电力", "market": "sh"},
        {"code": "601888", "name": "中国中免", "market": "sh"},
        {"code": "000333", "name": "美的集团", "market": "sz"},
        {"code": "002371", "name": "北方华创", "market": "sz"},
        {"code": "688981", "name": "中芯国际", "market": "sh"},
        {"code": "300308", "name": "中际旭创", "market": "sz"},
        {"code": "300502", "name": "新易盛", "market": "sz"},
        {"code": "600030", "name": "中信证券", "market": "sh"},
        {"code": "300059", "name": "东方财富", "market": "sz"},
    ]


@router.get("/klines/{stock_code}")
def get_klines(
    stock_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    adjust: str = "qfq"
):
    """
    获取K线数据
    优先级：缓存 > 数据库 > akshare
    """
    if not start_date:
        start_date = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")

    df = DataService.get_kline_dataframe(stock_code, start_date, end_date)

    if df is None or df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"未找到股票 {stock_code} 的K线数据"
        )

    return {
        "stock_code": stock_code,
        "start_date": start_date,
        "end_date": end_date,
        "count": len(df),
        "data": df.to_dict('records')
    }


@router.post("/sync")
def sync_stock_data(request: SyncRequest):
    """同步股票数据到数据库"""
    result = DataService.sync_stock_to_database(
        stock_code=request.stock_code,
        start_date=request.start_date,
        end_date=request.end_date
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))

    # 清除缓存
    DataService.clear_cache()

    return result


@router.post("/cache/clear")
def clear_cache():
    """清除数据缓存"""
    DataService.clear_cache()
    return {"status": "success", "message": "缓存已清除"}


@router.get("/stats")
def get_data_stats():
    """获取数据统计"""
    from sqlmodel import select, func
    from app.database import engine
    from app.models.external_data import StockBasic, StockKline

    with Session(engine) as session:
        stock_count = session.exec(func.count(StockBasic.id)).first() or 0
        kline_count = session.exec(func.count(StockKline.id)).first() or 0

        latest_kline = session.exec(
            select(func.max(StockKline.trade_date))
        ).first()

    return {
        "stock_count": stock_count,
        "kline_count": kline_count,
        "latest_kline_date": latest_kline
    }


# 修复导入
from sqlmodel import Session
