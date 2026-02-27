"""
股票基础数据模型
对应数据库 astock.stock_info
"""
from typing import Optional
from sqlmodel import SQLModel, Field


class StockInfo(SQLModel, table=True):
    """股票代码映射"""
    __tablename__ = "stock_info"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(description="股票代码", max_length=10)
    name: str = Field(description="股票名称", max_length=50)
