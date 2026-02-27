"""
游资数据API
- 优先从本地数据库查询
- 本地无数据时自动从 akshare 获取并存储
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel

from app.services.yz_data_service import YzDataService

router = APIRouter(prefix="/api/yz", tags=["游资数据"])


class AkshareExecuteRequest(BaseModel):
    func_name: str
    params: dict = {}


@router.get("/spot")
def get_stock_spot(force_refresh: bool = False):
    """获取A股实时行情"""
    try:
        data = YzDataService.get_stock_spot(force_refresh=force_refresh)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/limit-up")
def get_limit_up(date: Optional[str] = None, force_refresh: bool = False):
    """获取涨停板数据"""
    try:
        data = YzDataService.get_limit_up(trade_date=date, force_refresh=force_refresh)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/zt-pool")
def get_zt_pool(date: Optional[str] = None, force_refresh: bool = False):
    """获取涨停板池"""
    try:
        data = YzDataService.get_zt_pool(trade_date=date, force_refresh=force_refresh)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fund-flow/{stock_code}")
def get_individual_fund_flow(
    stock_code: str,
    market: str = "上海A股",
    force_refresh: bool = False
):
    """获取个股资金流向"""
    try:
        data = YzDataService.get_individual_fund_flow(
            stock_code=stock_code,
            market=market,
            force_refresh=force_refresh
        )
        return {"stock_code": stock_code, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sector-fund-flow")
def get_sector_fund_flow(
    indicator: str = "今日",
    sector_type: str = "行业资金流",
    force_refresh: bool = False
):
    """获取板块资金流向"""
    try:
        data = YzDataService.get_sector_fund_flow(
            indicator=indicator,
            sector_type=sector_type,
            force_refresh=force_refresh
        )
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lhb/detail")
def get_lhb_detail(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    force_refresh: bool = False
):
    """获取龙虎榜详情"""
    try:
        data = YzDataService.get_lhb_detail(
            start_date=start_date,
            end_date=end_date,
            force_refresh=force_refresh
        )
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lhb/yytj")
def get_lhb_yytj(force_refresh: bool = False):
    """获取游资追踪数据"""
    try:
        data = YzDataService.get_lhb_yytj(force_refresh=force_refresh)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lhb/yyb")
def get_lhb_yyb(force_refresh: bool = False):
    """获取龙虎榜营业部数据"""
    try:
        data = YzDataService.get_lhb_yyb(force_refresh=force_refresh)
        return {"count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
def sync_yz_data(data_type: str, trade_date: Optional[str] = None):
    """手动触发数据同步"""
    try:
        result = {"status": "success", "data_type": data_type}

        if data_type == "spot":
            data = YzDataService.get_stock_spot(force_refresh=True)
            result["count"] = len(data)
        elif data_type == "limit_up":
            data = YzDataService.get_limit_up(trade_date=trade_date, force_refresh=True)
            result["count"] = len(data)
        elif data_type == "zt_pool":
            data = YzDataService.get_zt_pool(trade_date=trade_date, force_refresh=True)
            result["count"] = len(data)
        elif data_type == "sector_fund_flow":
            data = YzDataService.get_sector_fund_flow(force_refresh=True)
            result["count"] = len(data)
        elif data_type == "lhb_detail":
            data = YzDataService.get_lhb_detail(force_refresh=True)
            result["count"] = len(data)
        elif data_type == "lhb_yytj":
            data = YzDataService.get_lhb_yytj(force_refresh=True)
            result["count"] = len(data)
        elif data_type == "lhb_yyb":
            data = YzDataService.get_lhb_yyb(force_refresh=True)
            result["count"] = len(data)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown data_type: {data_type}")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
