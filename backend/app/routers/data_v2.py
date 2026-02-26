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


# ========== Akshare 函数查询 ==========
# 完整的 akshare 函数列表
AKSHARE_FUNCTIONS = {
    # ========== 股票行情 ==========
    "stock_zh_a_hist": {
        "name": "stock_zh_a_hist",
        "description": "A股历史K线数据",
        "category": "股票行情",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "period", "default": "daily", "description": "周期", "required": False, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权类型", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_spot_em": {
        "name": "stock_zh_a_spot_em",
        "description": "A股实时行情(全部)",
        "category": "股票行情",
        "params": []
    },
    "stock_zh_a_hist_sina": {
        "name": "stock_zh_a_hist_sina",
        "description": "新浪A股历史数据",
        "category": "股票行情",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_zh_a_minute": {
        "name": "stock_zh_a_minute",
        "description": "A股分时数据",
        "category": "股票行情",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "股票代码", "required": True, "type": "str"},
            {"name": "period", "default": "5", "description": "周期(1/5/15/30/60)", "required": False, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权类型", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_cw_daily": {
        "name": "stock_zh_a_cw_daily",
        "description": "A股筹码分布日线",
        "category": "股票行情",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },

    # ========== 指数行情 ==========
    "stock_zh_index_daily": {
        "name": "stock_zh_index_daily",
        "description": "A股指数日K线",
        "category": "指数行情",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "指数代码", "required": True, "type": "str"},
        ]
    },
    "stock_zh_index_spot": {
        "name": "stock_zh_index_spot",
        "description": "A股指数实时行情",
        "category": "指数行情",
        "params": []
    },
    "stock_zh_index_cons": {
        "name": "stock_zh_index_cons",
        "description": "指数成分股",
        "category": "指数行情",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "指数代码", "required": True, "type": "str"},
        ]
    },

    # ========== 涨跌停数据 ==========
    "stock_zh_a_limit_up_em": {
        "name": "stock_zh_a_limit_up_em",
        "description": "A股涨停板",
        "category": "涨跌停",
        "params": [
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_limit_down_em": {
        "name": "stock_zh_a_limit_down_em",
        "description": "A股跌停板",
        "category": "涨跌停",
        "params": [
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "stock_zh_a_limit_up_sina": {
        "name": "stock_zh_a_limit_up_sina",
        "description": "新浪涨停板",
        "category": "涨跌停",
        "params": []
    },

    # ========== 资金流向 ==========
    "stock_individual_fund_flow": {
        "name": "stock_individual_fund_flow",
        "description": "个股资金流向",
        "category": "资金流向",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "market", "default": "上海A股", "description": "市场", "required": False, "type": "str"},
        ]
    },
    "stock_individual_fund_flow_stick": {
        "name": "stock_individual_fund_flow_stick",
        "description": "个股资金流向(支持多日)",
        "category": "资金流向",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "market", "default": "上海A股", "description": "市场", "required": False, "type": "str"},
        ]
    },
    "stock_sector_fund_flow_rank": {
        "name": "stock_sector_fund_flow_rank",
        "description": "板块资金流向排名",
        "category": "资金流向",
        "params": [
            {"name": "indicator", "default": "今日", "description": "指标(今日/5日/10日)", "required": False, "type": "str"},
            {"name": "sector_type", "default": "行业资金流", "description": "板块类型", "required": False, "type": "str"},
        ]
    },
    "stock_fund_flow": {
        "name": "stock_fund_flow",
        "description": "大盘资金流向",
        "category": "资金流向",
        "params": []
    },

    # ========== 龙虎榜 ==========
    "stock_lhb_detail_em": {
        "name": "stock_lhb_detail_em",
        "description": "龙虎榜详情",
        "category": "龙虎榜",
        "params": [
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ]
    },
    "stock_lh_yyb_most": {
        "name": "stock_lh_yyb_most",
        "description": "龙虎榜营业部排行-上榜次数",
        "category": "龙虎榜",
        "params": []
    },
    "stock_lh_yyb_capital": {
        "name": "stock_lh_yyb_capital",
        "description": "龙虎榜营业部排行-资金实力",
        "category": "龙虎榜",
        "params": []
    },
    "stock_lhb_hyyyb_em": {
        "name": "stock_lhb_hyyyb_em",
        "description": "每日活跃营业部",
        "category": "龙虎榜",
        "params": [
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ]
    },
    "stock_sina_lhb_jgzz": {
        "name": "stock_sina_lhb_jgzz",
        "description": "机构席位追踪",
        "category": "龙虎榜",
        "params": [
            {"name": "recent_day", "default": "5", "description": "天数", "required": False, "type": "str"},
        ]
    },
    "stock_zt_pool_em": {
        "name": "stock_zt_pool_em",
        "description": "涨停板池",
        "category": "龙虎榜",
        "params": [
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },

    # ========== 板块数据 ==========
    "stock_board_industry_name_em": {
        "name": "stock_board_industry_name_em",
        "description": "行业板块行情",
        "category": "板块数据",
        "params": []
    },
    "stock_board_concept_name_em": {
        "name": "stock_board_concept_name_em",
        "description": "概念板块行情",
        "category": "板块数据",
        "params": []
    },
    "stock_board_industry_cons_em": {
        "name": "stock_board_industry_cons_em",
        "description": "行业板块成分股",
        "category": "板块数据",
        "params": [
            {"name": "symbol", "default": "半导体", "description": "板块名称", "required": True, "type": "str"},
        ]
    },
    "stock_board_concept_cons_em": {
        "name": "stock_board_concept_cons_em",
        "description": "概念板块成分股",
        "category": "板块数据",
        "params": [
            {"name": "symbol", "default": "人工智能", "description": "板块名称", "required": True, "type": "str"},
        ]
    },

    # ========== 股票信息 ==========
    "stock_info_a_code_name": {
        "name": "stock_info_a_code_name",
        "description": "A股代码名称列表",
        "category": "股票信息",
        "params": []
    },
    "stock_szse_sse_info": {
        "name": "stock_szse_sse_info",
        "description": "深交所/上交所信息",
        "category": "股票信息",
        "params": []
    },
    "stock_info_global_sci_em": {
        "name": "stock_info_global_sci_em",
        "description": "全球市场重要指数",
        "category": "股票信息",
        "params": []
    },
    "stock_info_hk_sell_em": {
        "name": "stock_info_hk_sell_em",
        "description": "港股卖空数据",
        "category": "股票信息",
        "params": []
    },

    # ========== 财务数据 ==========
    "stock_financial_abstract": {
        "name": "stock_financial_abstract",
        "description": "财务摘要",
        "category": "财务数据",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_financial_analysis_indicator": {
        "name": "stock_financial_analysis_indicator",
        "description": "财务分析指标",
        "category": "财务数据",
        "params": [
            {"name": "stock", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "indicator", "default": "按报告期", "description": "指标类型", "required": False, "type": "str"},
        ]
    },
    "stock_yjbb_em": {
        "name": "stock_yjbb_em",
        "description": "业绩报表",
        "category": "财务数据",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_yysj_em": {
        "name": "stock_yysj_em",
        "description": "营业数据",
        "category": "财务数据",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_fh_em": {
        "name": "stock_fh_em",
        "description": "分红送转",
        "category": "财务数据",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_gpwy_em": {
        "name": "stock_gpwy_em",
        "description": "股本演变",
        "category": "财务数据",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========== 沪深港通 ==========
    "stock_hsgt_top10_em": {
        "name": "stock_hsgt_top10_em",
        "description": "沪深港通top10",
        "category": "沪深港通",
        "params": [
            {"name": "symbol", "default": "北向", "description": "类型(北向/南向)", "required": True, "type": "str"},
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "stock_hsgt_hist_em": {
        "name": "stock_hsgt_hist_em",
        "description": "沪深港通历史数据",
        "category": "沪深港通",
        "params": []
    },
    "stock_hsgt_sse_sgt_em": {
        "name": "stock_hsgt_sse_sgt_em",
        "description": "沪深港通持股标的",
        "category": "沪深港通",
        "params": []
    },

    # ========== 新股数据 ==========
    "stock_ipo_info_em": {
        "name": "stock_ipo_info_em",
        "description": "新股上市信息",
        "category": "新股数据",
        "params": []
    },
    "stock_ipo_bis_em": {
        "name": "stock_ipo_bis_em",
        "description": "新股申购",
        "category": "新股数据",
        "params": []
    },

    # ========== 复权数据 ==========
    "stock_daily_adj_em": {
        "name": "stock_daily_adj_em",
        "description": "日线复权数据",
        "category": "复权数据",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
            {"name": "adjust", "default": "qfq", "description": "复权类型", "required": False, "type": "str"},
        ]
    },

    # ========== 大盘数据 ==========
    "stock_zh_a_treda": {
        "name": "stock_zh_a_treda",
        "description": "A股市场总貌",
        "category": "大盘数据",
        "params": []
    },
    "stock_zh_a_tredb": {
        "name": "stock_zh_a_tredb",
        "description": "A股市场交易详情",
        "category": "大盘数据",
        "params": []
    },
    "stock_zh_a_trade": {
        "name": "stock_zh_a_trade",
        "description": "A股市场资金流向",
        "category": "大盘数据",
        "params": []
    },

    # ========== 融资融券 ==========
    "stock_rzrq_em": {
        "name": "stock_rzrq_em",
        "description": "融资融券",
        "category": "融资融券",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "stock_rzrq_detail_em": {
        "name": "stock_rzrq_detail_em",
        "description": "融资融券明细",
        "category": "融资融券",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_rzrq_fund_flow": {
        "name": "stock_rzrq_fund_flow",
        "description": "融资融券资金流向",
        "category": "融资融券",
        "params": []
    },

    # ========== 限售股 ==========
    "stock_xsg_fp_em": {
        "name": "stock_xsg_fp_em",
        "description": "限售股解禁",
        "category": "限售股",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },
    "stock_xsg_hold_em": {
        "name": "stock_xsg_hold_em",
        "description": "限售股持股",
        "category": "限售股",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========== 大宗交易 ==========
    "stock_dzjy_em": {
        "name": "stock_dzjy_em",
        "description": "大宗交易",
        "category": "大宗交易",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========== 股东人数 ==========
    "stock_zh_gbqy_em": {
        "name": "stock_zh_gbqy_em",
        "description": "股东人数变化",
        "category": "股东数据",
        "params": [
            {"name": "symbol", "default": "600519", "description": "股票代码", "required": True, "type": "str"},
        ]
    },

    # ========== 机构调研 ==========
    "stock_jgzy_em": {
        "name": "stock_jgzy_em",
        "description": "机构调研",
        "category": "机构调研",
        "params": []
    },

    # ========== 资金流向 ==========
    "stock_market_fund_flow": {
        "name": "stock_market_fund_flow",
        "description": "市场资金流向",
        "category": "资金流向",
        "params": []
    },
    "stock_fund_flow_ggyl": {
        "name": "stock_fund_flow_ggyl",
        "description": "资金流向-归公流向",
        "category": "资金流向",
        "params": []
    },

    # ========== 期货数据 ==========
    "futures_zh_daily_sina": {
        "name": "futures_zh_daily_sina",
        "description": "期货日线数据",
        "category": "期货数据",
        "params": [
            {"name": "symbol", "default": "RU9999", "description": "期货代码", "required": True, "type": "str"},
        ]
    },
    "futures_zh_spot": {
        "name": "futures_zh_spot",
        "description": "期货实时行情",
        "category": "期货数据",
        "params": []
    },

    # ========== 期权数据 ==========
    "opt_em_daily_sina": {
        "name": "opt_em_daily_sina",
        "description": "期权日线数据",
        "category": "期权数据",
        "params": [
            {"name": "symbol", "default": "510050C2306", "description": "期权代码", "required": True, "type": "str"},
        ]
    },
    "opt_em_spot_sina": {
        "name": "opt_em_spot_sina",
        "description": "期权实时行情",
        "category": "期权数据",
        "params": []
    },

    # ========== 可转债 ==========
    "bond_zh_hs_cov": {
        "name": "bond_zh_hs_cov",
        "description": "可转债数据",
        "category": "可转债",
        "params": []
    },
    "bond_zh_hs_cov_spot": {
        "name": "bond_zh_hs_cov_spot",
        "description": "可转债实时行情",
        "category": "可转债",
        "params": []
    },

    # ========== 基金数据 ==========
    "fund_etf_hist_em": {
        "name": "fund_etf_hist_em",
        "description": "ETF历史数据",
        "category": "基金数据",
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
        "category": "基金数据",
        "params": []
    },
    "fund_lof_spot_em": {
        "name": "fund_lof_spot_em",
        "description": "LOF实时行情",
        "category": "基金数据",
        "params": []
    },

    # ========== 外汇数据 ==========
    "forex_zh_spot": {
        "name": "forex_zh_spot",
        "description": "外汇实时行情",
        "category": "外汇数据",
        "params": []
    },
    "forex_zh_hist": {
        "name": "forex_zh_hist",
        "description": "外汇历史数据",
        "category": "外汇数据",
        "params": [
            {"name": "symbol", "default": "USD/CNY", "description": "货币对", "required": True, "type": "str"},
            {"name": "start_date", "default": "20250101", "description": "开始日期", "required": True, "type": "str"},
            {"name": "end_date", "default": "20250227", "description": "结束日期", "required": True, "type": "str"},
        ]
    },

    # ========== 宏观数据 ==========
    "macro_cn_gdp": {
        "name": "macro_cn_gdp",
        "description": "中国GDP数据",
        "category": "宏观数据",
        "params": []
    },
    "macro_cn_cpi": {
        "name": "macro_cn_cpi",
        "description": "中国CPI数据",
        "category": "宏观数据",
        "params": []
    },
    "macro_cn_ppi": {
        "name": "macro_cn_ppi",
        "description": "中国PPI数据",
        "category": "宏观数据",
        "params": []
    },
    "macro_cn_m2": {
        "name": "macro_cn_m2",
        "description": "中国M2数据",
        "category": "宏观数据",
        "params": []
    },
}


# 分类
CATEGORIES = {
    "股票行情": [
        {"name": "stock_zh_a_hist", "description": "A股历史K线数据"},
        {"name": "stock_zh_a_spot_em", "description": "A股实时行情"},
        {"name": "stock_zh_a_hist_sina", "description": "新浪A股历史数据"},
        {"name": "stock_zh_a_minute", "description": "A股分时数据"},
        {"name": "stock_zh_a_cw_daily", "description": "A股筹码分布日线"},
    ],
    "指数行情": [
        {"name": "stock_zh_index_daily", "description": "A股指数日K线"},
        {"name": "stock_zh_index_spot", "description": "A股指数实时行情"},
        {"name": "stock_zh_index_cons", "description": "指数成分股"},
    ],
    "涨跌停": [
        {"name": "stock_zh_a_limit_up_em", "description": "A股涨停板"},
        {"name": "stock_zh_a_limit_down_em", "description": "A股跌停板"},
        {"name": "stock_zh_a_limit_up_sina", "description": "新浪涨停板"},
    ],
    "资金流向": [
        {"name": "stock_individual_fund_flow", "description": "个股资金流向"},
        {"name": "stock_individual_fund_flow_stick", "description": "个股资金流向(多日)"},
        {"name": "stock_sector_fund_flow_rank", "description": "板块资金流向排名"},
        {"name": "stock_fund_flow", "description": "大盘资金流向"},
        {"name": "stock_market_fund_flow", "description": "市场资金流向"},
        {"name": "stock_fund_flow_ggyl", "description": "资金流向-归公流向"},
    ],
    "龙虎榜": [
        {"name": "stock_lhb_detail_em", "description": "龙虎榜详情"},
        {"name": "stock_lh_yyb_most", "description": "龙虎榜营业部排行-上榜次数"},
        {"name": "stock_lh_yyb_capital", "description": "龙虎榜营业部排行-资金实力"},
        {"name": "stock_lhb_hyyyb_em", "description": "每日活跃营业部"},
        {"name": "stock_sina_lhb_jgzz", "description": "机构席位追踪"},
        {"name": "stock_zt_pool_em", "description": "涨停板池"},
    ],
    "板块数据": [
        {"name": "stock_board_industry_name_em", "description": "行业板块行情"},
        {"name": "stock_board_concept_name_em", "description": "概念板块行情"},
        {"name": "stock_board_industry_cons_em", "description": "行业板块成分股"},
        {"name": "stock_board_concept_cons_em", "description": "概念板块成分股"},
    ],
    "股票信息": [
        {"name": "stock_info_a_code_name", "description": "A股代码名称列表"},
        {"name": "stock_szse_sse_info", "description": "深交所/上交所信息"},
        {"name": "stock_info_global_sci_em", "description": "全球市场重要指数"},
        {"name": "stock_info_hk_sell_em", "description": "港股卖空数据"},
    ],
    "财务数据": [
        {"name": "stock_financial_abstract", "description": "财务摘要"},
        {"name": "stock_financial_analysis_indicator", "description": "财务分析指标"},
        {"name": "stock_yjbb_em", "description": "业绩报表"},
        {"name": "stock_yysj_em", "description": "营业数据"},
        {"name": "stock_fh_em", "description": "分红送转"},
        {"name": "stock_gpwy_em", "description": "股本演变"},
    ],
    "沪深港通": [
        {"name": "stock_hsgt_top10_em", "description": "沪深港通top10"},
        {"name": "stock_hsgt_hist_em", "description": "沪深港通历史数据"},
        {"name": "stock_hsgt_sse_sgt_em", "description": "沪深港通持股标的"},
    ],
    "新股数据": [
        {"name": "stock_ipo_info_em", "description": "新股上市信息"},
        {"name": "stock_ipo_bis_em", "description": "新股申购"},
    ],
    "复权数据": [
        {"name": "stock_daily_adj_em", "description": "日线复权数据"},
    ],
    "大盘数据": [
        {"name": "stock_zh_a_treda", "description": "A股市场总貌"},
        {"name": "stock_zh_a_tredb", "description": "A股市场交易详情"},
        {"name": "stock_zh_a_trade", "description": "A股市场资金流向"},
    ],
    "融资融券": [
        {"name": "stock_rzrq_em", "description": "融资融券"},
        {"name": "stock_rzrq_detail_em", "description": "融资融券明细"},
        {"name": "stock_rzrq_fund_flow", "description": "融资融券资金流向"},
    ],
    "限售股": [
        {"name": "stock_xsg_fp_em", "description": "限售股解禁"},
        {"name": "stock_xsg_hold_em", "description": "限售股持股"},
    ],
    "大宗交易": [
        {"name": "stock_dzjy_em", "description": "大宗交易"},
    ],
    "股东数据": [
        {"name": "stock_zh_gbqy_em", "description": "股东人数变化"},
    ],
    "机构调研": [
        {"name": "stock_jgzy_em", "description": "机构调研"},
    ],
    "期货数据": [
        {"name": "futures_zh_daily_sina", "description": "期货日线数据"},
        {"name": "futures_zh_spot", "description": "期货实时行情"},
    ],
    "期权数据": [
        {"name": "opt_em_daily_sina", "description": "期权日线数据"},
        {"name": "opt_em_spot_sina", "description": "期权实时行情"},
    ],
    "可转债": [
        {"name": "bond_zh_hs_cov", "description": "可转债数据"},
        {"name": "bond_zh_hs_cov_spot", "description": "可转债实时行情"},
    ],
    "基金数据": [
        {"name": "fund_etf_hist_em", "description": "ETF历史数据"},
        {"name": "fund_etf_spot_em", "description": "ETF实时行情"},
        {"name": "fund_lof_spot_em", "description": "LOF实时行情"},
    ],
    "外汇数据": [
        {"name": "forex_zh_spot", "description": "外汇实时行情"},
        {"name": "forex_zh_hist", "description": "外汇历史数据"},
    ],
    "宏观数据": [
        {"name": "macro_cn_gdp", "description": "中国GDP数据"},
        {"name": "macro_cn_cpi", "description": "中国CPI数据"},
        {"name": "macro_cn_ppi", "description": "中国PPI数据"},
        {"name": "macro_cn_m2", "description": "中国M2数据"},
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


@router.get("/akshare/function/{func_name}")
def get_akshare_function(func_name: str):
    """获取akshare函数详情"""
    if func_name not in AKSHARE_FUNCTIONS:
        raise HTTPException(status_code=404, detail=f"函数 {func_name} 不存在")
    return AKSHARE_FUNCTIONS[func_name]


@router.post("/akshare/execute")
def execute_akshare_function(func_name: str, params: dict = {}):
    """执行akshare函数"""
    if func_name not in AKSHARE_FUNCTIONS:
        raise HTTPException(status_code=404, detail=f"函数 {func_name} 不存在")

    try:
        import akshare as ak
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

        # 转换为dict格式
        if hasattr(result, 'to_dict'):
            return {"data": result.to_dict('records'), "columns": list(result.columns) if hasattr(result, 'columns') else []}
        elif isinstance(result, list):
            return {"data": result, "columns": []}
        else:
            return {"data": str(result), "columns": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")
