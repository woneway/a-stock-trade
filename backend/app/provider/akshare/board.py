"""
行业板块数据接口
包含：概念板块、行业板块实时行情
"""
from typing import List, Optional
from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class BoardConceptNameOutput(BaseModel):
    """出参 - 概念板块实时行情"""
    排名: Optional[int] = Field(default=None, description="排名")
    板块名称: Optional[str] = Field(default=None, description="板块名称")
    板块代码: Optional[str] = Field(default=None, description="板块代码")
    最新价: Optional[float] = Field(default=None, description="最新价")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    总市值: Optional[float] = Field(default=None, description="总市值")
    换手率: Optional[float] = Field(default=None, description="换手率(%)")
    上涨家数: Optional[int] = Field(default=None, description="上涨家数")
    下跌家数: Optional[int] = Field(default=None, description="下跌家数")
    领涨股票: Optional[str] = Field(default=None, description="领涨股票")


class BoardIndustryNameOutput(BaseModel):
    """出参 - 行业板块实时行情"""
    排名: Optional[int] = Field(default=None, description="排名")
    板块名称: Optional[str] = Field(default=None, description="板块名称")
    板块代码: Optional[str] = Field(default=None, description="板块代码")
    最新价: Optional[float] = Field(default=None, description="最新价")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    总市值: Optional[float] = Field(default=None, description="总市值")
    换手率: Optional[float] = Field(default=None, description="换手率(%)")
    上涨家数: Optional[int] = Field(default=None, description="上涨家数")
    下跌家数: Optional[int] = Field(default=None, description="下跌家数")
    领涨股票: Optional[str] = Field(default=None, description="领涨股票")


# ============ 接口函数 ============

def get_board_concept_name_em() -> List[BoardConceptNameOutput]:
    """概念板块实时行情"""
    df = ak.stock_board_concept_name_em()
    records = df.to_dict(orient="records")
    return [BoardConceptNameOutput(**r) for r in records]


def get_board_industry_name_em() -> List[BoardIndustryNameOutput]:
    """行业板块实时行情"""
    df = ak.stock_board_industry_name_em()
    records = df.to_dict(orient="records")
    return [BoardIndustryNameOutput(**r) for r in records]
