"""
融资融券数据接口
包含：上交所融资融券、深交所融资融券、两融账户统计
"""
from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class MarginSseInput(BaseModel):
    """入参 - 上交所融资融券"""
    start_date: str = Field(description="开始日期，格式 YYYYMMDD")
    end_date: str = Field(description="结束日期，格式 YYYYMMDD")


class MarginSseOutput(BaseModel):
    """出参 - 上交所融资融券"""
    信用交易日期: Optional[Union[str, date]] = Field(default=None, description="信用交易日期")
    融资余额: Optional[float] = Field(default=None, description="融资余额(元)")
    融资买入额: Optional[float] = Field(default=None, description="融资买入额(元)")
    融券余量: Optional[float] = Field(default=None, description="融券余量(股)")
    融资融券余额: Optional[float] = Field(default=None, description="融资融券余额(元)")


class MarginSzseOutput(BaseModel):
    """出参 - 深交所融资融券"""
    信用交易日期: Optional[Union[str, date]] = Field(default=None, description="信用交易日期")
    融资余额: Optional[float] = Field(default=None, description="融资余额(元)")
    融资买入额: Optional[float] = Field(default=None, description="融资买入额(元)")
    融券卖出量: Optional[float] = Field(default=None, description="融券卖出量(股)")
    融资融券余额: Optional[float] = Field(default=None, description="融资融券余额(元)")


class MarginAccountInfoOutput(BaseModel):
    """出参 - 两融账户统计"""
    日期: Optional[Union[str, date]] = Field(default=None, description="日期")
    融资余额: Optional[float] = Field(default=None, description="融资余额(亿元)")
    融券余额: Optional[float] = Field(default=None, description="融券余额(亿元)")
    融资买入额: Optional[float] = Field(default=None, description="融资买入额(亿元)")
    融券卖出额: Optional[float] = Field(default=None, description="融券卖出额(亿元)")
    证券公司数量: Optional[float] = Field(default=None, description="证券公司数量")
    营业部数量: Optional[float] = Field(default=None, description="营业部数量")
    个人投资者数量: Optional[float] = Field(default=None, description="个人投资者数量")
    机构投资者数量: Optional[float] = Field(default=None, description="机构投资者数量")
    参与交易的投资者数量: Optional[float] = Field(default=None, description="参与交易的投资者数量")
    有融资融券负债的投资者数量: Optional[float] = Field(default=None, description="有融资融券负债的投资者数量")
    担保物总价值: Optional[float] = Field(default=None, description="担保物总价值(亿元)")
    平均维持担保比例: Optional[float] = Field(default=None, description="平均维持担保比例(%)")


# ============ 接口函数 ============

def get_margin_sse(start_date: str, end_date: str) -> List[MarginSseOutput]:
    """上交所融资融券汇总"""
    df = ak.stock_margin_sse(start_date=start_date, end_date=end_date)
    records = df.to_dict(orient="records")
    return [MarginSseOutput(**r) for r in records]


def get_margin_szse(date: str) -> List[MarginSzseOutput]:
    """深交所融资融券汇总"""
    df = ak.stock_margin_szse(date=date)
    records = df.to_dict(orient="records")
    return [MarginSzseOutput(**r) for r in records]


def get_margin_account_info() -> List[MarginAccountInfoOutput]:
    """两融账户统计"""
    df = ak.stock_margin_account_info()
    records = df.to_dict(orient="records")
    return [MarginAccountInfoOutput(**r) for r in records]
