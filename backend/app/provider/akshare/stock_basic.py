"""
股票基础数据接口
包含：股票代码映射、个股基本信息
"""
from typing import List, Optional, Union

from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class StockInfoInput(BaseModel):
    """入参 - 股票代码映射"""
    pass


class StockInfoOutput(BaseModel):
    """出参 - 股票代码映射"""
    code: str = Field(description="股票代码")
    name: str = Field(description="股票名称")


class StockIndividualInfoInput(BaseModel):
    """入参 - 个股基本信息"""
    symbol: str = Field(description="股票代码，如 000001")


class StockIndividualInfoOutput(BaseModel):
    """出参 - 个股基本信息"""
    item: str = Field(description="指标名称")
    value: Union[str, float, int] = Field(default=None, description="指标值")


# ============ 接口函数 ============

def get_stock_info_a_code_name() -> List[StockInfoOutput]:
    """
    接口名称：沪深京A股股票代码和简称
    接口代码：stock_info_a_code_name
    接口描述：沪深京 A 股股票代码和股票简称数据
    限量：单次获取所有 A 股股票代码和简称数据
    """
    df = ak.stock_info_a_code_name()
    records = df.to_dict(orient="records")
    return [StockInfoOutput(**r) for r in records]


def get_stock_individual_info_em(symbol: str) -> List[StockIndividualInfoOutput]:
    """
    接口名称：个股股票信息
    接口代码：stock_individual_info_em
    接口描述：东方财富-个股-股票信息
    限量：单次返回指定 symbol 的个股信息

    入参：
        - symbol: str - 股票代码，如 000001
    """
    df = ak.stock_individual_info_em(symbol=symbol)
    records = df.to_dict(orient="records")
    return [StockIndividualInfoOutput(**r) for r in records]
