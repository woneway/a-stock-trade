"""
资金流向数据接口
包含：大盘资金流向、板块资金流排名、个股资金流排名、个股资金流历史
"""
from datetime import date
from typing import List, Optional, Union

from pydantic import BaseModel, Field
import akshare as ak


# ============ Pydantic Schema 定义 ============

class MarketFundFlowInput(BaseModel):
    """入参 - 大盘资金流向"""
    pass


class MarketFundFlowOutput(BaseModel):
    """出参 - 大盘资金流向"""
    日期: Optional[Union[str, date]] = Field(default=None, description="日期")
    上证_收盘价: Optional[float] = Field(default=None, description="上证收盘价")
    上证_涨跌幅: Optional[float] = Field(default=None, description="上证涨跌幅(%)")
    深证_收盘价: Optional[float] = Field(default=None, description="深证收盘价")
    深证_涨跌幅: Optional[float] = Field(default=None, description="深证涨跌幅(%)")
    主力净流入_净额: Optional[float] = Field(default=None, description="主力净流入-净额(元)")
    主力净流入_净占比: Optional[float] = Field(default=None, description="主力净流入-净占比(%)")
    超大单净流入_净额: Optional[float] = Field(default=None, description="超大单净流入-净额(元)")
    超大单净流入_净占比: Optional[float] = Field(default=None, description="超大单净流入-净占比(%)")
    大单净流入_净额: Optional[float] = Field(default=None, description="大单净流入-净额(元)")
    大单净流入_净占比: Optional[float] = Field(default=None, description="大单净流入-净占比(%)")
    中单净流入_净额: Optional[float] = Field(default=None, description="中单净流入-净额(元)")
    中单净流入_净占比: Optional[float] = Field(default=None, description="中单净流入-净占比(%)")
    小单净流入_净额: Optional[float] = Field(default=None, description="小单净流入-净额(元)")
    小单净流入_净占比: Optional[float] = Field(default=None, description="小单净流入-净占比(%)")


class SectorFundFlowRankInput(BaseModel):
    """入参 - 板块资金流排名"""
    indicator: str = Field(default="今日", description="时间范围：今日/5日/10日")
    sector_type: str = Field(default="行业资金流", description="板块类型：行业资金流/概念资金流/地域资金流")


class SectorFundFlowRankOutput(BaseModel):
    """出参 - 板块资金流排名"""
    序号: Optional[int] = Field(default=None, description="序号")
    名称: Optional[str] = Field(default=None, description="板块名称")
    今日涨跌幅: Optional[float] = Field(default=None, description="今日涨跌幅(%)")
    主力净流入_净额: Optional[float] = Field(default=None, description="主力净流入-净额(元)")
    主力净流入最大股: Optional[str] = Field(default=None, description="主力净流入最大股")


class IndividualFundFlowRankInput(BaseModel):
    """入参 - 个股资金流排名"""
    indicator: str = Field(default="今日", description="时间范围：今日/3日/5日/10日")


class IndividualFundFlowRankOutput(BaseModel):
    """出参 - 个股资金流排名"""
    序号: Optional[int] = Field(default=None, description="序号")
    代码: Optional[str] = Field(default=None, description="股票代码")
    名称: Optional[str] = Field(default=None, description="股票名称")
    最新价: Optional[float] = Field(default=None, description="最新价")
    今日涨跌幅: Optional[float] = Field(default=None, description="今日涨跌幅(%)")
    今日主力净流入_净额: Optional[float] = Field(default=None, description="今日主力净流入-净额(元)")


class IndividualFundFlowInput(BaseModel):
    """入参 - 个股资金流历史"""
    stock: str = Field(description="股票代码，如 000425")
    market: str = Field(default="sz", description="市场：sh上海/sz深圳/bj北京")


class IndividualFundFlowOutput(BaseModel):
    """出参 - 个股资金流历史"""
    日期: Optional[Union[str, date]] = Field(default=None, description="日期")
    收盘价: Optional[float] = Field(default=None, description="收盘价")
    涨跌幅: Optional[float] = Field(default=None, description="涨跌幅(%)")
    主力净流入_净额: Optional[float] = Field(default=None, description="主力净流入-净额(元)")
    主力净流入_净占比: Optional[float] = Field(default=None, description="主力净流入-净占比(%)")
    超大单净流入_净额: Optional[float] = Field(default=None, description="超大单净流入-净额(元)")
    超大单净流入_净占比: Optional[float] = Field(default=None, description="超大单净流入-净占比(%)")
    大单净流入_净额: Optional[float] = Field(default=None, description="大单净流入-净额(元)")
    大单净流入_净占比: Optional[float] = Field(default=None, description="大单净流入-净占比(%)")
    中单净流入_净额: Optional[float] = Field(default=None, description="中单净流入-净额(元)")
    中单净流入_净占比: Optional[float] = Field(default=None, description="中单净流入-净占比(%)")
    小单净流入_净额: Optional[float] = Field(default=None, description="小单净流入-净额(元)")
    小单净流入_净占比: Optional[float] = Field(default=None, description="小单净流入-净占比(%)")


# ============ 接口函数 ============

def get_market_fund_flow() -> List[MarketFundFlowOutput]:
    """大盘资金流向"""
    df = ak.stock_market_fund_flow()
    records = df.to_dict(orient="records")
    return [MarketFundFlowOutput(**r) for r in records]


def get_sector_fund_flow_rank(
    indicator: str = "今日",
    sector_type: str = "行业资金流"
) -> List[SectorFundFlowRankOutput]:
    """板块资金流排名"""
    df = ak.stock_sector_fund_flow_rank(indicator=indicator, sector_type=sector_type)
    records = df.to_dict(orient="records")
    return [SectorFundFlowRankOutput(**r) for r in records]


def get_individual_fund_flow_rank(indicator: str = "今日") -> List[IndividualFundFlowRankOutput]:
    """个股资金流排名"""
    df = ak.stock_individual_fund_flow_rank(indicator=indicator)
    records = df.to_dict(orient="records")
    return [IndividualFundFlowRankOutput(**r) for r in records]


def get_individual_fund_flow(stock: str, market: str = "sz") -> List[IndividualFundFlowOutput]:
    """个股资金流向"""
    df = ak.stock_individual_fund_flow(stock=stock, market=market)
    records = df.to_dict(orient="records")
    return [IndividualFundFlowOutput(**r) for r in records]
