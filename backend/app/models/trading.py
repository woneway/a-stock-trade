"""
业务数据库模型 - 交易管理系统
包含：交易计划、复盘记录、持仓、委托、成交、策略、信号、回测结果、策略迭代
"""
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List


# ==================== 交易计划 ====================

class TradingPlan(SQLModel, table=True):
    """交易计划模型 - 存储用户的股票交易计划"""
    __tablename__ = "trading_plans"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 股票信息
    stock_code: str = Field(index=True, description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")

    # 计划信息
    plan_date: date = Field(description="计划日期")
    target_price: Optional[float] = Field(default=None, description="计划买入价")
    quantity: Optional[int] = Field(default=None, description="计划数量")

    # 策略与模式
    strategy_type: str = Field(default="custom", alias="strategyType", description="策略类型")
    trade_mode: Optional[str] = Field(default=None, alias="tradeMode", description="交易模式")

    # 止盈止损
    stop_loss: Optional[float] = Field(default=None, description="止损价")
    take_profit_1: Optional[float] = Field(default=None, alias="takeProfit1", description="止盈位1")
    take_profit_2: Optional[float] = Field(default=None, alias="takeProfit2", description="止盈位2")

    # 验证条件与理由
    validation_conditions: Optional[str] = Field(default=None, alias="validationConditions", description="验证条件")
    reason: Optional[str] = Field(default=None, description="买入理由")

    # 状态与备注
    status: str = Field(default="draft", description="状态: draft/executed/abandoned/expired")
    notes: Optional[str] = Field(default=None, description="备注")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Config:
        populate_by_name = True


# ==================== 交易复盘 ====================

class TradingReview(SQLModel, table=True):
    """交易复盘模型 - 存储用户的交易复盘记录"""
    __tablename__ = "trading_reviews"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 股票信息
    stock_code: str = Field(index=True, description="股票代码")
    stock_name: Optional[str] = Field(default=None, description="股票名称")
    trade_date: date = Field(index=True, description="交易日期")

    # 复盘内容
    review_content: Optional[str] = Field(default=None, alias="reviewContent", description="复盘内容")
    summary: Optional[str] = Field(default=None, description="总结")
    mistakes: Optional[str] = Field(default=None, description="错误记录")
    lessons: Optional[str] = Field(default=None, description="经验教训")

    # 关联
    plan_id: Optional[int] = Field(default=None, alias="planId", foreign_key="trading_plans.id", description="关联计划ID")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")

    class Config:
        populate_by_name = True


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

    # 盈亏
    pnl: Optional[float] = Field(default=None, description="盈亏")
    pnl_percent: Optional[float] = Field(default=None, alias="pnlPercent", description="盈亏比例")

    # 备注
    notes: Optional[str] = Field(default=None, description="备注")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")

    class Config:
        populate_by_name = True


# ==================== 策略定义 ====================

class Strategy(SQLModel, table=True):
    """策略模型 - 存储用户的策略定义"""
    __tablename__ = "strategies"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 基本信息
    name: str = Field(unique=True, index=True, description="策略名称")
    description: Optional[str] = Field(default=None, description="策略描述")

    # 策略类型
    strategy_type: str = Field(default="custom", alias="strategyType", description="策略类型: custom/builtin")

    # 策略代码
    code: Optional[str] = Field(default=None, description="策略代码")

    # 参数定义
    params_definition: str = Field(default="[]", alias="paramsDefinition", description="参数定义JSON")

    # 状态
    is_builtin: bool = Field(default=False, alias="isBuiltin", description="是否内置")
    is_active: bool = Field(default=True, alias="isActive", description="是否启用")

    # 时间戳
    created_at: date = Field(default_factory=date.today, alias="createdAt")
    updated_at: date = Field(default_factory=date.today, alias="updatedAt")

    class Config:
        populate_by_name = True


# ==================== 策略信号 ====================

class StrategySignal(SQLModel, table=True):
    """策略信号模型 - 存储策略产生的信号"""
    __tablename__ = "strategy_signals"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联策略
    strategy_id: int = Field(foreign_key="strategies.id", index=True, alias="strategyId")

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

    # 时间
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")

    class Config:
        populate_by_name = True


# ==================== 回测结果 ====================

class BacktestResult(SQLModel, table=True):
    """回测结果模型 - 存储策略回测结果"""
    __tablename__ = "backtest_results"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联策略
    strategy_id: int = Field(foreign_key="strategies.id", index=True, alias="strategyId")

    # 回测区间
    start_date: date = Field(alias="startDate", description="回测开始日期")
    end_date: date = Field(alias="endDate", description="回测结束日期")

    # 资金
    initial_capital: float = Field(alias="initialCapital", description="初始资金")
    final_capital: float = Field(alias="finalCapital", description="最终资金")

    # 收益率指标
    total_return: float = Field(default=0, alias="totalReturn", description="总收益率")
    annual_return: float = Field(default=0, alias="annualReturn", description="年化收益率")
    sharpe_ratio: float = Field(default=0, alias="sharpeRatio", description="夏普比率")
    max_drawdown: float = Field(default=0, alias="maxDrawdown", description="最大回撤")

    # 交易统计
    win_rate: float = Field(default=0, alias="winRate", description="胜率")
    total_trades: int = Field(default=0, alias="totalTrades", description="总交易次数")
    profit_trades: int = Field(default=0, alias="profitTrades", description="盈利次数")
    loss_trades: int = Field(default=0, alias="lossTrades", description="亏损次数")
    avg_profit: float = Field(default=0, alias="avgProfit", description="平均盈利")
    avg_loss: float = Field(default=0, alias="avgLoss", description="平均亏损")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")

    class Config:
        populate_by_name = True


# ==================== 策略迭代 ====================

class StrategyIteration(SQLModel, table=True):
    """策略迭代模型 - 存储策略的历史迭代"""
    __tablename__ = "strategy_iterations"

    id: Optional[int] = Field(default=None, primary_key=True)

    # 关联策略
    strategy_id: int = Field(foreign_key="strategies.id", index=True, alias="strategyId")

    # 迭代信息
    version: int = Field(description="迭代版本")
    changes: Optional[str] = Field(default=None, description="修改内容")
    test_result: Optional[str] = Field(default=None, alias="testResult", description="测试结果")

    # 关联回测
    backtest_result_id: Optional[int] = Field(default=None, alias="backtestResultId", foreign_key="backtest_results.id")

    # 备注
    notes: Optional[str] = Field(default=None, description="备注")

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")

    class Config:
        populate_by_name = True
