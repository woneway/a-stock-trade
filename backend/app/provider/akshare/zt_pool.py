"""
涨停板数据接口
包含：今日涨停池昨日涨停池、跌停股池、炸板股池
"""
from typing import List, Optional
from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class ZtPoolInput(BaseModel):
    """入参 - 涨停股池"""
    date: str = Field(description="日期，格式 YYYYMMDD")


class ZtPoolOutput(BaseModel):
    """出参 - 涨停股池"""
    序号: Optional[int] = Field(default=None, description="序号")
    代码: Optional[str] = Field(default=None, description="股票代码")
    名称: Optional[str] = Field(default=None, description="股票名称")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    最新价: Optional[float] = Field(default=None, description="最新价")
    成交额: Optional[float] = Field(default=None, description="成交额(元)")
    换手率: Optional[float] = Field(default=None, description="换手率(%)")
    首次封板时间: Optional[str] = Field(default=None, description="首次封板时间")
    最后封板时间: Optional[str] = Field(default=None, description="最后封板时间")
    炸板次数: Optional[int] = Field(default=None, description="炸板次数")
    涨停统计: Optional[str] = Field(default=None, description="涨停统计")
    连板数: Optional[int] = Field(default=None, description="连板数")
    所属行业: Optional[str] = Field(default=None, description="所属行业")


class ZtPoolPreviousOutput(BaseModel):
    """出参 - 昨日涨停股池"""
    序号: Optional[int] = Field(default=None, description="序号")
    代码: Optional[str] = Field(default=None, description="股票代码")
    名称: Optional[str] = Field(default=None, description="股票名称")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    最新价: Optional[float] = Field(default=None, description="最新价")
    换手率: Optional[float] = Field(default=None, description="换手率(%)")
    振幅: Optional[float] = Field(default=None, description="振幅(%)")
    昨日封板时间: Optional[str] = Field(default=None, description="昨日封板时间")
    昨日连板数: Optional[int] = Field(default=None, description="昨日连板数")
    所属行业: Optional[str] = Field(default=None, description="所属行业")


class ZtPoolDtgcOutput(BaseModel):
    """出参 - 跌停股池"""
    序号: Optional[int] = Field(default=None, description="序号")
    代码: Optional[str] = Field(default=None, description="股票代码")
    名称: Optional[str] = Field(default=None, description="股票名称")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    最新价: Optional[float] = Field(default=None, description="最新价")
    连续跌停: Optional[int] = Field(default=None, description="连续跌停天数")
    所属行业: Optional[str] = Field(default=None, description="所属行业")


class ZtPoolZbgcOutput(BaseModel):
    """出参 - 炸板股池"""
    序号: Optional[int] = Field(default=None, description="序号")
    代码: Optional[str] = Field(default=None, description="股票代码")
    名称: Optional[str] = Field(default=None, description="股票名称")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    炸板次数: Optional[int] = Field(default=None, description="炸板次数")
    所属行业: Optional[str] = Field(default=None, description="所属行业")


# ============ 接口函数 ============

def get_zt_pool_em(date: str) -> List[ZtPoolOutput]:
    """涨停股池"""
    df = ak.stock_zt_pool_em(date=date)
    records = df.to_dict(orient="records")
    return [ZtPoolOutput(**r) for r in records]


def get_zt_pool_previous_em(date: str) -> List[ZtPoolPreviousOutput]:
    """昨日涨停股池"""
    df = ak.stock_zt_pool_previous_em(date=date)
    records = df.to_dict(orient="records")
    return [ZtPoolPreviousOutput(**r) for r in records]


def get_zt_pool_dtgc_em(date: str) -> List[ZtPoolDtgcOutput]:
    """跌停股池"""
    df = ak.stock_zt_pool_dtgc_em(date=date)
    records = df.to_dict(orient="records")
    return [ZtPoolDtgcOutput(**r) for r in records]


def get_zt_pool_zbgc_em(date: str) -> List[ZtPoolZbgcOutput]:
    """炸板股池"""
    df = ak.stock_zt_pool_zbgc_em(date=date)
    records = df.to_dict(orient="records")
    return [ZtPoolZbgcOutput(**r) for r in records]
