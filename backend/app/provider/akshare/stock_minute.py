"""
分时数据接口
包含：分时数据
"""
from typing import List, Optional
from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class StockZhAHistMinEmInput(BaseModel):
    """入参 - 分时数据"""
    symbol: str = Field(description="股票代码，如 000300")
    start_date: Optional[str] = Field(default=None, description="开始日期时间，格式 YYYY-MM-DD HH:MM:SS")
    end_date: Optional[str] = Field(default=None, description="结束日期时间，格式 YYYY-MM-DD HH:MM:SS")
    period: str = Field(default="5", description="周期：1/5/15/30/60分钟")
    adjust: str = Field(default="", description="复权类型：qfq前复权/hfq后复权/空字符串不复权")


class StockZhAHistMinEmOutput(BaseModel):
    """出参 - 分时数据"""
    时间: Optional[str] = Field(default=None, description="时间")
    开盘: Optional[float] = Field(default=None, description="开盘价")
    收盘: Optional[float] = Field(default=None, description="收盘价")
    最高: Optional[float] = Field(default=None, description="最高价")
    最低: Optional[float] = Field(default=None, description="最低价")
    成交量: Optional[float] = Field(default=None, description="成交量(手)")
    成交额: Optional[float] = Field(default=None, description="成交额(元)")
    均价: Optional[float] = Field(default=None, description="均价")


# ============ 接口函数 ============

def get_stock_zh_a_hist_min_em(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "5",
    adjust: str = ""
) -> List[StockZhAHistMinEmOutput]:
    """每日分时行情"""
    df = ak.stock_zh_a_hist_min_em(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        period=period,
        adjust=adjust
    )
    records = df.to_dict(orient="records")
    return [StockZhAHistMinEmOutput(**r) for r in records]
