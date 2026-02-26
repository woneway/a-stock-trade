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
AKSHARE_FUNCTIONS = {
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
    "stock_zh_index_daily": {
        "name": "stock_zh_index_daily",
        "description": "A股指数日K线",
        "category": "指数行情",
        "params": [
            {"name": "symbol", "default": "sh000001", "description": "指数代码", "required": True, "type": "str"},
        ]
    },
    "stock_zh_a_spot_em": {
        "name": "stock_zh_a_spot_em",
        "description": "A股实时行情",
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
    "stock_info_a_code_name": {
        "name": "stock_info_a_code_name",
        "description": "A股代码名称列表",
        "category": "股票信息",
        "params": []
    },
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
    "stock_szse_sse_info": {
        "name": "stock_szse_sse_info",
        "description": "深交所/上交所信息",
        "category": "股票信息",
        "params": []
    },
    "stock_zt_pool_em": {
        "name": "stock_zt_pool_em",
        "description": "涨停板池",
        "category": "龙虎榜",
        "params": [
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
    "stock_lhb_em": {
        "name": "stock_lhb_em",
        "description": "龙虎榜数据",
        "category": "龙虎榜",
        "params": [
            {"name": "start_date", "default": "", "description": "开始日期", "required": False, "type": "str"},
            {"name": "end_date", "default": "", "description": "结束日期", "required": False, "type": "str"},
        ]
    },
    "stock_hsgt_top10_em": {
        "name": "stock_hsgt_top10_em",
        "description": "沪深港通top10",
        "category": "沪深港通",
        "params": [
            {"name": "symbol", "default": "北向", "description": "类型", "required": True, "type": "str"},
            {"name": "date", "default": "", "description": "日期", "required": False, "type": "str"},
        ]
    },
}

CATEGORIES = {
    "股票行情": [
        {"name": "stock_zh_a_hist", "description": "A股历史K线数据"},
        {"name": "stock_zh_a_spot_em", "description": "A股实时行情"},
        {"name": "stock_zh_a_hist_sina", "description": "新浪A股历史数据"},
    ],
    "指数行情": [
        {"name": "stock_zh_index_daily", "description": "A股指数日K线"},
    ],
    "股票信息": [
        {"name": "stock_info_a_code_name", "description": "A股代码名称列表"},
        {"name": "stock_szse_sse_info", "description": "深交所/上交所信息"},
    ],
    "财务数据": [
        {"name": "stock_financial_abstract", "description": "财务摘要"},
        {"name": "stock_financial_analysis_indicator", "description": "财务分析指标"},
        {"name": "stock_yjbb_em", "description": "业绩报表"},
    ],
    "龙虎榜": [
        {"name": "stock_zt_pool_em", "description": "涨停板池"},
        {"name": "stock_lhb_em", "description": "龙虎榜数据"},
    ],
    "沪深港通": [
        {"name": "stock_hsgt_top10_em", "description": "沪深港通top10"},
    ],
}


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


# 修复导入
from sqlmodel import Session
