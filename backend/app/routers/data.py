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
    from app.models.external_data import ExternalStockBasic, ExternalStockKline

    with Session(engine) as session:
        stock_count = session.exec(func.count(ExternalStockBasic.id)).first() or 0
        kline_count = session.exec(func.count(ExternalStockKline.id)).first() or 0

        latest_kline = session.exec(
            select(func.max(ExternalStockKline.trade_date))
        ).first()

    return {
        "stock_count": stock_count,
        "kline_count": kline_count,
        "latest_kline_date": latest_kline
    }


# ========== Akshare 函数查询 ==========
# 完整的 akshare A股接口列表
# 分类体系：宏观(政策/经济) -> 中观(板块/行业/概念) -> 微观(个股)
# 游资常用接口重点标注
AKSHARE_FUNCTIONS = {

    # ========================================
    # 一、微观 - 个股数据 (最爱用)
    # ========================================

    # ------ 个股行情 ------
    "stock_zh_a_hist": {
        "name": "stock_zh_a_hist",
        "description": "A股历史K线",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id21",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码(6位)", "required": True, "type": "str"},
            {"name": "period", "default": "daily", "description": "周期: daily/weekly/monthly", "required": False, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期YYYYMMDD", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期YYYYMMDD", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权: qfq/hfq/空字符串", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_spot_em": {
        "name": "stock_zh_a_spot_em",
        "description": "A股实时行情【游资最爱】",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id2",
        "params": [],
        "remark": "返回全部A股实时行情，包含涨跌幅、换手率、量比等核心指标"
    },
    "stock_zh_a_hist_sina": {
        "name": "stock_zh_a_hist_sina",
        "description": "新浪A股历史",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id22",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_zh_a_minute": {
        "name": "stock_zh_a_minute",
        "description": "A股分时数据",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id20",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "股票代码(sh/sz+代码)", "required": True, "type": "str"},
            {"name": "period", "default": "5", "description": "周期: 1/5/15/30/60", "required": False, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_cw_daily": {
        "name": "stock_zh_a_cw_daily",
        "description": "A股筹码分布",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id24",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },
    "stock_zh_daily_sina": {
        "name": "stock_zh_daily_sina",
        "description": "A股日K线",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id25",
        "params": [
            {"name": "symbol", "default": "sh600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_zh_tick_tx": {
        "name": "stock_zh_tick_tx",
        "description": "A股逐笔成交(腾讯)",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id27",
        "params": [
            {"name": "symbol", "default": "000001", "description": "股票代码", "required": True, "type": "str"},
            {"name": "date", "default": "20250110", "description": "日期YYYYMMDD", "required": True, "type": "str"},
        ]
    },
    "stock_zh_tick_js": {
        "name": "stock_zh_tick_js",
        "description": "A股逐笔成交(精简)",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id28",
        "params": [
            {"name": "symbol", "default": "000001", "description": "股票代码", "required": True, "type": "str"},
            {"name": "date", "default": "20250110", "description": "日期YYYYMMDD", "required": True, "type": "str"},
        ]
    },

    # ------ 个股资金流向【游资必看】------
    "stock_individual_fund_flow": {
        "name": "stock_individual_fund_flow",
        "description": "个股资金流向【游资最爱】",
        "category": "微观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id47",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "market", "default": "上海A股", "description": "市场: 上海A股/深圳A股", "required": False, "type": "str"},
        ],
        "remark": "返回单日主力资金流向，超大单/大单/中单/小单净流入"
    },
    "stock_individual_fund_flow_stick": {
        "name": "stock_individual_fund_flow_stick",
        "description": "个股资金流向(多日)",
        "category": "微观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id48",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "market", "default": "上海A股", "description": "市场", "required": False, "type": "str"},
        ]
    },

    # ------ 个股龙虎榜 ------
    "stock_lhb_detail_em": {
        "name": "stock_lhb_detail_em",
        "description": "龙虎榜详情【游资必看】",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id56",
        "params": [
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ],
        "remark": "返回龙虎榜上榜股票，机构买入/卖出金额"
    },

    # ------ 个股财务数据 ------
    "stock_financial_abstract": {
        "name": "stock_financial_abstract",
        "description": "财务摘要",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id81",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_financial_analysis_indicator": {
        "name": "stock_financial_analysis_indicator",
        "description": "财务分析指标",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id82",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "indicator", "default": "按报告期", "description": "指标类型", "required": False, "type": "str"},
        ]
    },
    "stock_yjbb_em": {
        "name": "stock_yjbb_em",
        "description": "业绩报表",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id83",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_yysj_em": {
        "name": "stock_yysj_em",
        "description": "营业数据",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id84",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_fh_em": {
        "name": "stock_fh_em",
        "description": "分红送转",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id85",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_gpwy_em": {
        "name": "stock_gpwy_em",
        "description": "股本演变",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id86",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ------ 个股融资融券 ------
    "stock_rzrq_em": {
        "name": "stock_rzrq_em",
        "description": "融资融券",
        "category": "微观-融资融券",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id111",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "stock_rzrq_detail_em": {
        "name": "stock_rzrq_detail_em",
        "description": "融资融券明细",
        "category": "微观-融资融券",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id112",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ------ 个股限售股 ------
    "stock_xsg_fp_em": {
        "name": "stock_xsg_fp_em",
        "description": "限售股解禁",
        "category": "微观-限售股",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id115",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_xsg_hold_em": {
        "name": "stock_xsg_hold_em",
        "description": "限售股持股",
        "category": "微观-限售股",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id116",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ------ 个股大宗交易 ------
    "stock_dzjy_em": {
        "name": "stock_dzjy_em",
        "description": "大宗交易",
        "category": "微观-大宗交易",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id117",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ------ 个股股东数据 ------
    "stock_zh_gbqy_em": {
        "name": "stock_zh_gbqy_em",
        "description": "股东人数变化",
        "category": "微观-股东数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id118",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ------ 个股资讯 ------
    "stock_news_em": {
        "name": "stock_news_em",
        "description": "个股新闻",
        "category": "微观-资讯",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id127",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_notice_em": {
        "name": "stock_notice_em",
        "description": "个股公告",
        "category": "微观-资讯",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id128",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_jgzy_em": {
        "name": "stock_jgzy_em",
        "description": "机构调研",
        "category": "微观-资讯",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id130",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },


    # ========================================
    # 二、中观 - 板块/行业/概念数据 (核心)
    # ========================================

    # ------ 涨跌停数据【游资必看】------
    "stock_zh_a_limit_up_em": {
        "name": "stock_zh_a_limit_up_em",
        "description": "涨停板【游资最爱】",
        "category": "中观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id3",
        "params": [
            {"name": "date", "default": "", "description": "日期YYYYMMDD", "required": False, "type": "str"},
        ],
        "remark": "返回当日涨停股票列表，包含代码、名称、涨停原因、封板金额"
    },
    "stock_zh_a_limit_down_em": {
        "name": "stock_zh_a_limit_down_em",
        "description": "跌停板",
        "category": "中观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id4",
        "params": [
            {"name": "date", "default": "", "description": "日期YYYYMMDD", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_limit_up_sina": {
        "name": "stock_zh_a_limit_up_sina",
        "description": "新浪涨停板",
        "category": "中观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id5",
        "params": []
    },
    "stock_zt_pool_em": {
        "name": "stock_zt_pool_em",
        "description": "涨停板池【游资常用】",
        "category": "中观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id59",
        "params": [
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "stock_zt_pool_strong_em": {
        "name": "stock_zt_pool_strong_em",
        "description": "强势涨停池",
        "category": "中观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id60",
        "params": [
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },

    # ------ 板块行情 ------
    "stock_board_industry_name_em": {
        "name": "stock_board_industry_name_em",
        "description": "行业板块行情",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id29",
        "params": [],
        "remark": "返回行业板块涨跌排名，看板块轮动"
    },
    "stock_board_concept_name_em": {
        "name": "stock_board_concept_name_em",
        "description": "概念板块行情",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id30",
        "params": [],
        "remark": "返回概念板块涨跌排名，找题材热点"
    },
    "stock_board_industry_cons_em": {
        "name": "stock_board_industry_cons_em",
        "description": "行业板块成分股",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id31",
        "params": [
            {"name": "symbol", "default": "半导体", "description": "板块名称", "required": True, "type": "str"},
        ]
    },
    "stock_board_concept_cons_em": {
        "name": "stock_board_concept_cons_em",
        "description": "概念板块成分股",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id32",
        "params": [
            {"name": "symbol", "default": "人工智能", "description": "板块名称", "required": True, "type": "str"},
        ]
    },

    # ------ 板块资金流向【游资必看】------
    "stock_sector_fund_flow_rank": {
        "name": "stock_sector_fund_flow_rank",
        "description": "板块资金流向排名【游资最爱】",
        "category": "中观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id50",
        "params": [
            {"name": "indicator", "default": "今日", "description": "指标: 今日/5日/10日/20日", "required": False, "type": "str"},
            {"name": "sector_type", "default": "行业资金流", "description": "板块类型: 行业资金流/概念资金流", "required": False, "type": "str"},
        ],
        "remark": "返回行业/概念板块资金净流入排名，主力资金方向"
    },

    # ------ 大盘资金流向 ------
    "stock_fund_flow": {
        "name": "stock_fund_flow",
        "description": "大盘资金流向",
        "category": "中观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id51",
        "params": []
    },
    "stock_market_fund_flow": {
        "name": "stock_market_fund_flow",
        "description": "市场资金流向",
        "category": "中观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id52",
        "params": []
    },
    "stock_fund_flow_ggyl": {
        "name": "stock_fund_flow_ggyl",
        "description": "资金流向-归公流向",
        "category": "中观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id53",
        "params": []
    },

    # ------ 龙虎榜营业部【游资核心】------
    "stock_lh_yyb_most": {
        "name": "stock_lh_yyb_most",
        "description": "龙虎榜营业部-上榜次数【游资必看】",
        "category": "中观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id57",
        "params": [],
        "remark": "返回龙虎榜上榜次数最多的营业部，游资席位追踪"
    },
    "stock_lh_yyb_capital": {
        "name": "stock_lh_yyb_capital",
        "description": "龙虎榜营业部-资金实力",
        "category": "中观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id58",
        "params": [],
        "remark": "返回龙虎榜买入金额最大的营业部"
    },
    "stock_lhb_hyyyb_em": {
        "name": "stock_lhb_hyyyb_em",
        "description": "每日活跃营业部",
        "category": "中观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id61",
        "params": [
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ]
    },
    "stock_sina_lhb_jgzz": {
        "name": "stock_sina_lhb_jgzz",
        "description": "机构席位追踪",
        "category": "中观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id62",
        "params": [
            {"name": "recent_day", "default": "5", "description": "天数: 5/10/30", "required": False, "type": "str"},
        ]
    },


    # ========================================
    # 三、宏观 - 市场整体数据 (判断大势)
    # ========================================

    # ------ 指数行情 ------
    "stock_zh_index_daily": {
        "name": "stock_zh_index_daily",
        "description": "指数日K线",
        "category": "宏观-指数行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id17",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "指数代码(sh000001上证指数/sh399001深证成指)", "required": True, "type": "str"},
        ]
    },
    "stock_zh_index_spot": {
        "name": "stock_zh_index_spot",
        "description": "指数实时行情",
        "category": "宏观-指数行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id18",
        "params": []
    },
    "stock_zh_index_cons": {
        "name": "stock_zh_index_cons",
        "description": "指数成分股",
        "category": "宏观-指数行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id19",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "指数代码", "required": True, "type": "str"},
        ]
    },

    # ------ 大盘行情 ------
    "stock_zh_a_treda": {
        "name": "stock_zh_a_treda",
        "description": "A股市场总貌",
        "category": "宏观-大盘行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id1",
        "params": [],
        "remark": "返回沪深两市涨跌家数、成交额等总貌数据"
    },
    "stock_zh_a_tredb": {
        "name": "stock_zh_a_tredb",
        "description": "A股市场交易详情",
        "category": "宏观-大盘行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id1",
        "params": []
    },
    "stock_zh_a_trade": {
        "name": "stock_zh_a_trade",
        "description": "A股市场资金流向",
        "category": "宏观-大盘行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id1",
        "params": []
    },

    # ------ 沪深港通 ------
    "stock_hsgt_top10_em": {
        "name": "stock_hsgt_top10_em",
        "description": "沪深港通top10",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id63",
        "params": [
            {"name": "symbol", "default": "北向", "description": "类型: 北向/南向", "required": True, "type": "str"},
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "stock_hsgt_hist_em": {
        "name": "stock_hsgt_hist_em",
        "description": "沪深港通历史数据",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id64",
        "params": []
    },
    "stock_hsgt_sse_sgt_em": {
        "name": "stock_hsgt_sse_sgt_em",
        "description": "沪深港通持股标的",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id65",
        "params": []
    },
    "stock_hsgt_em": {
        "name": "stock_hsgt_em",
        "description": "沪深港通持股",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id66",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ------ 融资融券汇总 ------
    "stock_rzrq_fund_flow": {
        "name": "stock_rzrq_fund_flow",
        "description": "融资融券资金流向",
        "category": "宏观-融资融券",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id113",
        "params": []
    },
    "stock_rzrq_latest": {
        "name": "stock_rzrq_latest",
        "description": "融资融券最新",
        "category": "宏观-融资融券",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id114",
        "params": []
    },


    # ========================================
    # 四、股票基础信息
    # ========================================

    # ------ 股票列表 ------
    "stock_info_a_code_name": {
        "name": "stock_info_a_code_name",
        "description": "A股代码名称列表",
        "category": "基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id68",
        "params": []
    },
    "stock_info_global_sci_em": {
        "name": "stock_info_global_sci_em",
        "description": "全球市场重要指数",
        "category": "基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id67",
        "params": []
    },
    "stock_szse_sse_info": {
        "name": "stock_szse_sse_info",
        "description": "深交所/上交所信息",
        "category": "基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id69",
        "params": []
    },

    # ------ 新股数据 ------
    "stock_ipo_info_em": {
        "name": "stock_ipo_info_em",
        "description": "新股上市信息",
        "category": "基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id70",
        "params": []
    },
    "stock_ipo_bis_em": {
        "name": "stock_ipo_bis_em",
        "description": "新股申购",
        "category": "基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id71",
        "params": []
    },

    # ------ 复权数据 ------
    "stock_daily_adj_em": {
        "name": "stock_daily_adj_em",
        "description": "日线复权数据",
        "category": "基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id23",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权类型", "required": False, "type": "str"},
        ]
    },

    # ------ 股票筛选器 ------
    "stock_fund_screener_em": {
        "name": "stock_fund_screener_em",
        "description": "股票筛选器",
        "category": "基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id35",
        "params": [
            {"name": "indicator", "default": "收盘价", "description": "筛选指标", "required": False, "type": "str"},
        ]
    },


    # ========================================
    # 五、ETF/基金/债券/期货
    # ========================================

    # ------ ETF数据 ------
    "fund_etf_hist_em": {
        "name": "fund_etf_hist_em",
        "description": "ETF历史数据",
        "category": "ETF/基金",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id1",
        "params": [
            {"name": "symbol", "default": "510500", "description": "ETF代码", "required": True, "type": "str"},
            {"name": "period", "default": "daily", "description": "周期", "required": False, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },
    "fund_etf_spot_em": {
        "name": "fund_etf_spot_em",
        "description": "ETF实时行情",
        "category": "ETF/基金",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id2",
        "params": []
    },
    "fund_lof_spot_em": {
        "name": "fund_lof_spot_em",
        "description": "LOF实时行情",
        "category": "ETF/基金",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id3",
        "params": []
    },

    # ------ 可转债 ------
    "bond_zh_hs_cov": {
        "name": "bond_zh_hs_cov",
        "description": "可转债数据",
        "category": "债券",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html#id1",
        "params": []
    },
    "bond_zh_hs_cov_spot": {
        "name": "bond_zh_hs_cov_spot",
        "description": "可转债实时行情",
        "category": "债券",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html#id2",
        "params": []
    },

    # ------ 期货 ------
    "futures_zh_daily_sina": {
        "name": "futures_zh_daily_sina",
        "description": "期货日线数据",
        "category": "期货",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id1",
        "params": [
            {"name": "symbol", "default": "RU9999", "description": "期货代码", "required": True, "type": "str"},
        ]
    },
    "futures_zh_spot": {
        "name": "futures_zh_spot",
        "description": "期货实时行情",
        "category": "期货",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id2",
        "params": []
    },
    "futures_zh_index_spot": {
        "name": "futures_zh_index_spot",
        "description": "期货指数行情",
        "category": "期货",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id3",
        "params": []
    },

    # ------ 期权 ------
    "opt_em_daily_sina": {
        "name": "opt_em_daily_sina",
        "description": "期权日线数据",
        "category": "期权",
        "doc_url": "https://akshare.akfamily.xyz/data/options/options.html#id1",
        "params": [
            {"name": "symbol", "default": "510050C2306", "description": "期权代码", "required": True, "type": "str"},
        ]
    },
    "opt_em_spot_sina": {
        "name": "opt_em_spot_sina",
        "description": "期权实时行情",
        "category": "期权",
        "doc_url": "https://akshare.akfamily.xyz/data/options/options.html#id2",
        "params": []
    },


    # ========================================
    # 六、宏观数据
    # ========================================

    # ------ 中国宏观 ------
    "macro_cn_gdp": {
        "name": "macro_cn_gdp",
        "description": "中国GDP",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id1",
        "params": []
    },
    "macro_cn_cpi": {
        "name": "macro_cn_cpi",
        "description": "中国CPI",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id2",
        "params": []
    },
    "macro_cn_ppi": {
        "name": "macro_cn_ppi",
        "description": "中国PPI",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id3",
        "params": []
    },
    "macro_china_m2_yearly": {
        "name": "macro_china_m2_yearly",
        "description": "中国M2年度数据",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro_china.html",
        "params": []
    },
    "macro_cn_m1": {
        "name": "macro_cn_m1",
        "description": "中国M1",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id5",
        "params": []
    },
    "macro_cn_m0": {
        "name": "macro_cn_m0",
        "description": "中国M0",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id6",
        "params": []
    },
    "macro_cn_shibor": {
        "name": "macro_cn_shibor",
        "description": "上海银行间拆借利率SHIBOR",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id7",
        "params": []
    },
    "macro_cn_lpr": {
        "name": "macro_cn_lpr",
        "description": "贷款市场报价利率LPR",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id8",
        "params": []
    },

    # ------ 外汇 ------
    "forex_zh_spot": {
        "name": "forex_zh_spot",
        "description": "外汇实时行情",
        "category": "宏观-外汇",
        "doc_url": "https://akshare.akfamily.xyz/data/forex/forex.html#id1",
        "params": []
    },
    "forex_zh_hist": {
        "name": "forex_zh_hist",
        "description": "外汇历史数据",
        "category": "宏观-外汇",
        "doc_url": "https://akshare.akfamily.xyz/data/forex/forex.html#id2",
        "params": [
            {"name": "symbol", "default": "USD/CNY", "description": "货币对", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 五、更多个股数据（扩展）
    # ========================================

    # ------ 个股实时行情 ------
    "stock_zh_a_new_em": {
        "name": "stock_zh_a_new_em",
        "description": "A股实时行情(新)",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id3",
        "params": [],
        "remark": "返回最新A股实时行情数据"
    },
    "stock_zh_a_st_em": {
        "name": "stock_zh_a_st_em",
        "description": "ST股实时行情",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id4",
        "params": [],
        "remark": "返回ST股票实时行情"
    },
    "stock_zh_a_stop_em": {
        "name": "stock_zh_a_stop_em",
        "description": "退市股实时行情",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id5",
        "params": [],
        "remark": "返回退市股票实时行情"
    },
    "stock_sz_a_spot_em": {
        "name": "stock_sz_a_spot_em",
        "description": "深市A股实时行情",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id6",
        "params": [],
        "remark": "返回深圳A股实时行情"
    },
    "stock_sh_a_spot_em": {
        "name": "stock_sh_a_spot_em",
        "description": "沪市A股实时行情",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id7",
        "params": [],
        "remark": "返回上海A股实时行情"
    },
    "stock_cy_a_spot_em": {
        "name": "stock_cy_a_spot_em",
        "description": "创业板实时行情",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id8",
        "params": [],
        "remark": "返回创业板股票实时行情"
    },
    "stock_kc_a_spot_em": {
        "name": "stock_kc_a_spot_em",
        "description": "科创板实时行情",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id9",
        "params": [],
        "remark": "返回科创板股票实时行情"
    },
    "stock_bj_a_spot_em": {
        "name": "stock_bj_a_spot_em",
        "description": "北交所实时行情",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id10",
        "params": [],
        "remark": "返回北京证券交易所股票实时行情"
    },
    "stock_new_a_spot_em": {
        "name": "stock_new_a_spot_em",
        "description": "新股实时行情",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id11",
        "params": [],
        "remark": "返回近期上市新股实时行情"
    },

    # ------ 个股历史数据 ------
    "stock_zh_a_hist_min_em": {
        "name": "stock_zh_a_hist_min_em",
        "description": "A股分时历史数据",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id19",
        "params": [
            {"name": "symbol", "default": "000001", "description": "股票代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250227", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
            {"name": "period", "default": "5", "description": "周期: 1/5/15/30/60", "required": False, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权: qfq/hfq", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_hist_pre_min_em": {
        "name": "stock_zh_a_hist_pre_min_em",
        "description": "A股指数分时历史",
        "category": "微观-个股行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id23",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "指数代码", "required": True, "type": "str"},
            {"name": "period", "default": "5", "description": "周期: 1/5/15/30/60", "required": False, "type": "str"},
        ]
    },

    # ------ 涨跌停数据 ------
    "stock_zh_a_limit_up_sina": {
        "name": "stock_zh_a_limit_up_sina",
        "description": "涨停板(新浪)",
        "category": "微观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id54",
        "params": []
    },
    "stock_zt_pool_dtgc_em": {
        "name": "stock_zt_pool_dtgc_em",
        "description": "涨停池-龙头股",
        "category": "微观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id58",
        "params": [
            {"name": "date", "default": "", "description": "日期YYYYMMDD", "required": False, "type": "str"},
        ]
    },
    "stock_zt_pool_previous_em": {
        "name": "stock_zt_pool_previous_em",
        "description": "昨日涨停池",
        "category": "微观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id59",
        "params": []
    },
    "stock_zt_pool_zbgc_em": {
        "name": "stock_zt_pool_zbgc_em",
        "description": "涨停池-炸板股",
        "category": "微观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id60",
        "params": [
            {"name": "date", "default": "", "description": "日期YYYYMMDD", "required": False, "type": "str"},
        ]
    },
    "stock_zt_pool_sub_new_em": {
        "name": "stock_zt_pool_sub_new_em",
        "description": "涨停池-次新股",
        "category": "微观-涨跌停",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id61",
        "params": []
    },

    # ------ 资金流向(扩展) ------
    "stock_fund_flow_big_deal": {
        "name": "stock_fund_flow_big_deal",
        "description": "资金流向-大单交易",
        "category": "微观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id50",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_fund_flow_concept": {
        "name": "stock_fund_flow_concept",
        "description": "概念板块资金流向",
        "category": "中观-板块资金",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id51",
        "params": [
            {"name": "symbol", "default": "半导体", "description": "概念名称", "required": True, "type": "str"},
        ]
    },
    "stock_fund_flow_industry": {
        "name": "stock_fund_flow_industry",
        "description": "行业板块资金流向",
        "category": "中观-板块资金",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id52",
        "params": [
            {"name": "symbol", "default": "新能源", "description": "行业名称", "required": True, "type": "str"},
        ]
    },
    "stock_individual_fund_flow_rank": {
        "name": "stock_individual_fund_flow_rank",
        "description": "个股资金流向排名",
        "category": "微观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id49",
        "params": [
            {"name": "market", "default": "北向", "description": "市场: 北向/主力/散户", "required": False, "type": "str"},
        ]
    },

    # ------ 龙虎榜(扩展) ------
    "stock_lhb_ggtj_sina": {
        "name": "stock_lhb_ggtj_sina",
        "description": "龙虎榜-股神统计",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id67",
        "params": []
    },
    "stock_lhb_stock_detail_em": {
        "name": "stock_lhb_stock_detail_em",
        "description": "龙虎榜-个股明细",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id68",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_lhb_stock_detail_date_em": {
        "name": "stock_lhb_stock_detail_date_em",
        "description": "龙虎榜-日期明细",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id69",
        "params": [
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ]
    },
    "stock_lhb_yybph_em": {
        "name": "stock_lhb_yybph_em",
        "description": "龙虎榜-营业部排行",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id70",
        "params": []
    },
    "stock_lhb_yyb_detail_em": {
        "name": "stock_lhb_yyb_detail_em",
        "description": "龙虎榜-营业部详情",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id71",
        "params": [
            {"name": "yb_code", "default": "", "description": "营业部代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ]
    },
    "stock_lhb_jgzz_sina": {
        "name": "stock_lhb_jgzz_sina",
        "description": "龙虎榜-机构席位",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id72",
        "params": []
    },
    "stock_lhb_jgmmtj_em": {
        "name": "stock_lhb_jgmmtj_em",
        "description": "龙虎榜-机构买卖统计",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id73",
        "params": []
    },
    "stock_lhb_traderstatistic_em": {
        "name": "stock_lhb_traderstatistic_em",
        "description": "龙虎榜-交易员统计",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id74",
        "params": []
    },

    # ------ 融资融券(扩展) ------
    "stock_rzrq_fund_flow": {
        "name": "stock_rzrq_fund_flow",
        "description": "融资融券资金流向",
        "category": "微观-融资融券",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id113",
        "params": []
    },
    "stock_rzrq_latest": {
        "name": "stock_rzrq_latest",
        "description": "融资融券最新",
        "category": "微观-融资融券",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id114",
        "params": []
    },

    # ------ 股票信息(扩展) ------
    "stock_info_change_name": {
        "name": "stock_info_change_name",
        "description": "股票更名信息",
        "category": "微观-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id122",
        "params": []
    },
    "stock_info_cjzc_em": {
        "name": "stock_info_cjzc_em",
        "description": "股票筹码分布",
        "category": "微观-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id123",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_info_sh_delist": {
        "name": "stock_info_sh_delist",
        "description": "上交所退市股票",
        "category": "微观-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id124",
        "params": []
    },
    "stock_info_sz_delist": {
        "name": "stock_info_sz_delist",
        "description": "深交所退市股票",
        "category": "微观-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id125",
        "params": []
    },
    "stock_info_sh_name_code": {
        "name": "stock_info_sh_name_code",
        "description": "上交所股票列表",
        "category": "微观-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id126",
        "params": []
    },
    "stock_info_sz_name_code": {
        "name": "stock_info_sz_name_code",
        "description": "深交所股票列表",
        "category": "微观-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id127",
        "params": []
    },

    # ------ 新股上市 ------
    "stock_ipo_info": {
        "name": "stock_ipo_info",
        "description": "新股上市信息",
        "category": "微观-IPO数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id128",
        "params": []
    },
    "stock_ipo_declare_em": {
        "name": "stock_ipo_declare_em",
        "description": "新股申报信息",
        "category": "微观-IPO数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id129",
        "params": []
    },
    "stock_ipo_review_em": {
        "name": "stock_ipo_review_em",
        "description": "IPO审核信息",
        "category": "微观-IPO数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id130",
        "params": []
    },

    # ------ 沪深港通(扩展) ------
    "stock_hsgt_em": {
        "name": "stock_hsgt_em",
        "description": "沪深港通持股",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id66",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_hsgt_sse_sgt_em": {
        "name": "stock_hsgt_sse_sgt_em",
        "description": "沪深港通持股标的",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id65",
        "params": []
    },
    "stock_hsgt_individual_em": {
        "name": "stock_hsgt_individual_em",
        "description": "沪深港通个人持股",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id75",
        "params": []
    },
    "stock_hsgt_individual_detail_em": {
        "name": "stock_hsgt_individual_detail_em",
        "description": "沪深港通个人持股明细",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id76",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_hsgt_hold_stock_em": {
        "name": "stock_hsgt_hold_stock_em",
        "description": "沪深港通持股股票",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id77",
        "params": []
    },
    "stock_hsgt_board_rank_em": {
        "name": "stock_hsgt_board_rank_em",
        "description": "沪深港通板块排名",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id78",
        "params": []
    },
    "stock_hsgt_fund_flow_summary_em": {
        "name": "stock_hsgt_fund_flow_summary_em",
        "description": "沪深港通资金流向汇总",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id79",
        "params": []
    },
    "stock_hsgt_stock_statistics_em": {
        "name": "stock_hsgt_stock_statistics_em",
        "description": "沪深港通股票统计",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id80",
        "params": []
    },

    # ------ 财务数据(扩展) ------
    "stock_financial_analysis_indicator_em": {
        "name": "stock_financial_analysis_indicator_em",
        "description": "财务分析指标(EM)",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id87",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "indicator", "default": "按报告期", "description": "指标类型", "required": False, "type": "str"},
        ]
    },
    "stock_fhps_em": {
        "name": "stock_fhps_em",
        "description": "分红送配",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id90",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_fhps_detail_em": {
        "name": "stock_fhps_detail_em",
        "description": "分红送配详情",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id91",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_yjkb_em": {
        "name": "stock_yjkb_em",
        "description": "业绩快报",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id92",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_yjyg_em": {
        "name": "stock_yjyg_em",
        "description": "业绩预告",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id93",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ------ 资讯公告 ------
    "stock_news_em": {
        "name": "stock_news_em",
        "description": "股票新闻",
        "category": "微观-资讯",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id115",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_notice_em": {
        "name": "stock_notice_em",
        "description": "股票公告",
        "category": "微观-资讯",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id116",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_jgzy_em": {
        "name": "stock_jgzy_em",
        "description": "机构调研",
        "category": "微观-资讯",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id117",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 六、中观-板块数据
    # ========================================

    # ------ 板块行情 ------
    "stock_board_industry_spot_em": {
        "name": "stock_board_industry_spot_em",
        "description": "行业板块行情",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id35",
        "params": []
    },
    "stock_board_concept_spot_em": {
        "name": "stock_board_concept_spot_em",
        "description": "概念板块行情",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id36",
        "params": []
    },
    "stock_board_change_em": {
        "name": "stock_board_change_em",
        "description": "板块涨跌排行",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id37",
        "params": []
    },
    "stock_board_industry_hist_em": {
        "name": "stock_board_industry_hist_em",
        "description": "行业板块历史",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id38",
        "params": [
            {"name": "symbol", "default": "BK0044", "description": "板块代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },
    "stock_board_concept_hist_em": {
        "name": "stock_board_concept_hist_em",
        "description": "概念板块历史",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id39",
        "params": [
            {"name": "symbol", "default": "BK1001", "description": "板块代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },

    # ------ 板块资金 ------
    "stock_sector_fund_flow_summary": {
        "name": "stock_sector_fund_flow_summary",
        "description": "板块资金流向汇总",
        "category": "中观-板块资金",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id53",
        "params": []
    },
    "stock_sector_fund_flow_hist": {
        "name": "stock_sector_fund_flow_hist",
        "description": "板块资金流向历史",
        "category": "中观-板块资金",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id54",
        "params": [
            {"name": "sector_type", "default": "行业", "description": "板块类型: 行业/概念", "required": True, "type": "str"},
            {"name": "symbol", "default": "半导体", "description": "板块名称", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 七、宏观-指数数据
    # ========================================

    # ------ 指数行情 ------
    "stock_zh_index_spot_em": {
        "name": "stock_zh_index_spot_em",
        "description": "A股指数实时行情",
        "category": "宏观-指数",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id17",
        "params": []
    },
    "stock_zh_index_daily_em": {
        "name": "stock_zh_index_daily_em",
        "description": "A股指数日K线",
        "category": "宏观-指数",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id18",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "指数代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权", "required": False, "type": "str"},
        ]
    },
    "stock_zh_index_cons": {
        "name": "stock_zh_index_cons",
        "description": "指数成分股",
        "category": "宏观-指数",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id44",
        "params": [
            {"name": "symbol", "default": "sh000300", "description": "指数代码", "required": True, "type": "str"},
        ]
    },

    # ------ 市场总貌 ------
    "stock_zh_a_treda": {
        "name": "stock_zh_a_treda",
        "description": "市场总貌(上海)",
        "category": "宏观-市场",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id13",
        "params": []
    },
    "stock_zh_a_tredb": {
        "name": "stock_zh_a_tredb",
        "description": "市场总貌(深圳)",
        "category": "宏观-市场",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id14",
        "params": []
    },
    "stock_zh_a_trade": {
        "name": "stock_zh_a_trade",
        "description": "市场交易数据",
        "category": "宏观-市场",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id15",
        "params": []
    },

    # ========================================
    # 八、期货数据
    # ========================================

    "futures_zh_spot": {
        "name": "futures_zh_spot",
        "description": "期货实时行情",
        "category": "期货-实时行情",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id2",
        "params": []
    },
    "futures_zh_realtime": {
        "name": "futures_zh_realtime",
        "description": "期货实时数据",
        "category": "期货-实时行情",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id3",
        "params": []
    },
    "futures_hist_em": {
        "name": "futures_hist_em",
        "description": "期货历史数据",
        "category": "期货-历史数据",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id4",
        "params": [
            {"name": "symbol", "default": "IF2306", "description": "合约代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权", "required": False, "type": "str"},
        ]
    },
    "futures_comm_info": {
        "name": "futures_comm_info",
        "description": "期货品种信息",
        "category": "期货-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id5",
        "params": []
    },
    "futures_contract_info_cffex": {
        "name": "futures_contract_info_cffex",
        "description": "中金所合约信息",
        "category": "期货-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id6",
        "params": []
    },
    "futures_contract_info_shfe": {
        "name": "futures_contract_info_shfe",
        "description": "上期所合约信息",
        "category": "期货-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id7",
        "params": []
    },
    "futures_contract_info_dce": {
        "name": "futures_contract_info_dce",
        "description": "大商所合约信息",
        "category": "期货-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id8",
        "params": []
    },
    "futures_contract_info_czce": {
        "name": "futures_contract_info_czce",
        "description": "郑商所合约信息",
        "category": "期货-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html#id9",
        "params": []
    },

    # ========================================
    # 九、期权数据
    # ========================================

    "option_current_day_sse": {
        "name": "option_current_day_sse",
        "description": "上证期权实时行情",
        "category": "期权-实时行情",
        "doc_url": "https://akshare.akfamily.xyz/data/option/option.html#id2",
        "params": []
    },
    "option_current_day_szse": {
        "name": "option_current_day_szse",
        "description": "深证期权实时行情",
        "category": "期权-实时行情",
        "doc_url": "https://akshare.akfamily.xyz/data/option/option.html#id3",
        "params": []
    },
    "option_sse_list_sina": {
        "name": "option_sse_list_sina",
        "description": "期权标的列表",
        "category": "期权-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/option/option.html#id4",
        "params": []
    },
    "option_comm_symbol": {
        "name": "option_comm_symbol",
        "description": "期权合约代码",
        "category": "期权-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/option/option.html#id5",
        "params": [
            {"name": "underlying", "default": "510050", "description": "标的代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 十、基金数据
    # ========================================

    "fund_etf_spot_em": {
        "name": "fund_etf_spot_em",
        "description": "ETF实时行情",
        "category": "基金-ETF",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id2",
        "params": []
    },
    "fund_etf_hist_em": {
        "name": "fund_etf_hist_em",
        "description": "ETF历史数据",
        "category": "基金-ETF",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id3",
        "params": [
            {"name": "symbol", "default": "511880", "description": "ETF代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权", "required": False, "type": "str"},
        ]
    },
    "fund_open_fund_daily_em": {
        "name": "fund_open_fund_daily_em",
        "description": "开放式基金净值",
        "category": "基金-公募",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id4",
        "params": []
    },
    "fund_open_fund_info_em": {
        "name": "fund_open_fund_info_em",
        "description": "开放式基金列表",
        "category": "基金-公募",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id5",
        "params": []
    },
    "fund_money_fund_daily_em": {
        "name": "fund_money_fund_daily_em",
        "description": "货币基金净值",
        "category": "基金-货币",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id6",
        "params": []
    },
    "fund_fh_em": {
        "name": "fund_fh_em",
        "description": "基金分红",
        "category": "基金-数据",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id7",
        "params": []
    },
    "fund_manager_em": {
        "name": "fund_manager_em",
        "description": "基金经理",
        "category": "基金-数据",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id8",
        "params": []
    },
    "fund_portfolio_hold_em": {
        "name": "fund_portfolio_hold_em",
        "description": "基金持仓",
        "category": "基金-数据",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id9",
        "params": [
            {"name": "symbol", "default": "000001", "description": "基金代码", "required": True, "type": "str"},
            {"name": "date", "default": "", "description": "报告期", "required": False, "type": "str"},
        ]
    },

    # ========================================
    # 十一、债券数据
    # ========================================

    "bond_zh_hs_spot": {
        "name": "bond_zh_hs_spot",
        "description": "沪深债券实时行情",
        "category": "债券-实时行情",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html#id2",
        "params": []
    },
    "bond_zh_hs_daily": {
        "name": "bond_zh_hs_daily",
        "description": "沪深债券日K线",
        "category": "债券-历史数据",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html#id3",
        "params": [
            {"name": "symbol", "default": "sh113009", "description": "债券代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },
    "bond_zh_cov": {
        "name": "bond_zh_cov",
        "description": "可转债列表",
        "category": "债券-可转债",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html#id4",
        "params": []
    },
    "bond_cb_jsl": {
        "name": "bond_cb_jsl",
        "description": "可转债数据(集思录)",
        "category": "债券-可转债",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html#id5",
        "params": []
    },

    # ========================================
    # 十二、宏观数据
    # ========================================

    # ------ 中国宏观 ------
    "macro_china_m2_yearly": {
        "name": "macro_china_m2_yearly",
        "description": "中国M2年度数据【重要】",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro_china.html",
        "params": []
    },
    "macro_china_cpi": {
        "name": "macro_china_cpi",
        "description": "中国CPI数据",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id3",
        "params": []
    },
    "macro_china_ppi": {
        "name": "macro_china_ppi",
        "description": "中国PPI数据",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id4",
        "params": []
    },
    "macro_china_gdp": {
        "name": "macro_china_gdp",
        "description": "中国GDP数据",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id5",
        "params": []
    },
    "macro_china_stock_market_cap": {
        "name": "macro_china_stock_market_cap",
        "description": "中国股市市值",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id6",
        "params": []
    },
    "macro_china_fdi": {
        "name": "macro_china_fdi",
        "description": "中国FDI数据",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id7",
        "params": []
    },
    "macro_china_exports_yoy": {
        "name": "macro_china_exports_yoy",
        "description": "中国出口同比",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id8",
        "params": []
    },
    "macro_china_imports_yoy": {
        "name": "macro_china_imports_yoy",
        "description": "中国进口同比",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id9",
        "params": []
    },
    "macro_china_trade": {
        "name": "macro_china_trade",
        "description": "中国贸易数据",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id10",
        "params": []
    },
    "macro_china_czsr": {
        "name": "macro_china_czsr",
        "description": "中国财政数据",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id11",
        "params": []
    },
    "macro_china_consumer_goods_retail": {
        "name": "macro_china_consumer_goods_retail",
        "description": "中国消费数据",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id12",
        "params": []
    },
    "macro_china_central_bank_balance": {
        "name": "macro_china_central_bank_balance",
        "description": "中国央行资产负债表",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id13",
        "params": []
    },
    "macro_china_bank_financing": {
        "name": "macro_china_bank_financing",
        "description": "中国社会融资",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id14",
        "params": []
    },

    # ------ 美国宏观 ------
    "macro_usa_unemployment_rate": {
        "name": "macro_usa_unemployment_rate",
        "description": "美国失业率",
        "category": "宏观-美国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id100",
        "params": []
    },
    "macro_usa_cpi": {
        "name": "macro_usa_cpi",
        "description": "美国CPI",
        "category": "宏观-美国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id101",
        "params": []
    },
    "macro_usa_ppi": {
        "name": "macro_usa_ppi",
        "description": "美国PPI",
        "category": "宏观-美国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id102",
        "params": []
    },
    "macro_usa_gdp": {
        "name": "macro_usa_gdp",
        "description": "美国GDP",
        "category": "宏观-美国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id103",
        "params": []
    },
    "macro_usa_interest_rate": {
        "name": "macro_usa_interest_rate",
        "description": "美国利率",
        "category": "宏观-美国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro.html#id104",
        "params": []
    },

    # ========================================
    # 十三、外汇数据
    # ========================================

    "forex_spot_em": {
        "name": "forex_spot_em",
        "description": "外汇实时行情",
        "category": "外汇-实时",
        "doc_url": "https://akshare.akfamily.xyz/data/forex/forex.html#id2",
        "params": []
    },
    "forex_hist_em": {
        "name": "forex_hist_em",
        "description": "外汇历史数据",
        "category": "外汇-历史",
        "doc_url": "https://akshare.akfamily.xyz/data/forex/forex.html#id3",
        "params": [
            {"name": "symbol", "default": "USD/CNY", "description": "货币对", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },
    "forex_zh_spot": {
        "name": "forex_zh_spot",
        "description": "外汇实时数据(人民币)",
        "category": "外汇-实时",
        "doc_url": "https://akshare.akfamily.xyz/data/forex/forex.html#id4",
        "params": []
    },

    # ========================================
    # 十四、港股数据
    # ========================================

    "stock_hk_spot_em": {
        "name": "stock_hk_spot_em",
        "description": "港股实时行情",
        "category": "港股-实时行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock_hk.html#id2",
        "params": []
    },
    "stock_hk_daily": {
        "name": "stock_hk_daily",
        "description": "港股日K线",
        "category": "港股-历史数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock_hk.html#id3",
        "params": [
            {"name": "symbol", "default": "00700", "description": "港股代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },
    "stock_hk_index_spot_em": {
        "name": "stock_hk_index_spot_em",
        "description": "港股指数行情",
        "category": "港股-指数",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock_hk.html#id4",
        "params": []
    },

    # ========================================
    # 十五、美股数据
    # ========================================

    "stock_us_spot_em": {
        "name": "stock_us_spot_em",
        "description": "美股实时行情",
        "category": "美股-实时行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock_us.html#id2",
        "params": []
    },
    "stock_us_daily": {
        "name": "stock_us_daily",
        "description": "美股日K线",
        "category": "美股-历史数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock_us.html#id3",
        "params": [
            {"name": "symbol", "default": "AAPL", "description": "股票代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 十六、新增：指数数据（补充）
    # ========================================

    "index_zh_a_hist": {
        "name": "index_zh_a_hist",
        "description": "A股指数历史K线【重要】",
        "category": "宏观-指数",
        "doc_url": "https://akshare.akfamily.xyz/data/index/index.html#id2",
        "params": [
            {"name": "symbol", "default": "000300", "description": "指数代码(000001上证/000300沪深300)", "required": True, "type": "str"},
            {"name": "period", "default": "daily", "description": "周期: daily/weekly/monthly", "required": False, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期YYYYMMDD", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期YYYYMMDD", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权: qfq/hfq/空字符串", "required": False, "type": "str"},
        ]
    },
    "stock_zh_index_spot_em": {
        "name": "stock_zh_index_spot_em",
        "description": "A股指数实时行情",
        "category": "宏观-指数行情",
        "doc_url": "https://akshare.akfamily.xyz/data/index/index.html#id3",
        "params": []
    },
    "stock_zh_index_daily": {
        "name": "stock_zh_index_daily",
        "description": "A股指数日K线",
        "category": "宏观-指数行情",
        "doc_url": "https://akshare.akfamily.xyz/data/index/index.html#id4",
        "params": [
            {"name": "symbol", "default": "000001", "description": "指数代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 十七、新增：ETF数据（补充）
    # ========================================

    "fund_etf_hist_sina": {
        "name": "fund_etf_hist_sina",
        "description": "ETF历史数据(新浪)【重要】",
        "category": "ETF/基金",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html#id3",
        "params": [
            {"name": "symbol", "default": "sh510500", "description": "ETF代码", "required": True, "type": "str"},
            {"name": "period", "default": "daily", "description": "周期", "required": False, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权", "required": False, "type": "str"},
        ]
    },

    # ========================================
    # 十八、新增：股东数据（补充）
    # ========================================

    "stock_main_stock_holder": {
        "name": "stock_main_stock_holder",
        "description": "主要股东持股情况【游资必看】",
        "category": "微观-股东数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id117",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_fund_stock_holder": {
        "name": "stock_fund_stock_holder",
        "description": "基金股东持股情况",
        "category": "微观-股东数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id118",
        "params": [
            {"name": "symbol", "default": "600004", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_circulate_stock_holder": {
        "name": "stock_circulate_stock_holder",
        "description": "流通股东持股情况",
        "category": "微观-股东数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id119",
        "params": [
            {"name": "symbol", "default": "600000", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_shareholder_change_ths": {
        "name": "stock_shareholder_change_ths",
        "description": "股东增减持公告(同花顺)",
        "category": "微观-股东数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id120",
        "params": [
            {"name": "symbol", "default": "688981", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 十九、新增：大宗交易（补充）
    # ========================================

    "stock_dzjy_mrmx": {
        "name": "stock_dzjy_mrmx",
        "description": "大宗交易明细(按行业)",
        "category": "微观-大宗交易",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id105",
        "params": [
            {"name": "symbol", "default": "基金", "description": "行业/概念", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },
    "stock_dzjy_mrtj": {
        "name": "stock_dzjy_mrtj",
        "description": "大宗交易统计(按行业)",
        "category": "微观-大宗交易",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id106",
        "params": [
            {"name": "symbol", "default": "基金", "description": "行业/概念", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 二十、新增：龙虎榜补充
    # ========================================

    "stock_lhb_detail_daily_sina": {
        "name": "stock_lhb_detail_daily_sina",
        "description": "龙虎榜每日详情(新浪)",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id57",
        "params": [
            {"name": "date", "default": "20250227", "description": "日期YYYYMMDD", "required": True, "type": "str"},
        ]
    },
    "stock_lhb_stock_statistic_em": {
        "name": "stock_lhb_stock_statistic_em",
        "description": "龙虎榜股票统计",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id58",
        "params": [
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ]
    },
    "stock_lhb_jgstatistic_em": {
        "name": "stock_lhb_jgstatistic_em",
        "description": "龙虎榜机构统计",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id59",
        "params": [
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ]
    },

    # ========================================
    # 二十一、新增：资金流向补充
    # ========================================

    "stock_main_fund_flow": {
        "name": "stock_main_fund_flow",
        "description": "主力资金流向",
        "category": "微观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id49",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_concept_fund_flow_hist": {
        "name": "stock_concept_fund_flow_hist",
        "description": "概念板块资金流向历史",
        "category": "中观-板块资金",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id50",
        "params": [
            {"name": "symbol", "default": "互联网", "description": "概念名称", "required": True, "type": "str"},
            {"name": "period", "default": "daily", "description": "周期", "required": False, "type": "str"},
        ]
    },

    # ========================================
    # 二十二、新增：财务数据补充
    # ========================================

    "stock_balance_sheet_by_report_em": {
        "name": "stock_balance_sheet_by_report_em",
        "description": "资产负债表(报告期)",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id87",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "indicator", "default": "按报告期", "description": "指标类型", "required": False, "type": "str"},
        ]
    },
    "stock_cash_flow_sheet_by_report_em": {
        "name": "stock_cash_flow_sheet_by_report_em",
        "description": "现金流量表(报告期)",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id88",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "indicator", "default": "按报告期", "description": "指标类型", "required": False, "type": "str"},
        ]
    },
    "stock_financial_analysis_indicator_em": {
        "name": "stock_financial_analysis_indicator_em",
        "description": "财务分析指标(同花顺)",
        "category": "微观-财务数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id89",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 二十三、新增：限售股补充
    # ========================================

    "stock_restricted_release_summary_em": {
        "name": "stock_restricted_release_summary_em",
        "description": "限售股解禁汇总",
        "category": "微观-限售股",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id121",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_restricted_release_detail_em": {
        "name": "stock_restricted_release_detail_em",
        "description": "限售股解禁明细",
        "category": "微观-限售股",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id122",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 二十四、新增：IPO数据补充
    # ========================================

    "stock_ipo_summary_cninfo": {
        "name": "stock_ipo_summary_cninfo",
        "description": "IPO概况(证监会)",
        "category": "微观-IPO数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock_ipo.html#id2",
        "params": []
    },
    "stock_new_ipo_cninfo": {
        "name": "stock_new_ipo_cninfo",
        "description": "新股申购(证监会)",
        "category": "微观-IPO数据",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock_ipo.html#id3",
        "params": []
    },

    # ========================================
    # 二十五、新增：板块数据补充（同花顺）
    # ========================================

    "stock_board_concept_name_ths": {
        "name": "stock_board_concept_name_ths",
        "description": "同花顺概念板块名称",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id60",
        "params": []
    },
    "stock_board_concept_info_ths": {
        "name": "stock_board_concept_info_ths",
        "description": "同花顺概念板块详情",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id61",
        "params": [
            {"name": "name", "default": "人工智能", "description": "概念名称", "required": True, "type": "str"},
        ]
    },
    "stock_board_industry_name_ths": {
        "name": "stock_board_industry_name_ths",
        "description": "同花顺行业板块名称",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id62",
        "params": []
    },
    "stock_board_industry_info_ths": {
        "name": "stock_board_industry_info_ths",
        "description": "同花顺行业板块详情",
        "category": "中观-板块行情",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html#id63",
        "params": [
            {"name": "name", "default": "银行", "description": "行业名称", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 二十六、新增：其他补充
    # ========================================

    "stock_zh_index_daily_tx": {
        "name": "stock_zh_index_daily_tx",
        "description": "A股指数日K线(腾讯)",
        "category": "宏观-指数行情",
        "doc_url": "https://akshare.akfamily.xyz/data/index/index.html#id5",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "指数代码", "required": True, "type": "str"},
        ]
    },
    "stock_zh_index_spot_sina": {
        "name": "stock_zh_index_spot_sina",
        "description": "A股指数实时行情(新浪)",
        "category": "宏观-指数行情",
        "doc_url": "https://akshare.akfamily.xyz/data/index/index.html#id6",
        "params": []
    },
    "stock_index_pe_lg": {
        "name": "stock_index_pe_lg",
        "description": "指数市盈率",
        "category": "宏观-指数",
        "doc_url": "https://akshare.akfamily.xyz/data/index/index.html#id7",
        "params": [
            {"name": "symbol", "default": "沪深300", "description": "指数名称", "required": False, "type": "str"},
        ]
    },
    "stock_index_pb_lg": {
        "name": "stock_index_pb_lg",
        "description": "指数市净率",
        "category": "宏观-指数",
        "doc_url": "https://akshare.akfamily.xyz/data/index/index.html#id8",
        "params": [
            {"name": "symbol", "default": "上证50", "description": "指数名称", "required": False, "type": "str"},
        ]
    },

    # ========================================
    # 二十七、新增：更多ETF/基金数据
    # ========================================

    "fund_etf_category_sina": {
        "name": "fund_etf_category_sina",
        "description": "ETF分类数据(新浪)",
        "category": "ETF/基金",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html",
        "params": []
    },
    "fund_etf_fund_daily_em": {
        "name": "fund_etf_fund_daily_em",
        "description": "ETF基金每日行情",
        "category": "ETF/基金",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html",
        "params": [
            {"name": "symbol", "default": "512880", "description": "ETF代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },
    "fund_etf_scale_sse": {
        "name": "fund_etf_scale_sse",
        "description": "ETF规模数据(上交所)",
        "category": "ETF/基金",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html",
        "params": []
    },
    "fund_aum_em": {
        "name": "fund_aum_em",
        "description": "公募基金资产管理规模",
        "category": "基金-公募",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html",
        "params": [
            {"name": "symbol", "default": "", "description": "基金代码", "required": False, "type": "str"},
        ]
    },
    "fund_cf_em": {
        "name": "fund_cf_em",
        "description": "基金持仓明细(重仓股)",
        "category": "基金-数据",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html",
        "params": [
            {"name": "symbol", "default": "161039", "description": "基金代码", "required": True, "type": "str"},
            {"name": "date", "default": "", "description": "报告期", "required": False, "type": "str"},
        ]
    },
    "fund_report_fund_hold": {
        "name": "fund_report_fund_hold",
        "description": "基金持仓报告",
        "category": "基金-数据",
        "doc_url": "https://akshare.akfamily.xyz/data/fund/fund.html",
        "params": [
            {"name": "symbol", "default": "", "description": "基金代码", "required": False, "type": "str"},
        ]
    },

    # ========================================
    # 二十八、新增：更多期货数据
    # ========================================

    "futures_display_main_sina": {
        "name": "futures_display_main_sina",
        "description": "期货主力合约排行(新浪)",
        "category": "期货",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html",
        "params": []
    },
    "futures_dce_position_rank": {
        "name": "futures_dce_position_rank",
        "description": "大商所持仓排名",
        "category": "期货",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html",
        "params": [
            {"name": "symbol", "default": "i", "description": "合约代码", "required": True, "type": "str"},
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "futures_zh_index_spot": {
        "name": "futures_zh_index_spot",
        "description": "期货指数实时行情",
        "category": "期货",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html",
        "params": []
    },
    "futures_delivery_shfe": {
        "name": "futures_delivery_shfe",
        "description": "上期所交割数据",
        "category": "期货",
        "doc_url": "https://akshare.akfamily.xyz/data/futures/futures.html",
        "params": [
            {"name": "symbol", "default": "cu", "description": "合约代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 二十九、新增：更多债券数据
    # ========================================

    "bond_china_yield": {
        "name": "bond_china_yield",
        "description": "中国国债收益率",
        "category": "债券",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html",
        "params": []
    },
    "bond_corporate_issue_cninfo": {
        "name": "bond_corporate_issue_cninfo",
        "description": "企业债发行数据(证监会)",
        "category": "债券",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html",
        "params": []
    },
    "bond_cb_summary_sina": {
        "name": "bond_cb_summary_sina",
        "description": "可转债概况(新浪)",
        "category": "债券-可转债",
        "doc_url": "https://akshare.akfamily.xyz/data/bond/bond.html",
        "params": []
    },

    # ========================================
    # 三十、新增：更多宏观数据
    # ========================================

    "macro_china_shibor": {
        "name": "macro_china_shibor",
        "description": "中国SHIBOR数据",
        "category": "宏观-中国经济",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro_china.html",
        "params": []
    },
    "macro_china_market_margin": {
        "name": "macro_china_market_margin",
        "description": "中国融资融券数据",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro_china.html",
        "params": []
    },
    "macro_china_new_house_price": {
        "name": "macro_china_new_house_price",
        "description": "中国新建住宅价格指数",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro_china.html",
        "params": []
    },
    "macro_china_freight_index": {
        "name": "macro_china_freight_index",
        "description": "中国物流运价指数",
        "category": "宏观-中国",
        "doc_url": "https://akshare.akfamily.xyz/data/macro/macro_china.html",
        "params": []
    },

    # ========================================
    # 三十一、新增：更多期权数据
    # ========================================

    "option_current_em": {
        "name": "option_current_em",
        "description": "期权实时行情(东方财富)",
        "category": "期权",
        "doc_url": "https://akshare.akfamily.xyz/data/option/option.html",
        "params": []
    },
    "option_comm_info": {
        "name": "option_comm_info",
        "description": "期权合约信息",
        "category": "期权-基础信息",
        "doc_url": "https://akshare.akfamily.xyz/data/option/option.html",
        "params": []
    },
    "option_cffex_hs300_spot_sina": {
        "name": "option_cffex_hs300_spot_sina",
        "description": "沪深300期权实时行情",
        "category": "期权-实时行情",
        "doc_url": "https://akshare.akfamily.xyz/data/option/option.html",
        "params": []
    },

    # ========================================
    # 三十二、新增：更多龙虎榜数据
    # ========================================

    "stock_lhb_yytj_sina": {
        "name": "stock_lhb_yytj_sina",
        "description": "龙虎榜游资追踪(新浪)",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html",
        "params": []
    },
    "stock_lhb_jgmx_sina": {
        "name": "stock_lhb_jgmx_sina",
        "description": "龙虎榜机构明细(新浪)",
        "category": "微观-龙虎榜",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html",
        "params": []
    },
    "stock_fund_flow_individual": {
        "name": "stock_fund_flow_individual",
        "description": "个股资金流向详细",
        "category": "微观-资金流向",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 三十三、新增：更多机构数据
    # ========================================

    "stock_jgdy_tj_em": {
        "name": "stock_jgdy_tj_em",
        "description": "机构调研统计",
        "category": "微观-资讯",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html",
        "params": [
            {"name": "symbol", "default": "", "description": "股票代码", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_gbjg_em": {
        "name": "stock_zh_a_gbjg_em",
        "description": "A股北向资金持股",
        "category": "宏观-沪深港通",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock.html",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========================================
    # 三十四、新增：更多指数数据
    # ========================================

    "stock_zh_index_hist_csindex": {
        "name": "stock_zh_index_hist_csindex",
        "description": "中证指数历史数据",
        "category": "宏观-指数行情",
        "doc_url": "https://akshare.akfamily.xyz/data/index/index.html",
        "params": [
            {"name": "symbol", "default": "000985", "description": "指数代码", "required": True, "type": "str"},
        ]
    },
    "stock_hk_index_spot_sina": {
        "name": "stock_hk_index_spot_sina",
        "description": "港股指数实时行情(新浪)",
        "category": "港股-指数",
        "doc_url": "https://akshare.akfamily.xyz/data/stock/stock_hk.html",
        "params": []
    },

}


# ==================== 缓存配置 ====================
# 从 cache_service 导入缓存配置
from app.services.cache_service import CacheService
CACHE_MODELS = CacheService.CACHE_CONFIG

# 需要同步到数据库的接口列表
SYNC_FUNCTIONS = {k for k, v in CACHE_MODELS.items() if v.get("sync")}


# 分类 - 重新设计
CATEGORIES = {
    # ==================== 一、A股行情 ====================
    "A股行情": [
        {"name": "stock_zh_a_spot_em", "description": "A股实时行情【游资最爱】"},
        {"name": "stock_zh_a_hist", "description": "A股历史K线"},
        {"name": "stock_zh_a_minute", "description": "A股分时数据"},
        {"name": "stock_zh_daily_sina", "description": "A股日K线"},
        {"name": "stock_zh_a_hist_sina", "description": "新浪A股历史"},
        {"name": "stock_zh_a_cw_daily", "description": "A股筹码分布"},
        {"name": "stock_zh_tick_tx", "description": "A股逐笔成交(腾讯)"},
        {"name": "stock_zh_tick_js", "description": "A股逐笔成交(精简)"},
        {"name": "stock_zh_a_limit_up_em", "description": "涨停板【游资最爱】"},
        {"name": "stock_zh_a_limit_down_em", "description": "跌停板"},
        {"name": "stock_zh_a_limit_up_sina", "description": "新浪涨停板"},
        {"name": "stock_zt_pool_em", "description": "涨停板池【游资常用】"},
        {"name": "stock_zt_pool_strong_em", "description": "强势涨停池"},
        {"name": "stock_zt_pool_dtgc_em", "description": "涨停池顶格成妖"},
        {"name": "stock_zt_pool_zbgc_em", "description": "涨停池炸板高测"},
        {"name": "stock_zt_pool_previous_em", "description": "昨日涨停池"},
        {"name": "stock_zt_pool_sub_new_em", "description": "新股涨停池"},
    ],

    # ==================== 二、港股行情 ====================
    "港股行情": [
        {"name": "stock_hk_spot_em", "description": "港股实时行情"},
        {"name": "stock_hk_daily", "description": "港股日K线"},
        {"name": "stock_hk_index_spot_em", "description": "港股指数行情"},
        {"name": "stock_hk_index_spot_sina", "description": "港股指数(新浪)"},
    ],

    # ==================== 三、美股行情 ====================
    "美股行情": [
        {"name": "stock_us_spot_em", "description": "美股实时行情"},
        {"name": "stock_us_daily", "description": "美股日K线"},
    ],

    # ==================== 四、指数数据 ====================
    "指数数据": [
        {"name": "stock_zh_index_spot_em", "description": "A股指数实时行情"},
        {"name": "stock_zh_index_daily", "description": "A股指数日K线"},
        {"name": "index_zh_a_hist", "description": "A股指数历史K线"},
        {"name": "stock_zh_index_daily_tx", "description": "指数日K线(腾讯)"},
        {"name": "stock_zh_index_spot_sina", "description": "指数实时行情(新浪)"},
        {"name": "stock_zh_index_cons", "description": "指数成分股"},
        {"name": "stock_index_pe_lg", "description": "指数市盈率"},
        {"name": "stock_index_pb_lg", "description": "指数市净率"},
        {"name": "stock_zh_index_hist_csindex", "description": "中证指数历史数据"},
        {"name": "stock_zh_a_treda", "description": "A股市场总貌"},
        {"name": "stock_zh_a_tredb", "description": "A股市场交易详情"},
        {"name": "stock_zh_a_trade", "description": "A股市场资金流向"},
    ],

    # ==================== 五、板块行情 ====================
    "板块行情": [
        {"name": "stock_board_industry_name_em", "description": "行业板块行情"},
        {"name": "stock_board_concept_name_em", "description": "概念板块行情"},
        {"name": "stock_board_industry_cons_em", "description": "行业板块成分股"},
        {"name": "stock_board_concept_cons_em", "description": "概念板块成分股"},
        {"name": "stock_board_industry_spot_em", "description": "行业板块实时行情"},
        {"name": "stock_board_concept_spot_em", "description": "概念板块实时行情"},
        {"name": "stock_board_concept_name_ths", "description": "同花顺概念板块名称"},
        {"name": "stock_board_concept_info_ths", "description": "同花顺概念板块详情"},
        {"name": "stock_board_industry_name_ths", "description": "同花顺行业板块名称"},
        {"name": "stock_board_industry_info_ths", "description": "同花顺行业板块详情"},
        {"name": "stock_board_change_em", "description": "板块涨跌变化"},
    ],

    # ==================== 六、资金流向【核心】 ====================
    "资金流向": [
        {"name": "stock_individual_fund_flow", "description": "个股资金流向【游资最爱】"},
        {"name": "stock_individual_fund_flow_stick", "description": "个股资金流向(多日)"},
        {"name": "stock_fund_flow_individual", "description": "个股资金流向详细"},
        {"name": "stock_sector_fund_flow_rank", "description": "板块资金流向排名【游资最爱】"},
        {"name": "stock_fund_flow", "description": "大盘资金流向"},
        {"name": "stock_market_fund_flow", "description": "市场资金流向"},
        {"name": "stock_fund_flow_ggyl", "description": "资金流向-归公流向"},
        {"name": "stock_main_fund_flow", "description": "主力资金流向"},
        {"name": "stock_concept_fund_flow_hist", "description": "概念资金流向历史"},
        {"name": "stock_fund_flow_big_deal", "description": "资金流向-大单交易"},
        {"name": "stock_individual_fund_flow_rank", "description": "个股资金流向排名"},
        {"name": "stock_rzrq_fund_flow", "description": "融资融券资金流向"},
    ],

    # ==================== 七、龙虎榜 ====================
    "龙虎榜": [
        {"name": "stock_lhb_detail_em", "description": "龙虎榜详情【游资必看】"},
        {"name": "stock_lhb_detail_daily_sina", "description": "龙虎榜每日详情(新浪)"},
        {"name": "stock_lhb_stock_statistic_em", "description": "龙虎榜股票统计"},
        {"name": "stock_lhb_jgstatistic_em", "description": "龙虎榜机构统计"},
        {"name": "stock_lhb_yytj_sina", "description": "龙虎榜游资追踪"},
        {"name": "stock_lhb_jgmx_sina", "description": "龙虎榜机构明细"},
        {"name": "stock_lh_yyb_most", "description": "龙虎榜营业部-上榜次数"},
        {"name": "stock_lh_yyb_capital", "description": "龙虎榜营业部-资金实力"},
        {"name": "stock_lhb_hyyyb_em", "description": "每日活跃营业部"},
        {"name": "stock_sina_lhb_jgzz", "description": "机构席位追踪"},
        {"name": "stock_lhb_ggtj_sina", "description": "龙虎榜股东增持"},
        {"name": "stock_lhb_jgzz_sina", "description": "龙虎榜机构增持"},
        {"name": "stock_lhb_jgmmtj_em", "description": "龙虎榜机构买卖统计"},
        {"name": "stock_lhb_yyb_detail_em", "description": "龙虎榜营业部详情"},
        {"name": "stock_lhb_traderstatistic_em", "description": "龙虎榜交易员统计"},
    ],

    # ==================== 八、股东数据 ====================
    "股东数据": [
        {"name": "stock_zh_gbqy_em", "description": "股东人数变化"},
        {"name": "stock_main_stock_holder", "description": "主要股东持股情况"},
        {"name": "stock_fund_stock_holder", "description": "基金股东持股情况"},
        {"name": "stock_circulate_stock_holder", "description": "流通股东持股情况"},
        {"name": "stock_shareholder_change_ths", "description": "股东增减持公告"},
    ],

    # ==================== 九、财务报表 ====================
    "财务报表": [
        {"name": "stock_financial_abstract", "description": "财务摘要"},
        {"name": "stock_financial_analysis_indicator", "description": "财务分析指标"},
        {"name": "stock_financial_analysis_indicator_em", "description": "财务分析指标(同花顺)"},
        {"name": "stock_balance_sheet_by_report_em", "description": "资产负债表(报告期)"},
        {"name": "stock_cash_flow_sheet_by_report_em", "description": "现金流量表(报告期)"},
        {"name": "stock_yjbb_em", "description": "业绩报表"},
        {"name": "stock_yjkb_em", "description": "业绩快报"},
        {"name": "stock_yjyg_em", "description": "业绩预告"},
        {"name": "stock_yysj_em", "description": "营业数据"},
        {"name": "stock_fh_em", "description": "分红送转"},
        {"name": "stock_gpwy_em", "description": "股本演变"},
        {"name": "stock_fhps_em", "description": "分红送转详情"},
        {"name": "stock_fhps_detail_em", "description": "分红送转详细"},
    ],

    # ==================== 十、融资融券 ====================
    "融资融券": [
        {"name": "stock_rzrq_em", "description": "融资融券"},
        {"name": "stock_rzrq_detail_em", "description": "融资融券明细"},
        {"name": "stock_rzrq_latest", "description": "融资融券最新"},
    ],

    # ==================== 十一、大宗交易/限售股 ====================
    "大宗交易/限售股": [
        {"name": "stock_dzjy_em", "description": "大宗交易"},
        {"name": "stock_dzjy_mrmx", "description": "大宗交易明细"},
        {"name": "stock_dzjy_mrtj", "description": "大宗交易统计"},
        {"name": "stock_xsg_fp_em", "description": "限售股解禁"},
        {"name": "stock_xsg_hold_em", "description": "限售股持股"},
        {"name": "stock_restricted_release_summary_em", "description": "限售股解禁汇总"},
        {"name": "stock_restricted_release_detail_em", "description": "限售股解禁明细"},
    ],

    # ==================== 十二、沪深港通 ====================
    "沪深港通": [
        {"name": "stock_hsgt_em", "description": "沪深港通持股"},
        {"name": "stock_hsgt_hist_em", "description": "沪深港通历史数据"},
        {"name": "stock_hsgt_top10_em", "description": "沪深港通top10"},
        {"name": "stock_hsgt_sse_sgt_em", "description": "沪深港通持股标的"},
        {"name": "stock_hsgt_hold_stock_em", "description": "沪深港通持股股票"},
        {"name": "stock_hsgt_individual_em", "description": "沪深港通个人持股"},
        {"name": "stock_hsgt_individual_detail_em", "description": "沪深港通个人持股明细"},
        {"name": "stock_hsgt_stock_statistics_em", "description": "沪深港通股票统计"},
        {"name": "stock_hsgt_fund_flow_summary_em", "description": "沪深港通资金流向汇总"},
        {"name": "stock_hsgt_board_rank_em", "description": "沪深港通板块排名"},
        {"name": "stock_zh_a_gbjg_em", "description": "A股北向资金持股"},
    ],

    # ==================== 十三、基金数据 ====================
    "基金数据": [
        {"name": "fund_etf_spot_em", "description": "ETF实时行情"},
        {"name": "fund_etf_hist_em", "description": "ETF历史数据"},
        {"name": "fund_etf_hist_sina", "description": "ETF历史数据(新浪)"},
        {"name": "fund_etf_category_sina", "description": "ETF分类数据(新浪)"},
        {"name": "fund_etf_fund_daily_em", "description": "ETF基金每日行情"},
        {"name": "fund_etf_scale_sse", "description": "ETF规模数据(上交所)"},
        {"name": "fund_lof_spot_em", "description": "LOF实时行情"},
        {"name": "fund_open_fund_daily_em", "description": "公募基金每日行情"},
        {"name": "fund_open_fund_info_em", "description": "公募基金信息"},
        {"name": "fund_manager_em", "description": "基金经理"},
        {"name": "fund_portfolio_hold_em", "description": "基金持仓"},
        {"name": "fund_fh_em", "description": "基金分红"},
        {"name": "fund_aum_em", "description": "基金资产管理规模"},
        {"name": "fund_cf_em", "description": "基金持仓明细"},
        {"name": "fund_report_fund_hold", "description": "基金持仓报告"},
        {"name": "fund_money_fund_daily_em", "description": "货币基金每日行情"},
    ],

    # ==================== 十四、期货行情 ====================
    "期货行情": [
        {"name": "futures_zh_spot", "description": "期货实时行情"},
        {"name": "futures_zh_realtime", "description": "期货实时行情(详细)"},
        {"name": "futures_zh_daily_sina", "description": "期货日线数据"},
        {"name": "futures_zh_index_spot", "description": "期货指数行情"},
        {"name": "futures_display_main_sina", "description": "期货主力合约排行"},
        {"name": "futures_dce_position_rank", "description": "大商所持仓排名"},
        {"name": "futures_delivery_shfe", "description": "上期所交割数据"},
        {"name": "futures_hist_em", "description": "期货历史数据"},
    ],

    # ==================== 十五、期权行情 ====================
    "期权行情": [
        {"name": "opt_em_spot_sina", "description": "期权实时行情"},
        {"name": "opt_em_daily_sina", "description": "期权日线数据"},
        {"name": "option_current_em", "description": "期权实时行情(东财)"},
        {"name": "option_current_day_sse", "description": "上证期权实时行情"},
        {"name": "option_current_day_szse", "description": "深证期权实时行情"},
        {"name": "option_cffex_hs300_spot_sina", "description": "沪深300期权实时行情"},
        {"name": "option_comm_info", "description": "期权合约信息"},
        {"name": "option_comm_symbol", "description": "期权合约代码"},
        {"name": "option_sse_list_sina", "description": "上证期权列表"},
    ],

    # ==================== 十六、债券数据 ====================
    "债券数据": [
        {"name": "bond_zh_hs_spot", "description": "债券实时行情"},
        {"name": "bond_zh_hs_daily", "description": "债券历史数据"},
        {"name": "bond_zh_hs_cov", "description": "可转债数据"},
        {"name": "bond_zh_hs_cov_spot", "description": "可转债实时行情"},
        {"name": "bond_zh_cov", "description": "可转债概况"},
        {"name": "bond_cb_jsl", "description": "可转债详情(集思录)"},
        {"name": "bond_cb_summary_sina", "description": "可转债概况(新浪)"},
        {"name": "bond_china_yield", "description": "中国国债收益率"},
        {"name": "bond_corporate_issue_cninfo", "description": "企业债发行数据"},
    ],

    # ==================== 十七、宏观数据 ====================
    "宏观数据": [
        {"name": "macro_cn_gdp", "description": "中国GDP"},
        {"name": "macro_cn_cpi", "description": "中国CPI"},
        {"name": "macro_cn_ppi", "description": "中国PPI"},
        {"name": "macro_china_m2_yearly", "description": "中国M2年度数据"},
        {"name": "macro_cn_m1", "description": "中国M1"},
        {"name": "macro_cn_m0", "description": "中国M0"},
        {"name": "macro_cn_shibor", "description": "SHIBOR"},
        {"name": "macro_cn_lpr", "description": "LPR"},
        {"name": "macro_usa_gdp", "description": "美国GDP"},
        {"name": "macro_usa_cpi", "description": "美国CPI"},
        {"name": "macro_usa_ppi", "description": "美国PPI"},
        {"name": "macro_usa_unemployment_rate", "description": "美国失业率"},
        {"name": "macro_usa_interest_rate", "description": "美国利率"},
    ],

    # ==================== 十八、外汇数据 ====================
    "外汇数据": [
        {"name": "forex_zh_spot", "description": "外汇实时行情"},
        {"name": "forex_zh_hist", "description": "外汇历史数据"},
        {"name": "forex_spot_em", "description": "外汇实时(主流)"},
        {"name": "forex_hist_em", "description": "外汇历史(主流)"},
    ],

    # ==================== 十九、新股/IPO ====================
    "新股/IPO": [
        {"name": "stock_ipo_info_em", "description": "新股上市信息"},
        {"name": "stock_ipo_bis_em", "description": "新股申购"},
        {"name": "stock_ipo_declare_em", "description": "IPO申报信息"},
        {"name": "stock_ipo_review_em", "description": "IPO审核信息"},
        {"name": "stock_ipo_info", "description": "IPO信息"},
        {"name": "stock_ipo_summary_cninfo", "description": "IPO概况"},
        {"name": "stock_new_ipo_cninfo", "description": "新股申购(证监会)"},
    ],

    # ==================== 二十、基础信息 ====================
    "基础信息": [
        {"name": "stock_info_a_code_name", "description": "A股代码名称列表"},
        {"name": "stock_info_global_sci_em", "description": "全球市场重要指数"},
        {"name": "stock_szse_sse_info", "description": "深交所/上交所信息"},
        {"name": "stock_daily_adj_em", "description": "日线复权数据"},
        {"name": "stock_fund_screener_em", "description": "股票筛选器"},
        {"name": "stock_info_change_name", "description": "股票更名"},
        {"name": "stock_info_cjzc_em", "description": "股票资金站岗"},
        {"name": "stock_info_sh_name_code", "description": "上交所股票代码"},
        {"name": "stock_info_sz_name_code", "description": "深交所股票代码"},
        {"name": "stock_info_sh_delist", "description": "上交所退市股票"},
        {"name": "stock_info_sz_delist", "description": "深交所退市股票"},
    ],

    # ==================== 二十一、资讯数据 ====================
    "资讯数据": [
        {"name": "stock_news_em", "description": "个股新闻"},
        {"name": "stock_notice_em", "description": "个股公告"},
        {"name": "stock_jgzy_em", "description": "机构调研"},
        {"name": "stock_jgdy_tj_em", "description": "机构调研统计"},
    ],

    # 补充未分类的函数
    "补充函数": [
        # 期货基础信息
        {"name": "futures_comm_info", "description": "期货品种信息"},
        {"name": "futures_contract_info_cffex", "description": "中金所合约信息"},
        {"name": "futures_contract_info_czce", "description": "郑商所合约信息"},
        {"name": "futures_contract_info_dce", "description": "大商所合约信息"},
        {"name": "futures_contract_info_shfe", "description": "上期所合约信息"},
        # 北上广深行情
        {"name": "stock_bj_a_spot_em", "description": "北交所实时行情"},
        {"name": "stock_cy_a_spot_em", "description": "创业板实时行情"},
        {"name": "stock_kc_a_spot_em", "description": "科创板实时行情"},
        {"name": "stock_new_a_spot_em", "description": "新股实时行情"},
        {"name": "stock_sh_a_spot_em", "description": "上交所实时行情"},
        {"name": "stock_sz_a_spot_em", "description": "深交所实时行情"},
        {"name": "stock_zh_a_new_em", "description": "A股新股"},
        {"name": "stock_zh_a_st_em", "description": "A股ST股票"},
        {"name": "stock_zh_a_stop_em", "description": "A股停牌股票"},
        # 板块历史
        {"name": "stock_board_concept_hist_em", "description": "概念板块历史"},
        {"name": "stock_board_industry_hist_em", "description": "行业板块历史"},
        # 板块资金流向补充
        {"name": "stock_fund_flow_concept", "description": "概念资金流向"},
        {"name": "stock_fund_flow_industry", "description": "行业资金流向"},
        {"name": "stock_sector_fund_flow_hist", "description": "板块资金流向历史"},
        {"name": "stock_sector_fund_flow_summary", "description": "板块资金流向汇总"},
        # 龙虎榜补充
        {"name": "stock_lhb_stock_detail_em", "description": "龙虎榜股票详情"},
        {"name": "stock_lhb_stock_detail_date_em", "description": "龙虎榜股票详情(按日期)"},
        {"name": "stock_lhb_yybph_em", "description": "龙虎榜营业部排行"},
        # 指数补充
        {"name": "stock_zh_a_hist_min_em", "description": "A股分钟K线"},
        {"name": "stock_zh_a_hist_pre_min_em", "description": "A股分钟K线(上一个交易日)"},
        {"name": "stock_zh_index_daily_em", "description": "指数日K线(东财)"},
        {"name": "stock_zh_index_spot", "description": "指数实时行情(旧)"},
        # 宏观补充
        {"name": "macro_china_bank_financing", "description": "中国银行融资"},
        {"name": "macro_china_central_bank_balance", "description": "中国央行资产负债表"},
        {"name": "macro_china_consumer_goods_retail", "description": "中国消费品零售"},
        {"name": "macro_china_cpi", "description": "中国CPI(旧)"},
        {"name": "macro_china_czsr", "description": "中国财政收入"},
        {"name": "macro_china_exports_yoy", "description": "中国出口同比"},
        {"name": "macro_china_fdi", "description": "中国FDI"},
        {"name": "macro_china_freight_index", "description": "中国物流运价指数"},
        {"name": "macro_china_gdp", "description": "中国GDP(旧)"},
        {"name": "macro_china_imports_yoy", "description": "中国进口同比"},
        {"name": "macro_china_market_margin", "description": "中国融资融券"},
        {"name": "macro_china_new_house_price", "description": "中国新建住宅价格"},
        {"name": "macro_china_ppi", "description": "中国PPI(旧)"},
        {"name": "macro_china_shibor", "description": "中国SHIBOR(旧)"},
        {"name": "macro_china_stock_market_cap", "description": "中国股市市值"},
        {"name": "macro_china_trade", "description": "中国贸易数据"},
    ],
}


# ========== Akshare API 路由 ==========
@router.get("/akshare/categories")
def get_akshare_categories():
    """获取akshare函数分类"""
    return CATEGORIES


@router.get("/akshare/functions")
def get_akshare_functions():
    """获取akshare函数列表"""
    return list(AKSHARE_FUNCTIONS.values())


@router.get("/akshare/search")
def search_akshare_functions(q: str = ""):
    """搜索akshare函数(支持函数名/描述模糊匹配)"""
    if not q:
        return []

    q_lower = q.lower()
    results = []

    for func_name, func_info in AKSHARE_FUNCTIONS.items():
        # 匹配函数名或描述
        if (q_lower in func_name.lower() or
            q_lower in func_info.get("description", "").lower() or
            q_lower in func_info.get("category", "").lower()):
            results.append(func_info)

    return results


@router.get("/akshare/function/{func_name}")
def get_akshare_function(func_name: str):
    """获取akshare函数详情"""
    if func_name not in AKSHARE_FUNCTIONS:
        raise HTTPException(status_code=404, detail=f"函数 {func_name} 不存在")
    return AKSHARE_FUNCTIONS[func_name]


class AkshareExecuteRequest(BaseModel):
    func_name: str
    params: dict = {}
    use_cache: bool = True  # 是否使用缓存，默认开启


@router.post("/akshare/execute")
def execute_akshare_function(request: AkshareExecuteRequest):
    """执行akshare函数，支持缓存和数据血缘"""
    from app.services.cache_service import CacheService

    func_name = request.func_name
    params = request.params
    use_cache = request.use_cache

    if func_name not in AKSHARE_FUNCTIONS:
        raise HTTPException(status_code=404, detail=f"函数 {func_name} 不存在")

    # 检查是否有缓存配置
    cache_config = CACHE_MODELS.get(func_name)

    # 有缓存配置且启用缓存
    if cache_config and use_cache:
        # 尝试从本地获取
        local_result = CacheService.query_from_local(func_name, params)
        if local_result:
            # 获取血缘信息
            lineage = CacheService.get_lineage_info(func_name, params)
            return {"source": "cache", **local_result, "lineage": lineage}

        # 无缓存，调用 akshare
        result = _call_akshare(func_name, params)

        # 如果需要同步，则存储到数据库
        if cache_config["sync"]:
            CacheService.save_to_local(func_name, params, result)

        # 获取血缘信息
        lineage = CacheService.get_lineage_info(func_name, params)
        return {"source": "akshare", **result, "lineage": lineage}

    # 无缓存配置或禁用缓存，直接调用 akshare
    result = _call_akshare(func_name, params)
    # 直接调用 akshare 时，血缘来源为 akshare
    lineage = {
        "func_name": func_name,
        "source": "akshare",
        "last_updated": None,
        "record_count": len(result.get("data", [])),
    }
    return {"source": "akshare", **result, "lineage": lineage}


def _call_akshare(func_name: str, params: dict):
    """调用 akshare 函数"""
    import akshare as ak
    from sqlmodel import Session

    func = getattr(ak, func_name)

    # 过滤有效参数
    valid_params = {}
    func_params = AKSHARE_FUNCTIONS[func_name]["params"]
    for p in func_params:
        pname = p["name"]
        if pname in params and params[pname]:
            valid_params[pname] = params[pname]

    if valid_params:
        result = func(**valid_params)
    else:
        result = func()

    # 转换为dict格式，处理NaN值
    def clean_value(v):
        import math
        if v is None:
            return None
        if isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                return None
        return v

    def clean_record(record):
        return {k: clean_value(v) for k, v in record.items()}

    if hasattr(result, 'to_dict'):
        records = result.to_dict('records')
        cleaned_records = [clean_record(r) for r in records]
        return {"data": cleaned_records, "columns": list(result.columns) if hasattr(result, 'columns') else []}
    elif isinstance(result, list):
        if result and isinstance(result[0], dict):
            result = [clean_record(r) if isinstance(r, dict) else r for r in result]
        return {"data": result, "columns": []}
    else:
        return {"data": str(result), "columns": []}


@router.post("/akshare/sync/{func_name}")
def sync_function(
    func_name: str,
    trade_date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """手动同步数据到本地数据库"""
    from app.services.cache_service import CacheService

    if func_name not in AKSHARE_FUNCTIONS:
        raise HTTPException(status_code=404, detail=f"函数 {func_name} 不存在")

    cache_config = CACHE_MODELS.get(func_name)
    if not cache_config:
        raise HTTPException(status_code=400, detail=f"该接口不支持同步")

    if not cache_config["sync"]:
        raise HTTPException(status_code=400, detail=f"该接口不需要同步到数据库")

    try:
        # 构建参数
        params = {}
        if trade_date:
            params["date"] = trade_date.replace("-", "")
        if start_date:
            params["start_date"] = start_date.replace("-", "")
        if end_date:
            params["end_date"] = end_date.replace("-", "")

        # 调用 akshare
        result = _call_akshare(func_name, params)

        # 保存到本地
        CacheService.save_to_local(func_name, params, result)

        data = result.get("data", [])
        return {"status": "success", "synced": len(data), "func_name": func_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


# 修复导入
from sqlmodel import Session
