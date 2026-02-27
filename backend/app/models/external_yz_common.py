"""
游资常用接口外部数据模型
对应 akshare API:
- stock_zh_a_spot_em (A股实时行情)
- stock_zh_a_limit_up_em (涨停板)
- stock_zt_pool_em (涨停板池)
- stock_individual_fund_flow (个股资金流向)
- stock_sector_fund_flow_rank (板块资金流向)
- stock_lhb_detail_em (龙虎榜详情)
- stock_lhb_yytj_sina (龙虎榜游资追踪)
- stock_lh_yyb_most (龙虎榜营业部)
"""
from datetime import date, datetime
from sqlmodel import Field, SQLModel
from typing import Optional


class ExternalStockSpot(SQLModel, table=True):
    """A股实时行情 - stock_zh_a_spot_em"""
    __tablename__ = "external_stock_spot"

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, description="股票代码")
    name: str = Field(description="股票名称")
    trade_date: date = Field(index=True, description="交易日期")

    # 核心指标
    latest_price: Optional[float] = Field(default=None, description="最新价")
    change: Optional[float] = Field(default=None, description="涨跌额")
    pct_chg: Optional[float] = Field(default=None, description="涨跌幅")
    volume: Optional[float] = Field(default=None, description="成交量")
    amount: Optional[float] = Field(default=None, description="成交额")
    amplitude: Optional[float] = Field(default=None, description="振幅")
    high: Optional[float] = Field(default=None, description="最高")
    low: Optional[float] = Field(default=None, description="最低")
    open_price: Optional[float] = Field(default=None, description="今开")
    pre_close: Optional[float] = Field(default=None, description="昨收")

    # 交易指标
    volume_ratio: Optional[float] = Field(default=None, description="量比")
    turnover_rate: Optional[float] = Field(default=None, description="换手率")
    pe: Optional[float] = Field(default=None, description="市盈率")
    pb: Optional[float] = Field(default=None, description="市净率")

    # 市值
    market_cap: Optional[float] = Field(default=None, description="总市值")
    circ_market_cap: Optional[float] = Field(default=None, description="流通市值")

    # 时间戳
    update_time: Optional[datetime] = Field(default=None, description="更新时间")

    class Config:
        populate_by_name = True


class ExternalLimitUp(SQLModel, table=True):
    """涨停板 - stock_zh_a_limit_up_em"""
    __tablename__ = "external_limit_up"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True, description="交易日期")
    code: str = Field(index=True, description="股票代码")
    name: str = Field(description="股票名称")

    # 涨停信息
    close_price: Optional[float] = Field(default=None, description="收盘价")
    change_pct: Optional[float] = Field(default=None, description="涨跌幅")
    reason: Optional[str] = Field(default=None, description="涨停原因")

    # 封板数据
    seal_amount: Optional[float] = Field(default=None, description="封板金额")
    seal_ratio: Optional[float] = Field(default=None, description="封比")
    open_count: Optional[int] = Field(default=None, description="打开次数")
    first_time: Optional[str] = Field(default=None, description="首次涨停时间")
    last_time: Optional[str] = Field(default=None, description="最后涨停时间")

    # 辅助信息
    turnover_rate: Optional[float] = Field(default=None, description="换手率")
    market_cap: Optional[float] = Field(default=None, description="总市值")

    class Config:
        populate_by_name = True


class ExternalZtPool(SQLModel, table=True):
    """涨停板池 - stock_zt_pool_em"""
    __tablename__ = "external_zt_pool"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True, description="交易日期")
    code: str = Field(index=True, description="股票代码")
    name: str = Field(description="股票名称")

    close_price: Optional[float] = Field(default=None, description="收盘价")
    change_pct: Optional[float] = Field(default=None, description="涨跌幅")
    reason: Optional[str] = Field(default=None, description="涨停原因")
    first_time: Optional[str] = Field(default=None, description="首次涨停时间")

    seal_amount: Optional[float] = Field(default=None, description="封板金额")
    turnover_rate: Optional[float] = Field(default=None, description="换手率")

    class Config:
        populate_by_name = True


class ExternalIndividualFundFlow(SQLModel, table=True):
    """个股资金流向 - stock_individual_fund_flow"""
    __tablename__ = "external_individual_fund_flow"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True, description="交易日期")
    code: str = Field(index=True, description="股票代码")
    name: str = Field(description="股票名称")

    # 资金流向
    net_main: Optional[float] = Field(default=None, description="主力净流入")
    net_super: Optional[float] = Field(default=None, description="超大单净流入")
    net_big: Optional[float] = Field(default=None, description="大单净流入")
    net_mid: Optional[float] = Field(default=None, description="中单净流入")
    net_small: Optional[float] = Field(default=None, description="小单净流入")

    # 成交额
    amount_main: Optional[float] = Field(default=None, description="主力成交额")
    amount_super: Optional[float] = Field(default=None, description="超大单成交额")
    amount_big: Optional[float] = Field(default=None, description="大单成交额")
    amount_mid: Optional[float] = Field(default=None, description="中单成交额")
    amount_small: Optional[float] = Field(default=None, description="小单成交额")

    # 占比
    ratio_main: Optional[float] = Field(default=None, description="主力净流入占比")

    class Config:
        populate_by_name = True


class ExternalSectorFundFlow(SQLModel, table=True):
    """板块资金流向 - stock_sector_fund_flow_rank"""
    __tablename__ = "external_sector_fund_flow"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True, description="交易日期")
    indicator: str = Field(default="今日", description="指标(今日/5日/10日/20日)")
    sector_type: str = Field(default="行业资金流", description="板块类型")

    sector_code: Optional[str] = Field(default=None, index=True, description="板块代码")
    sector_name: str = Field(index=True, description="板块名称")

    # 资金流向
    net_inflow: Optional[float] = Field(default=None, description="主力净流入")
    net_inflow_main: Optional[float] = Field(default=None, description="主力净流入净额")

    # 成交数据
    change_pct: Optional[float] = Field(default=None, description="涨跌幅")
    turnover_rate: Optional[float] = Field(default=None, description="换手率")
    amount: Optional[float] = Field(default=None, description="成交额")

    # 排名
    rank: Optional[int] = Field(default=None, description="排名")

    class Config:
        populate_by_name = True


class ExternalLhbDetail(SQLModel, table=True):
    """龙虎榜详情 - stock_lhb_detail_em"""
    __tablename__ = "external_lhb_detail"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True, description="交易日期")
    code: str = Field(index=True, description="股票代码")
    name: str = Field(description="股票名称")

    # 榜单信息
    list_type: Optional[str] = Field(default=None, description="榜单类型")

    # 机构买卖
    buy_amount: Optional[float] = Field(default=None, description="机构买入金额")
    sell_amount: Optional[float] = Field(default=None, description="机构卖出金额")
    net_amount: Optional[float] = Field(default=None, description="净买入金额")

    # 营业部信息
    broker_name: Optional[str] = Field(default=None, description="营业部名称")
    broker_buy: Optional[float] = Field(default=None, description="营业部买入")
    broker_sell: Optional[float] = Field(default=None, description="营业部卖出")

    class Config:
        populate_by_name = True


class ExternalLhbYytj(SQLModel, table=True):
    """龙虎榜游资追踪 - stock_lhb_yytj_sina"""
    __tablename__ = "external_lhb_yytj"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True, description="交易日期")

    # 游资信息
    trader_name: Optional[str] = Field(index=True, description="游资名称")

    # 买入统计
    buy_count: Optional[int] = Field(default=None, description="买入次数")
    buy_amount: Optional[float] = Field(default=None, description="买入金额")
    buy_avg: Optional[float] = Field(default=None, description="平均买入金额")

    # 卖出统计
    sell_count: Optional[int] = Field(default=None, description="卖出次数")
    sell_amount: Optional[float] = Field(default=None, description="卖出金额")

    # 关联股票
    related_stocks: Optional[str] = Field(default=None, description="关联股票")

    class Config:
        populate_by_name = True


class ExternalLhbYyb(SQLModel, table=True):
    """龙虎榜营业部 - stock_lh_yyb_most"""
    __tablename__ = "external_lhb_yyb"

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: date = Field(index=True, description="交易日期")

    # 营业部信息
    broker_name: str = Field(index=True, description="营业部名称")

    # 上榜统计
    up_count: Optional[int] = Field(default=None, description="上榜次数")
    buy_count: Optional[int] = Field(default=None, description="买入次数")
    sell_count: Optional[int] = Field(default=None, description="卖出次数")

    # 资金统计
    buy_amount: Optional[float] = Field(default=None, description="买入金额")
    sell_amount: Optional[float] = Field(default=None, description="卖出金额")
    net_amount: Optional[float] = Field(default=None, description="净买入金额")

    # 胜率
    win_rate: Optional[float] = Field(default=None, description="胜率")

    class Config:
        populate_by_name = True
