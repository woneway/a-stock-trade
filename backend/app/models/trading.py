"""
业务数据库模型 - 交易相关核心模型
只保留必要的模型，避免与现有模型重复：
- Plan (daily.py): 计划和复盘模板
- BacktestStrategy (backtest_strategy.py): 回测策略

本文件只包含：持仓、委托、成交、策略信号
"""
from datetime import date, datetime
from sqlmodel import Field, SQLModel
from typing import Optional


# ==================== 持仓 ====================

class Position(SQLModel, table=True):
    """持仓模型 - 存储用户的当前持仓"""
    __tablename__ = "positions"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 股票信息
    stock_code: str = Field(index=True, description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")

    # 数量与价格
    quantity: int = Field(default=0, description="持仓数量")
    available_quantity: int = Field(default=0, alias="availableQuantity", description="可用数量")
    cost_price: float = Field(default=0, alias="costPrice", description="成本价")
    current_price: float = Field(default=0, alias="currentPrice", description="当前价")

    # 计算字段
    market_value: float = Field(default=0, alias="marketValue", description="市值")
    profit_amount: float = Field(default=0, alias="profitAmount", description="盈亏金额")
    profit_ratio: float = Field(default=0, alias="profitRatio", description="盈亏比例")

    # 止盈止损
    stop_loss: Optional[float] = Field(default=None, alias="stopLoss", description="止损价")
    take_profit: Optional[float] = Field(default=None, alias="takeProfit", description="止盈价")

    # 状态
    status: str = Field(default="holding", description="状态: holding/sold/stopped")

    # 开仓日期
    opened_at: date = Field(alias="openedAt", description="开仓日期")

    # 关联计划（可选，关联 daily.Plan）
    plan_id: Optional[int] = Field(default=None, description="关联计划ID")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Config:
        populate_by_name = True


# ==================== 委托 ====================

class Order(SQLModel, table=True):
    """委托模型 - 存储用户的委托单"""
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 股票信息
    stock_code: str = Field(index=True, description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")

    # 委托信息
    order_price: float = Field(alias="orderPrice", description="委托价格")
    quantity: int = Field(description="委托数量")
    direction: str = Field(default="buy", description="方向: buy/sell")
    order_type: str = Field(default="limit", alias="orderType", description="委托类型: limit/market")

    # 状态
    status: str = Field(default="pending", description="状态: pending/filled/cancelled/rejected/partial")

    # 时间
    order_time: Optional[datetime] = Field(default=None, alias="orderTime", description="委托时间")

    # 成交信息
    filled_quantity: int = Field(default=0, alias="filledQuantity", description="成交数量")
    filled_price: Optional[float] = Field(default=None, alias="filledPrice", description="成交价")

    # 关联
    plan_id: Optional[int] = Field(default=None, description="关联计划ID")
    position_id: Optional[int] = Field(default=None, alias="positionId", foreign_key="positions.id", description="关联持仓ID")

    # 备注
    notes: Optional[str] = Field(default=None, description="备注")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Config:
        populate_by_name = True


# ==================== 成交记录 ====================

class Trade(SQLModel, table=True):
    """成交记录模型 - 存储用户的成交流水"""
    __tablename__ = "trades"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 股票信息
    stock_code: str = Field(index=True, description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")

    # 交易信息
    trade_type: str = Field(alias="tradeType", description="交易类型: buy/sell")
    price: float = Field(description="成交价")
    quantity: int = Field(description="成交数量")
    amount: float = Field(description="成交金额")
    fee: float = Field(default=0, description="手续费")

    # 时间
    trade_date: date = Field(index=True, alias="tradeDate", description="交易日期")
    trade_time: Optional[datetime] = Field(default=None, alias="tradeTime", description="成交时间")

    # 关联
    order_id: Optional[int] = Field(default=None, alias="orderId", foreign_key="orders.id", description="关联委托ID")
    position_id: Optional[int] = Field(default=None, alias="positionId", foreign_key="positions.id", description="关联持仓ID")
    plan_id: Optional[int] = Field(default=None, description="关联计划ID")

    # 盈亏
    pnl: Optional[float] = Field(default=None, description="盈亏")
    pnl_percent: Optional[float] = Field(default=None, alias="pnlPercent", description="盈亏比例")

    # 备注
    notes: Optional[str] = Field(default=None, description="备注")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")

    class Config:
        populate_by_name = True


# ==================== 策略信号 ====================

class StrategySignal(SQLModel, table=True):
    """策略信号模型 - 存储策略产生的信号"""
    __tablename__ = "strategy_signals"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联策略（使用 backtest_strategy 表）
    strategy_id: int = Field(foreign_key="backtest_strategies.id", index=True, alias="strategyId")

    # 股票信息
    stock_code: str = Field(index=True, alias="stockCode", description="股票代码")
    stock_name: Optional[str] = Field(default=None, alias="stockName", description="股票名称")

    # 信号信息
    signal_type: str = Field(alias="signalType", description="信号类型: buy/sell/hold")
    signal_strength: float = Field(default=0, alias="signalStrength", description="信号强度")
    confidence: float = Field(default=0, description="置信度")

    # 价格
    target_price: Optional[float] = Field(default=None, alias="targetPrice", description="目标价")
    stop_loss: Optional[float] = Field(default=None, alias="stopLoss", description="止损价")

    # 原因
    reason: Optional[str] = Field(default=None, description="信号原因")

    # 关联计划
    plan_id: Optional[int] = Field(default=None, description="关联计划ID")

    # 时间
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")

    class Config:
        populate_by_name = True
