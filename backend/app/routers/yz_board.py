"""
游资看板 API
调用 DataService 获取 AKShare 数据
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta

from app.services.data_service import DataService

router = APIRouter(prefix="/api/yz", tags=["游资看板"])


def _get_today() -> str:
    return datetime.now().strftime("%Y%m%d")


def _get_yesterday() -> str:
    return (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")


# ============ 交易状态 ============

@router.get("/trade-status")
def get_trade_status():
    """获取交易状态"""
    from app.services.cache_service import CacheService

    is_trade_day = CacheService.is_trading_day(_get_today())

    # 简单判断交易时间 (9:30-15:00)
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    is_trade_time = False
    if is_trade_day:
        if 9 < hour < 15:
            is_trade_time = True
        elif hour == 9 and minute >= 30:
            is_trade_time = True
        elif hour == 15 and minute == 0:
            is_trade_time = True

    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

    return {
        "is_trade_time": is_trade_time,
        "is_trade_day": is_trade_day,
        "current_time": now.strftime("%H:%M"),
        "current_date": now.strftime("%Y-%m-%d"),
        "weekday": weekdays[now.weekday()],
    }


# ============ 涨跌停数据 ============

@router.get("/zt-pool")
def get_zt_pool(date: Optional[str] = None):
    """获取涨停股池"""
    if not date:
        date = _get_today()
    try:
        result = DataService.get_zt_pool_em(date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/zt-pool-yesterday")
def get_zt_pool_yesterday(date: Optional[str] = None):
    """获取昨日涨停"""
    if not date:
        date = _get_yesterday()
    try:
        result = DataService.get_zt_pool_previous_em(date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/zt-pool-dtgc")
def get_zt_pool_dtgc(date: Optional[str] = None):
    """获取跌停股池"""
    if not date:
        date = _get_today()
    try:
        result = DataService.get_zt_pool_dtgc_em(date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/zt-pool-zbgc")
def get_zt_pool_zbgc(date: Optional[str] = None):
    """获取炸板股池"""
    if not date:
        date = _get_today()
    try:
        result = DataService.get_zt_pool_zbgc_em(date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


# ============ 资金流向 ============

@router.get("/fund-flow/market")
def get_market_fund_flow():
    """获取大盘资金流向"""
    try:
        result = DataService.get_market_fund_flow()
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/fund-flow/sector")
def get_sector_fund_flow(
    indicator: str = "今日",
    sector_type: str = "行业资金流"
):
    """获取板块资金流"""
    try:
        result = DataService.get_sector_fund_flow_rank(indicator, sector_type)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/fund-flow/individual")
def get_individual_fund_flow(indicator: str = "今日"):
    """获取个股资金流排名"""
    try:
        result = DataService.get_individual_fund_flow_rank(indicator)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/fund-flow/stock")
def get_stock_fund_flow(stock: str = "000001"):
    """获取个股资金流向"""
    try:
        result = DataService.get_individual_fund_flow(stock)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


# ============ 龙虎榜 ============

@router.get("/lhb/detail")
def get_lhb_detail(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取龙虎榜详情"""
    if not start_date:
        start_date = _get_today()
    if not end_date:
        end_date = _get_today()
    try:
        result = DataService.get_lhb_detail_em(start_date, end_date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/lhb/yybph")
def get_lhb_yybph(symbol: str = "近一月"):
    """获取营业部排行"""
    try:
        result = DataService.get_lhb_yybph_em(symbol)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/lhb/stock-statistic")
def get_lhb_stock_statistic(symbol: str = "近一月"):
    """获取个股上榜统计"""
    try:
        result = DataService.get_lhb_stock_statistic_em(symbol)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/lhb/stock-detail")
def get_lhb_stock_detail(
    symbol: str,
    date: str,
    flag: str = "买入"
):
    """获取个股龙虎榜详情"""
    try:
        result = DataService.get_lhb_stock_detail_em(symbol, date, flag)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


# ============ 两融数据 ============

@router.get("/margin/sse")
def get_margin_sse(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取上交所融资融券"""
    if not start_date:
        start_date = _get_yesterday()
    if not end_date:
        end_date = _get_today()
    try:
        result = DataService.get_margin_sse(start_date, end_date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/margin/szse")
def get_margin_szse(date: Optional[str] = None):
    """获取深交所融资融券"""
    if not date:
        date = _get_yesterday()
    try:
        result = DataService.get_margin_szse(date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/margin/account-info")
def get_margin_account_info():
    """获取两融账户统计"""
    try:
        result = DataService.get_margin_account_info()
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


# ============ 大宗交易 ============

@router.get("/dzjy/mrmx")
def get_dzjy_mrmx(
    symbol: str = "A股",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取大宗交易明细"""
    if not start_date:
        start_date = _get_yesterday()
    if not end_date:
        end_date = _get_today()
    try:
        result = DataService.get_dzjy_mrmx(symbol, start_date, end_date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/dzjy/mrtj")
def get_dzjy_mrtj(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取大宗交易统计"""
    if not start_date:
        start_date = _get_yesterday()
    if not end_date:
        end_date = _get_today()
    try:
        result = DataService.get_dzjy_mrtj(start_date, end_date)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


# ============ 市场情绪 ============

@router.get("/market/activity")
def get_market_activity():
    """获取赚钱效应分析"""
    try:
        result = DataService.get_market_activity_legu()
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/market/high-low")
def get_high_low_statistics(symbol: str = "all"):
    """获取创新高/新低"""
    try:
        result = DataService.get_a_high_low_statistics(symbol)
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}


@router.get("/market/hot-rank")
def get_hot_rank():
    """获取股票热度排名"""
    try:
        result = DataService.get_hot_rank_em()
        return {"data": result}
    except Exception as e:
        return {"error": str(e), "data": []}
