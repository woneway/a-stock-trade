"""
AKShare 数据接口测试路由
提供所有AKShare接口的查询功能
"""
from typing import Optional
from fastapi import APIRouter, Query
from datetime import datetime, timedelta

from app.services.data_service import DataService

router = APIRouter(prefix="/akshare", tags=["AKShare"])


# ============ 数据库查询接口 ============

@router.get("/stock_info")
async def get_stock_info(
    code: Optional[str] = Query(None, description="股票代码，不传返回所有"),
    limit: int = Query(100, description="返回数量限制")
):
    """查询股票基本信息（数据库）"""
    return DataService.stock_info(code=code, limit=limit)


@router.get("/stock_kline")
async def get_stock_kline(
    stock_code: str = Query(..., description="股票代码"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYYMMDD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYYMMDD"),
    limit: int = Query(1000, description="返回数量限制")
):
    """查询日K线数据（数据库）"""
    return DataService.stock_kline(
        stock_code=stock_code,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )


@router.get("/stock_kline_minute")
async def get_stock_kline_minute(
    stock_code: str = Query(..., description="股票代码"),
    trade_date: Optional[str] = Query(None, description="交易日期 YYYYMMDD"),
    limit: int = Query(1000, description="返回数量限制")
):
    """查询分时数据（数据库）"""
    return DataService.stock_kline_minute(
        stock_code=stock_code,
        trade_date=trade_date,
        limit=limit
    )


# ============ AKShare 接口 ============

@router.get("/stock_info_a_code_name")
async def get_stock_info_a_code_name():
    """获取股票代码名称映射"""
    return DataService.get_stock_info_a_code_name()


@router.get("/stock_individual_info")
async def get_stock_individual_info(symbol: str = Query(..., description="股票代码")):
    """获取个股基本信息"""
    return DataService.get_stock_individual_info_em(symbol=symbol)


# ============ 龙虎榜 ============

@router.get("/lhb_detail")
async def get_lhb_detail(
    start_date: str = Query(..., description="开始日期 YYYYMMDD"),
    end_date: str = Query(..., description="结束日期 YYYYMMDD")
):
    """获取龙虎榜详情"""
    return DataService.get_lhb_detail_em(start_date=start_date, end_date=end_date)


@router.get("/lhb_yybph")
async def get_lhb_yybph(symbol: str = Query("近一月", description="统计周期")):
    """获取营业部排行"""
    return DataService.get_lhb_yybph_em(symbol=symbol)


@router.get("/lhb_stock_statistic")
async def get_lhb_stock_statistic(symbol: str = Query("近一月", description="统计周期")):
    """获取个股上榜统计"""
    return DataService.get_lhb_stock_statistic_em(symbol=symbol)


@router.get("/lhb_stock_detail")
async def get_lhb_stock_detail(
    symbol: str = Query(..., description="股票代码"),
    date: str = Query(..., description="日期 YYYYMMDD"),
    flag: str = Query("买入", description="类型")
):
    """获取个股龙虎榜详情"""
    return DataService.get_lhb_stock_detail_em(symbol=symbol, date=date, flag=flag)


# ============ K线数据 ============

@router.get("/stock_zh_a_hist")
async def get_stock_zh_a_hist(
    symbol: str = Query(..., description="股票代码"),
    start_date: str = Query(..., description="开始日期 YYYYMMDD"),
    end_date: str = Query(..., description="结束日期 YYYYMMDD"),
    period: str = Query("daily", description="周期"),
    adjust: str = Query("", description="复权类型")
):
    """获取日K线数据"""
    return DataService.get_stock_zh_a_hist(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        period=period,
        adjust=adjust
    )


@router.get("/stock_zh_a_hist_min")
async def get_stock_zh_a_hist_min(
    symbol: str = Query(..., description="股票代码"),
    period: str = Query("5", description="周期"),
    start_date: Optional[str] = Query(None, description="开始日期 YYYYMMDD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYYMMDD")
):
    """获取分时K线数据"""
    return DataService.get_stock_zh_a_hist_min_em(
        symbol=symbol,
        period=period,
        start_date=start_date,
        end_date=end_date
    )


# ============ 资金流向 ============

@router.get("/market_fund_flow")
async def get_market_fund_flow():
    """获取大盘资金流向"""
    return DataService.get_market_fund_flow()


@router.get("/sector_fund_flow_rank")
async def get_sector_fund_flow_rank(
    indicator: str = Query("今日", description="时间范围"),
    sector_type: str = Query("行业资金流", description="板块类型")
):
    """获取板块资金流排名"""
    return DataService.get_sector_fund_flow_rank(indicator=indicator, sector_type=sector_type)


@router.get("/individual_fund_flow_rank")
async def get_individual_fund_flow_rank(indicator: str = Query("今日", description="时间范围")):
    """获取个股资金流排名"""
    return DataService.get_individual_fund_flow_rank(indicator=indicator)


@router.get("/individual_fund_flow")
async def get_individual_fund_flow(
    stock: str = Query(..., description="股票代码"),
    market: str = Query("sz", description="市场")
):
    """获取个股资金流向"""
    return DataService.get_individual_fund_flow(stock=stock, market=market)


# ============ 涨停板 ============

@router.get("/zt_pool")
async def get_zt_pool(date: str = Query(..., description="日期 YYYYMMDD")):
    """获取涨停股池"""
    return DataService.get_zt_pool_em(date=date)


@router.get("/zt_pool_previous")
async def get_zt_pool_previous(date: str = Query(..., description="日期 YYYYMMDD")):
    """获取昨日涨停"""
    return DataService.get_zt_pool_previous_em(date=date)


@router.get("/zt_pool_dtgc")
async def get_zt_pool_dtgc(date: str = Query(..., description="日期 YYYYMMDD")):
    """获取跌停股池"""
    return DataService.get_zt_pool_dtgc_em(date=date)


@router.get("/zt_pool_zbgc")
async def get_zt_pool_zbgc(date: str = Query(..., description="日期 YYYYMMDD")):
    """获取炸板股池"""
    return DataService.get_zt_pool_zbgc_em(date=date)


# ============ 融资融券 ============

@router.get("/margin_sse")
async def get_margin_sse(
    start_date: str = Query(..., description="开始日期 YYYYMMDD"),
    end_date: str = Query(..., description="结束日期 YYYYMMDD")
):
    """获取上交所融资融券"""
    return DataService.get_margin_sse(start_date=start_date, end_date=end_date)


@router.get("/margin_szse")
async def get_margin_szse(date: str = Query(..., description="日期 YYYYMMDD")):
    """获取深交所融资融券"""
    return DataService.get_margin_szse(date=date)


@router.get("/margin_account_info")
async def get_margin_account_info():
    """获取两融账户统计"""
    return DataService.get_margin_account_info()


# ============ 大宗交易 ============

@router.get("/dzjy_mrmx")
async def get_dzjy_mrmx(
    symbol: str = Query("A股", description="类型"),
    start_date: str = Query(..., description="开始日期 YYYYMMDD"),
    end_date: str = Query(..., description="结束日期 YYYYMMDD")
):
    """获取大宗交易明细"""
    return DataService.get_dzjy_mrmx(symbol=symbol, start_date=start_date, end_date=end_date)


@router.get("/dzjy_mrtj")
async def get_dzjy_mrtj(
    start_date: str = Query(..., description="开始日期 YYYYMMDD"),
    end_date: str = Query(..., description="结束日期 YYYYMMDD")
):
    """获取大宗交易统计"""
    return DataService.get_dzjy_mrtj(start_date=start_date, end_date=end_date)


# ============ 热点数据 ============

@router.get("/market_activity")
async def get_market_activity():
    """获取赚钱效应分析"""
    return DataService.get_market_activity_legu()


@router.get("/high_low_statistics")
async def get_high_low_statistics(symbol: str = Query("all", description="市场")):
    """获取创新高/新低"""
    return DataService.get_a_high_low_statistics(symbol=symbol)


@router.get("/hot_rank")
async def get_hot_rank():
    """获取股票热度排名"""
    return DataService.get_hot_rank_em()
