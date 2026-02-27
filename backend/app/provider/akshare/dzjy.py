"""
大宗交易数据接口
包含：每日明细、每日统计
"""
from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class DzjyMrmxInput(BaseModel):
    """入参 - 大宗交易每日明细"""
    symbol: str = Field(default="A股", description="类型：A股/B股/基金/债券")
    start_date: str = Field(description="开始日期，格式 YYYYMMDD")
    end_date: str = Field(description="结束日期，格式 YYYYMMDD")


class DzjyMrmxOutput(BaseModel):
    """出参 - 大宗交易每日明细"""
    序号: Optional[int] = Field(default=None, description="序号")
    交易日期: Optional[Union[str, date]] = Field(default=None, description="交易日期")
    证券代码: Optional[str] = Field(default=None, description="证券代码")
    证券简称: Optional[str] = Field(default=None, description="证券简称")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    收盘价: Optional[float] = Field(default=None, description="收盘价")
    成交价: Optional[float] = Field(default=None, description="成交价")
    折溢率: Optional[float] = Field(default=None, description="折溢率(%)")
    成交量: Optional[float] = Field(default=None, description="成交量(股)")
    成交额: Optional[float] = Field(default=None, description="成交额(元)")
    成交额_流通市值: Optional[float] = Field(default=None, description="成交额/流通市值")
    买方营业部: Optional[str] = Field(default=None, description="买方营业部")
    卖方营业部: Optional[str] = Field(default=None, description="卖方营业部")


class DzjyMrtjInput(BaseModel):
    """入参 - 大宗交易每日统计"""
    start_date: str = Field(description="开始日期，格式 YYYYMMDD")
    end_date: str = Field(description="结束日期，格式 YYYYMMDD")


class DzjyMrtjOutput(BaseModel):
    """出参 - 大宗交易每日统计"""
    序号: Optional[int] = Field(default=None, description="序号")
    交易日期: Optional[Union[str, date]] = Field(default=None, description="交易日期")
    证券代码: Optional[str] = Field(default=None, description="证券代码")
    证券简称: Optional[str] = Field(default=None, description="证券简称")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    收盘价: Optional[float] = Field(default=None, description="收盘价")
    成交价: Optional[float] = Field(default=None, description="成交价")
    折溢率: Optional[float] = Field(default=None, description="折溢率(%)")
    成交笔数: Optional[int] = Field(default=None, description="成交笔数")
    成交总量: Optional[float] = Field(default=None, description="成交总量(万股)")
    成交总额: Optional[float] = Field(default=None, description="成交总额(万元)")
    成交总额_流通市值: Optional[float] = Field(default=None, description="成交总额/流通市值")


# ============ 接口函数 ============

def get_dzjy_mrmx(
    symbol: str = "A股",
    start_date: str = "20240101",
    end_date: str = "20241231"
) -> List[DzjyMrmxOutput]:
    """大宗交易每日明细"""
    df = ak.stock_dzjy_mrmx(symbol=symbol, start_date=start_date, end_date=end_date)
    records = df.to_dict(orient="records")
    return [DzjyMrmxOutput(**r) for r in records]


def get_dzjy_mrtj(start_date: str, end_date: str) -> List[DzjyMrtjOutput]:
    """大宗交易每日统计"""
    df = ak.stock_dzjy_mrtj(start_date=start_date, end_date=end_date)
    records = df.to_dict(orient="records")
    return [DzjyMrtjOutput(**r) for r in records]
