# AI化游资交易系统完整设计

> A股智能交易信号系统 - AI化版本

---

## 一、系统架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              系统整体架构                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端层 (Frontend)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Dashboard  │  │  复盘中心   │  │  计划中心   │  │  监控中心   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  持仓管理   │  │  交易记录   │  │  AI审批    │  │  设置中心   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↑
                                  HTTP/WebSocket
                                      ↑
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API层 (FastAPI)                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Dashboard  │  │  复盘API    │  │  计划API    │  │  监控API    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  持仓API    │  │  交易API    │  │  AI API     │  │  设置API    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↑
┌─────────────────────────────────────────────────────────────────────────────┐
│                             服务层 (Services)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ 数据采集    │  │ 计划管理    │  │ 持仓管理    │  │ 交易记录    │   │
│  │ Service    │  │ Service    │  │ Service    │  │ Service    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ 监控服务    │  │ 复盘服务    │  │ 通知服务    │  │ 学习服务    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↑
┌─────────────────────────────────────────────────────────────────────────────┐
│                             AI层 (AI Agents)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ 市场分析    │  │ 计划生成    │  │ 执行控制    │  │ 学习优化    │   │
│  │ Agent      │  │ Agent      │  │ Agent      │  │ Agent      │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↑
┌─────────────────────────────────────────────────────────────────────────────┐
│                             数据层 (Data)                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ SQLite     │  │ 行情数据    │  │ 配置数据    │  │ 缓存数据    │   │
│  │ (主数据库)  │  │ (外部API)   │  │ (JSON文件)  │  │ (Redis)    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、数据模型设计

### 2.1 现有模型（保持不变）

```python
# 现有模型 - 位置: app/models/models.py

class TradingPlan(Base):
    """交易计划"""
    id = Column(Integer, primary_key=True)
    stock_code = Column(String(10))      # 股票代码
    stock_name = Column(String(50))      # 股票名称
    stock_type = Column(String(20))      # 股票类型
    trade_mode = Column(String(20))      # 交易模式: low_buy/breakthrough/limit_up
    buy_timing = Column(String(50))      # 买入时机
    validation_conditions = Column(JSON) # 验证条件
    target_price = Column(Float)         # 目标价
    position_ratio = Column(Float)       # 仓位比例
    stop_loss_price = Column(Float)      # 止损价
    stop_loss_ratio = Column(Float)      # 止损比例
    take_profit_price = Column(Float)   # 止盈价
    take_profit_ratio = Column(Float)   # 止盈比例
    hold_period = Column(String(20))     # 持仓周期
    logic = Column(Text)                 # 买入逻辑
    status = Column(String(20))          # 状态: observing/pending/approved/executing/completed/cancelled
    execute_result = Column(String(50))  # 执行结果
    plan_date = Column(Date)            # 计划日期
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Position(Base):
    """持仓"""
    id = Column(Integer, primary_key=True)
    stock_code = Column(String(10))
    stock_name = Column(String(50))
    quantity = Column(Integer)
    available_quantity = Column(Integer)
    cost_price = Column(Float)
    current_price = Column(Float)
    profit_amount = Column(Float)
    profit_ratio = Column(Float)
    stop_loss_price = Column(Float)
    take_profit_price = Column(Float)
    plan_id = Column(Integer, ForeignKey("trading_plans.id"))
    status = Column(String(20))
    opened_at = Column(Date)

class Trade(Base):
    """交易记录"""
    id = Column(Integer, primary_key=True)
    stock_code = Column(String(10))
    stock_name = Column(String(50))
    trade_type = Column(String(10))     # buy/sell
    quantity = Column(Integer)
    price = Column(Float)
    amount = Column(Float)
    fee = Column(Float)
    position_id = Column(Integer, ForeignKey("positions.id"))
    plan_id = Column(Integer, ForeignKey("trading_plans.id"))
    trade_date = Column(Date)
    trade_time = Column(String(10))
    notes = Column(Text)

class Account(Base):
    """账户"""
    id = Column(Integer, primary_key=True)
    total_assets = Column(Float)
    available_cash = Column(Float)
    market_value = Column(Float)
    today_profit = Column(Float)
    today_profit_ratio = Column(Float)
    total_profit = Column(Float)
    total_profit_ratio = Column(Float)
```

### 2.2 新增AI模型

```python
# 新增AI模型 - 位置: app/models/ai_models.py

class AIStrategyConfig(Base):
    """AI策略配置"""
    __tablename__ = "ai_strategy_config"

    id = Column(Integer, primary_key=True)

    # 风格配置
    strategy_name = Column(String(50))                    # 策略名称: 激进/稳健/保守
    risk_preference = Column(String(20))                 # aggressive/moderate/conservative
    trade_mode_preference = Column(String(200))         # low_buy,breakthrough,limit_up,any

    # 仓位配置
    max_position_per_trade = Column(Float, default=20)  # 单笔最大仓位%
    max_total_position = Column(Float, default=70)       # 总仓位上限%
    min_cash_reserve = Column(Float, default=30)        # 最小现金储备%

    # 执行权限
    auto_buy_enabled = Column(Boolean, default=False)    # 自动买入
    auto_sell_enabled = Column(Boolean, default=False)   # 自动卖出
    confirm_before_trade = Column(Boolean, default=True) # 交易前确认
    auto_stop_loss = Column(Boolean, default=True)       # 自动止损
    auto_take_profit = Column(Boolean, default=True)     # 自动止盈
    time_stop_enabled = Column(Boolean, default=True)    # 时间止损

    # 止损配置
    default_stop_loss = Column(Float, default=-5)        # 默认止损比例%
    time_stop_minutes = Column(Integer, default=30)      # 时间止损分钟数
    max_daily_loss = Column(Float, default=-5)          # 日最大亏损%
    max_weekly_loss = Column(Float, default=-10)         # 周最大亏损%

    # 止盈配置
    take_profit_1 = Column(Float, default=7)             # 第一止盈点%
    take_profit_2 = Column(Float, default=15)           # 第二止盈点%
    trailing_stop_enabled = Column(Boolean, default=True)# 移动止损
    trailing_stop_trigger = Column(Float, default=5)     # 移动止损触发盈利%
    trailing_stop_distance = Column(Float, default=3)   # 移动止损距离%

    # 学习配置
    learning_enabled = Column(Boolean, default=True)     # 启用学习
    min_samples_to_learn = Column(Integer, default=20)   # 最少样本数

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AIMarketAnalysis(Base):
    """AI市场分析"""
    __tablename__ = "ai_market_analysis"

    id = Column(Integer, primary_key=True)
    analysis_date = Column(Date)

    # 基础指标
    total_limit_up = Column(Integer)                     # 涨停家数
    total_limit_down = Column(Integer)                  # 跌停家数
    limit_up_ratio = Column(Float)                     # 涨停溢价率%
    broken_plate_ratio = Column(Float)                  # 炸板率%
    continuous_board_count = Column(Integer)            # 连板家数
    highest_board = Column(Integer)                    # 最高连板数
    red_line_count = Column(Integer)                   # 红盘家数

    # AI判断
    market_sentiment = Column(String(20))               # bullish/bearish/neutral
    market_cycle = Column(String(20))                  # ice_point/start/ferment/peak/decline/chaos
    risk_level = Column(Float)                         # 0-1
    opportunity_score = Column(Float)                  # 0-1
    recommendation = Column(String(20))                # heavy/medium/light/empty
    win_probability = Column(Float)                   # 赢面 0-1

    # 板块分析
    hot_sectors = Column(JSON)                         # ["AI", "新能源"]
    emerging_sectors = Column(JSON)                   # 新兴板块
    declining_sectors = Column(JSON)                  # 衰退板块

    # 详细分析
    reasoning = Column(Text)                           # 分析理由
    key_signals = Column(JSON)                        # 关键信号
    created_at = Column(DateTime, default=datetime.now)


class AIStockSelection(Base):
    """AI选股结果"""
    __tablename__ = "ai_stock_selection"

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("ai_market_analysis.id"))

    # 股票信息
    stock_code = Column(String(10))
    stock_name = Column(String(50))
    sector = Column(String(50))                      # 所属板块

    # 选股理由
    selection_type = Column(String(20))               # 龙头/补涨/首板/反包
    selection_reason = Column(Text)
    selection_score = Column(Float)                   # 选股评分 0-1

    # 推荐交易
    recommended_mode = Column(String(20))             # 推荐交易模式
    recommended_price = Column(Float)                 # 推荐价格
    confidence = Column(Float)                        # 信心指数 0-1

    # 状态
    status = Column(String(20))                       # pending/approved/rejected/used
    created_at = Column(DateTime, default=datetime.now)


class AITradePlan(Base):
    """AI生成的交易计划"""
    __tablename__ = "ai_trade_plans"

    id = Column(Integer, primary_key=True)
    plan_date = Column(Date)

    # 股票信息
    stock_code = Column(String(10))
    stock_name = Column(String(50))
    sector = Column(String(50))

    # 交易配置
    trade_mode = Column(String(20))                   # 买入模式
    target_price = Column(Float)                     # 目标价
    position_ratio = Column(Float)                    # 仓位比例%
    stop_loss_price = Column(Float)                  # 止损价
    stop_loss_ratio = Column(Float)                  # 止损比例%
    take_profit_price_1 = Column(Float)             # 第一止盈价
    take_profit_ratio_1 = Column(Float)              # 第一止盈比例%
    take_profit_price_2 = Column(Float)             # 第二止盈价
    take_profit_ratio_2 = Column(Float)              # 第二止盈比例%

    # 验证条件
    validation_conditions = Column(JSON)             # {open_pct, volume, sector}

    # 时间配置
    valid_time_start = Column(String(10))            # 有效时段开始
    valid_time_end = Column(String(10))              # 有效时段结束

    # AI判断
    ai_confidence = Column(Float)                    # AI信心指数
    ai_reasoning = Column(Text)                      # AI决策理由
    risk_warning = Column(String(200))               # 风险提示

    # 审批状态
    approval_status = Column(String(20))              # pending/approved/rejected/modified
    approval_comment = Column(Text)                  # 审批意见
    approved_at = Column(DateTime)                   # 审批时间
    approved_by = Column(String(20))                 # 审批人: ai/user

    # 执行状态
    execution_status = Column(String(20))            # waiting/triggered/executed/cancelled/expired
    triggered_at = Column(DateTime)                  # 触发时间
    executed_at = Column(DateTime)                   # 执行时间

    # 关联
    source_selection_id = Column(Integer)             # 来源选股ID

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AIExecutionLog(Base):
    """AI执行日志"""
    __tablename__ = "ai_execution_log"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("ai_trade_plans.id"))

    # 触发信息
    trigger_type = Column(String(50))                 # price_reach/condition_met/time_stop/stop_loss/take_profit
    trigger_price = Column(Float)                    # 触发价格
    trigger_time = Column(DateTime)                  # 触发时间
    trigger_data = Column(JSON)                      # 触发时市场数据

    # 决策信息
    decision = Column(String(20))                    # execute/wait/skip/cancel
    decision_reason = Column(Text)

    # 执行结果
    result = Column(String(20))                      # success/failed/cancelled/expired
    error_message = Column(Text)
    trade_id = Column(Integer, ForeignKey("trades.id"))

    created_at = Column(DateTime, default=datetime.now)


class AILearning(Base):
    """AI学习记录"""
    __tablename__ = "ai_learning"

    id = Column(Integer, primary_key=True)

    # 学习周期
    learn_date = Column(Date)

    # 绩效统计
    total_trades = Column(Integer)                    # 总交易次数
    winning_trades = Column(Integer)                  # 盈利次数
    win_rate = Column(Float)                         # 胜率
    total_profit = Column(Float)                     # 总盈利%
    profit_loss_ratio = Column(Float)                # 盈亏比
    plan_completion_rate = Column(Float)             # 计划完成率

    # 模式分析
    mode_stats = Column(JSON)                         # {low_buy: {win_rate, avg_profit}, ...}
    sector_stats = Column(JSON)                      # 板块胜率统计
    timing_stats = Column(JSON)                       # 时段胜率统计

    # 学习洞察
    insights = Column(JSON)                          # 学习发现
    recommendations = Column(Text)                   # 优化建议
    adjustments = Column(JSON)                       # 策略调整

    created_at = Column(DateTime, default=datetime.now)


class AIReminder(Base):
    """AI提醒记录"""
    __tablename__ = "ai_reminders"

    id = Column(Integer, primary_key=True)

    # 提醒类型
    reminder_type = Column(String(50))                # price_alert/stop_loss/take_profit/approval/time_stop

    # 关联
    plan_id = Column(Integer, ForeignKey("ai_trade_plans.id"))
    position_id = Column(Integer, ForeignKey("positions.id"))

    # 内容
    title = Column(String(100))
    message = Column(Text)
    priority = Column(String(20))                    # low/medium/high/urgent

    # 状态
    status = Column(String(20))                      # pending/sent/clicked/dismissed
    sent_at = Column(DateTime)
    clicked_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.now)
```

---

## 三、API接口设计

### 3.1 AI市场分析API

```yaml
# API: /api/v1/ai/analyze-market
# 方法: POST
# 说明: AI分析当前市场状态

Request:
{}

Response:
{
    "success": true,
    "data": {
        "analysis_id": 1,
        "analysis_date": "2026-02-25",
        "metrics": {
            "total_limit_up": 45,
            "total_limit_down": 8,
            "limit_up_ratio": 85.5,
            "broken_plate_ratio": 22.3,
            "continuous_board_count": 18,
            "highest_board": 7,
            "red_line_count": 2850
        },
        "market_sentiment": "bullish",
        "market_cycle": "ferment",
        "risk_level": 0.4,
        "opportunity_score": 0.75,
        "recommendation": "medium",
        "win_probability": 0.72,
        "hot_sectors": ["AI", "半导体", "新能源车"],
        "emerging_sectors": ["人形机器人"],
        "declining_sectors": ["房地产"],
        "reasoning": "涨停45家，炸板率22%，连板18家，市场情绪良好，处于发酵期",
        "key_signals": [
            {"type": "limit_up_count", "value": 45, "status": "positive"},
            {"type": "broken_plate_ratio", "value": 22.3, "status": "neutral"},
            {"type": "highest_board", "value": 7, "status": "positive"}
        ]
    }
}
```

### 3.2 AI选股API

```yaml
# API: /api/v1/ai/select-stocks
# 方法: POST
# 说明: 基于市场分析结果进行AI选股

Request:
{
    "analysis_id": 1,                    # 可选，使用指定分析结果
    "max_count": 10,                     # 最多选股数量
    "sectors": ["AI", "半导体"],        # 可选，限定板块
    "exclude_stocks": ["600519"]         # 可选，排除股票
}

Response:
{
    "success": true,
    "data": {
        "selections": [
            {
                "id": 1,
                "stock_code": "300750",
                "stock_name": "宁德时代",
                "sector": "新能源车",
                "selection_type": "龙头",
                "selection_reason": "板块涨停最多，早盘封板，资金净流入最大",
                "selection_score": 0.92,
                "recommended_mode": "breakthrough",
                "recommended_price": 185.5,
                "confidence": 0.85
            }
        ]
    }
}
```

### 3.3 AI生成交易计划API

```yaml
# API: /api/v1/ai/generate-plans
# 方法: POST
# 说明: AI生成交易计划

Request:
{
    "plan_date": "2026-02-26",           # 计划日期
    "selections": [1, 2, 3],             # 选股ID列表
    "max_plans": 5,                      # 最多计划数
    "total_capital": 100000,             # 总资金
    "strategy_id": 1                      # 策略配置ID
}

Response:
{
    "success": true,
    "data": {
        "plans": [
            {
                "id": 1,
                "stock_code": "300750",
                "stock_name": "宁德时代",
                "trade_mode": "breakthrough",
                "target_price": 185.5,
                "position_ratio": 15.0,
                "stop_loss_price": 172.5,
                "stop_loss_ratio": -7.0,
                "take_profit_price_1": 198.5,
                "take_profit_ratio_1": 7.0,
                "take_profit_price_2": 213.3,
                "take_profit_ratio_2": 15.0,
                "validation_conditions": {
                    "open_pct": "<5%",
                    "volume": ">5亿",
                    "sector_up": true
                },
                "valid_time_start": "09:30",
                "valid_time_end": "10:30",
                "ai_confidence": 0.85,
                "ai_reasoning": "新能源车板块持续发酵，龙头股回调企稳，符合半路买入条件",
                "risk_warning": "市场处于发酵期，仓位建议控制在50%以内",
                "approval_status": "pending"
            }
        ],
        "summary": {
            "total_plans": 3,
            "total_position": 45.0,
            "risk_level": "medium"
        }
    }
}
```

### 3.4 AI计划审批API

```yaml
# API: /api/v1/ai/approve-plan
# 方法: POST
# 说明: 审批AI生成的交易计划

Request:
{
    "plan_id": 1,
    "action": "approve",                 # approve/reject/modify
    "comment": "同意执行",               # 审批意见
    "modifications": {                   # 如果是modify，修改内容
        "position_ratio": 20.0,
        "target_price": 186.0
    }
}

Response:
{
    "success": true,
    "data": {
        "plan_id": 1,
        "approval_status": "approved",
        "approved_at": "2026-02-25T09:20:00",
        "approved_by": "user"
    }
}

# API: /api/v1/ai/pending-approvals
# 方法: GET
# 说明: 获取待审批计划列表

Response:
{
    "success": true,
    "data": {
        "pending_count": 3,
        "plans": [
            {
                "id": 1,
                "stock_code": "300750",
                "stock_name": "宁德时代",
                "trade_mode": "breakthrough",
                "target_price": 185.5,
                "position_ratio": 15.0,
                "ai_confidence": 0.85,
                "ai_reasoning": "...",
                "created_at": "2026-02-25T09:15:00"
            }
        ]
    }
}
```

### 3.5 AI执行监控API

```yaml
# API: /api/v1/ai/monitor
# 方法: GET
# 说明: 获取当前AI监控状态

Response:
{
    "success": true,
    "data": {
        "active_plans": [
            {
                "id": 1,
                "stock_code": "300750",
                "stock_name": "宁德时代",
                "current_price": 184.2,
                "target_price": 185.5,
                "distance_pct": 0.7,
                "status": "waiting",
                "valid_until": "10:30:00"
            }
        ],
        "positions_monitored": [
            {
                "id": 1,
                "stock_code": "300750",
                "current_price": 190.5,
                "cost_price": 185.0,
                "profit_pct": 2.97,
                "stop_loss_price": 172.5,
                "take_profit_price_1": 198.5,
                "alert_level": "normal"
            }
        ]
    }
}

# API: /api/v1/ai/execute
# 方法: POST
# 说明: 手动触发执行或确认执行

Request:
{
    "plan_id": 1,
    "action": "execute",                  # execute/cancel/skip
    "price": 185.8,                      # 实际成交价格
    "quantity": 1000                     # 成交数量
}

Response:
{
    "success": true,
    "data": {
        "trade_id": 1,
        "execution_status": "executed",
        "executed_at": "2026-02-25T10:15:30"
    }
}
```

### 3.6 AI绩效与学习API

```yaml
# API: /api/v1/ai/performance
# 方法: GET
# 说明: 获取AI绩效报告

Query:
    start_date: 2026-01-01
    end_date: 2026-02-25
    mode: daily/weekly/monthly

Response:
{
    "success": true,
    "data": {
        "summary": {
            "total_trades": 45,
            "winning_trades": 27,
            "win_rate": 0.60,
            "total_profit_pct": 15.8,
            "profit_loss_ratio": 1.85,
            "plan_completion_rate": 0.72
        },
        "mode_performance": {
            "low_buy": {"win_rate": 0.68, "avg_profit": 5.2},
            "breakthrough": {"win_rate": 0.55, "avg_profit": 4.1},
            "limit_up": {"win_rate": 0.45, "avg_profit": 8.5}
        },
        "daily_stats": [
            {"date": "2026-02-25", "trades": 3, "profit_pct": 2.1}
        ]
    }
}

# API: /api/v1/ai/learning-insights
# 方法: GET
# 说明: 获取AI学习洞察

Response:
{
    "success": true,
    "data": {
        "insights": [
            {
                "type": "mode_advantage",
                "description": "低吸模式胜率68%，高于打板模式15%",
                "recommendation": "建议增加低吸模式权重"
            },
            {
                "type": "timing_pattern",
                "description": "上午10:00-10:30买入的股票胜率最高",
                "recommendation": "建议将买入时段集中在此时间段"
            }
        ],
        "strategy_adjustments": {
            "trade_mode_preference": ["low_buy", "breakthrough"],
            "max_position_per_trade": 18,
            "default_stop_loss": -6
        }
    }
}
```

### 3.7 AI策略配置API

```yaml
# API: /api/v1/ai/strategy-config
# 方法: GET/POST/PUT
# 说明: AI策略配置管理

# GET 获取配置
Response:
{
    "success": true,
    "data": {
        "id": 1,
        "strategy_name": "稳健型",
        "risk_preference": "moderate",
        "trade_mode_preference": ["low_buy", "breakthrough"],
        "max_position_per_trade": 20,
        "max_total_position": 60,
        "auto_buy_enabled": false,
        "auto_sell_enabled": true,
        "confirm_before_trade": true,
        "auto_stop_loss": true,
        "default_stop_loss": -5,
        "time_stop_minutes": 30,
        "take_profit_1": 7,
        "take_profit_2": 15,
        "trailing_stop_enabled": true
    }
}

# POST 创建配置
Request:
{
    "strategy_name": "激进型",
    "risk_preference": "aggressive",
    "trade_mode_preference": ["limit_up", "breakthrough"],
    "max_position_per_trade": 30,
    "max_total_position": 80,
    "auto_buy_enabled": true,
    "auto_sell_enabled": true,
    "confirm_before_trade": false
}
```

---

## 四、前端页面设计

### 4.1 页面结构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              前端页面结构                                   │
└─────────────────────────────────────────────────────────────────────────────┘

pages/
├── Dashboard.vue              # 首页/Dashboard
├── Review/                    # 复盘中心
│   ├── Index.vue             # 复盘主页
│   ├── MarketAnalysis.vue    # AI市场分析
│   └── StockSelection.vue    # AI选股结果
├── Plans/                    # 计划中心
│   ├── Index.vue             # 计划列表
│   ├── AIGenerate.vue        # AI生成计划
│   └── Approval.vue          # 计划审批
├── Monitor/                  # 监控中心
│   ├── Index.vue             # 监控主页
│   ├── RealTime.vue          # 实时监控
│   └── Alerts.vue            # 提醒记录
├── Positions/                # 持仓管理
│   └── Index.vue             # 持仓列表
├── Trades/                   # 交易记录
│   └── Index.vue             # 交易记录
├── AI/                       # AI中心
│   ├── Performance.vue        # AI绩效
│   ├── Learning.vue          # AI学习
│   └── Settings.vue          # AI设置
└── Settings/                 # 设置中心
    └── Index.vue             # 系统设置
```

### 4.2 核心页面设计

#### 4.2.1 首页 (Dashboard)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Dashboard 设计                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  今日概览                                            2026年2月25日 周二   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │   总资产     │ │   今日盈亏   │ │   待审批     │ │   监控中     │    │
│  │  ¥128,500   │ │  +2.35%     │ │     3笔     │ │     5笔     │    │
│  │   ↑5.2%     │ │   ¥+2,850   │ │   ⚠️待处理   │ │   🔔活跃    │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  AI市场状态                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │  🟢 市场情绪: 乐观    📈 机会评分: 75%    ⚠️ 风险等级: 40%        │  │
│  │  🔄 周期阶段: 发酵期    💰 推荐仓位: 5-7成                          │  │
│  │  🔥 热门板块: AI、半导体、新能源车                                    │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│  快捷操作                                                                  │
│  [🤖 AI分析] [📋 今日计划] [👀 监控中] [📊 绩效]                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  最近交易                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ 时间    股票       方向  价格     数量    状态                     │  │
│  │ 10:15  宁德时代   买入  185.50  1000    ✅ 已执行                 │  │
│  │ 10:28  贵州茅台   卖出  1720.0  500     ✅ 止盈1                 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.2.2 AI市场分析页面

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI市场分析页面设计                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  🤖 AI市场分析                                            [立即分析] 🔄   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        核心指标卡片                                  │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │   │
│  │  │ 涨停 45  │ │ 跌停 8   │ │ 炸板率22%│ │ 最高7板  │            │   │
│  │  │   ↑      │ │   ↓      │ │   ↓      │ │   ↑      │            │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────┐  ┌──────────────────────────────────────┐   │
│  │    情绪周期判断           │  │    仓位建议                         │   │
│  │  ┌────────────────────┐  │  │  ┌────────────────────────────────┐ │   │
│  │  │                    │  │  │  │     ●●●●●○○○○○              │ │   │
│  │  │    🔄 发酵期       │  │  │  │      推荐仓位: 50-70%          │ │   │
│  │  │                    │  │  │  │      赢面: 72%                │ │   │
│  │  │  赚钱效应良好     │  │  │  └────────────────────────────────┘ │   │
│  │  │  可重仓参与       │  │  │                                    │   │
│  │  └────────────────────┘  │  │  轻仓 ●●○○○○○○○○○  10-20%    │   │
│  └──────────────────────────┘  │  半仓 ●●●●○○○○○○○  30-50%    │   │
│                                │  重仓 ●●●●●●○○○○○  50-70%    │   │
│                                │  满仓 ●●●●●●●●●●●  80-100%   │   │
│                                └──────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │    热门板块                                                             │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │   │
│  │  │  🔥 AI   │ │半导体   │ │新能源车 │ │ 机器人  │ │   ...   │     │   │
│  │  │  涨停12 │ │  涨停8  │ │  涨停6  │ │  涨停4  │ │         │     │   │
│  │  │  ↑+2天  │ │  ↑+1天  │ │  →平    │ │  ↑+1天  │ │         │     │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [🤖 基于分析选股]                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.2.3 AI计划审批页面

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI计划审批页面设计                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  📋 今日AI交易计划                              共3笔  |  总仓位: 45%     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [600519] 贵州茅台                                      ⭐⭐⭐⭐☆ 0.75 │   │
│  │  模式: 低吸  |  目标价: 1680  |  仓位: 15%                         │   │
│  │  止损: 1562 (-7%)  |  止盈1: 1764 (+5%)  |  止盈2: 1848 (+10%)   │   │
│  │  验证条件: 高开<3% AND 成交量>1.5亿                              │   │
│  │  有效时段: 09:30 - 10:30                                          │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │  💡 AI理由: 龙头回调企稳，量能配合，支撑位明显                    │   │
│  │  ⚠️ 风险提示: 市场处于发酵期，注意板块持续性                     │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │  [✅ 批准] [❌ 拒绝] [📝 修改] [⏰ 延后]                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [300750] 宁德时代                                      ⭐⭐⭐⭐⭐ 0.88 │   │
│  │  模式: 半路  |  目标价: 185.5  |  仓位: 20%                        │   │
│  │  止损: 172.5 (-7%)  |  止盈1: 198.5 (+7%)  |  止盈2: 213.3 (+15%) │   │
│  │  验证条件: 涨幅<5% AND 成交量>5亿                                │   │
│  │  有效时段: 09:30 - 10:30                                          │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │  💡 AI理由: 新能源车板块持续发酵，龙头股回调企稳                   │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │  [✅ 批准] [❌ 拒绝] [📝 修改] [⏰ 延后]                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  [688981] 中芯国际                                      ⭐⭐⭐☆☆ 0.55 │   │
│  │  模式: 打板  |  目标价: 52.0  |  仓位: 10%                         │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │  ⚠️ 信心指数较低，建议谨慎考虑                                      │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │  [✅ 批准] [❌ 拒绝] [📝 修改] [⏰ 延后]                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [🤖 一键批准全部]  [⏸️ 全部延后]                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.2.4 实时监控页面

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           实时监控页面设计                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  👀 实时监控                                              [筛选: 全部 ▼]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  待执行计划                                                          │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │ [300750] 宁德时代                        目标: 185.5 当前: 185.2│ │   │
│  │  │ ████████████░░░░░░░░░░░░  98%  距目标-0.7%                   │ │   │
│  │  │ 验证条件: ✓ 涨幅3.2%  ✓ 成交量5.2亿  有效时段: 09:30-10:30   │ │   │
│  │  │ ─────────────────────────────────────────────────────────────   │ │   │
│  │  │ [⚡ 立即执行] [⏰ 稍后提醒] [❌ 放弃]                          │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  持仓监控 (5)                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │ [600519] 贵州茅台 成本:1850 当前:1905  盈利: +2.97%           │ │   │
│  │  │ 止损: 1722  止盈1: 1985  止盈2: 2135                          │ │   │
│  │  │ ████████████████████████████████████  移动止损触发!            │ │   │
│  │  │ [⚠️ 触及移动止损] [💰 部分止盈] [📌 继续持有]                 │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │ [300750] 宁德时代 成本:185.5 当前:184.0  盈利: -0.81%        │ │   │
│  │  │ 止损: 172.5  🔴 距止损-0.69%                                  │ │   │
│  │  │ [⚠️ 接近止损] [💰 手动卖出] [📌 继续持有]                      │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  今日提醒 (12)     [全部已读]                                       │   │
│  │  ┌────────────────────────────────────────────────────────────────┐ │   │
│  │  │ 🔔 10:15  [300750]宁德时代 价格触及目标价185.5                │ │   │
│  │  │ 🔔 10:28  [600519]贵州茅台 盈利达到+5%，可考虑止盈             │ │   │
│  │  │ ⚠️ 10:35  [300750]宁德时代 亏损-3%，接近止损线                │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.2.5 AI绩效页面

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            AI绩效页面设计                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  📊 AI绩效报告                              时间: 2026-01-01 ~ 2026-02-25 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │   总交易     │ │    胜率      │ │   盈亏比     │ │  计划完成率  │    │
│  │     45笔     │ │    60%      │ │    1.85     │ │    72%      │    │
│  │              │ │   🟢 +5%    │ │   🟢 +0.3   │ │   🟢 +12%   │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │  总收益率    │ │  月均收益    │ │  最大回撤   │ │  胜率最高   │    │
│  │   +15.8%    │ │   +7.9%     │ │   -8.2%     │ │   低吸68%   │    │
│  │   🟢 超预期  │ │   🟢 正常   │ │   🟢 低于   │ │   模式      │    │
│  │              │ │              │ │   阈值10%   │ │              │    │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  模式胜率对比                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  低吸    ████████████████████░░░░░░░░  68%  ⭐最高                   │   │
│  │  半路    ██████████████████░░░░░░░░░░  55%                         │   │
│  │  打板    ██████████████░░░░░░░░░░░░░░  45%  ⭐建议减少            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  📈 学习洞察与建议                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  💡 发现1: 低吸模式胜率68%，建议增加低吸权重                        │   │
│  │  💡 发现2: 上午10:00-10:30买入胜率最高                             │   │
│  │  💡 发现3: AI板块交易胜率高于平均15%                                │   │
│  │  ─────────────────────────────────────────────────────────────     │   │
│  │  ⚡ 建议: 调整策略配置                                              │   │
│  │     • 交易模式偏好: [低吸 ✓] [半路 ✓] [打板 ✗]                    │   │
│  │     • 单笔仓位上限: 20% → 18%                                      │   │
│  │     • 默认止损: -5% → -6%                                          │   │
│  │     [💾 应用建议]                                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 五、核心模块设计

### 5.1 市场分析模块 (MarketAnalysisAgent)

```python
# 模块职责：分析市场情绪、判断周期、输出仓位建议

class MarketAnalysisAgent:
    """市场分析Agent"""

    async def analyze(self, date: date) -> AIMarketAnalysis:
        """
        执行市场分析
        1. 获取市场基础数据
        2. 计算各项指标
        3. 判断情绪周期
        4. 输出仓位建议
        """

    def _fetch_market_data(self) -> MarketData:
        """获取市场数据"""

    def _calculate_indicators(self, data: MarketData) -> Indicators:
        """计算情绪指标"""

    def _judge_cycle(self, indicators: Indicators) -> CycleResult:
        """判断情绪周期"""

    def _recommend_position(self, cycle: str, indicators: Indicators) -> PositionRecommendation:
        """仓位推荐"""

# 核心判断规则
CYCLE_RULES = {
    "ice_point": {  # 冰点
        "limit_up": "<10",
        "limit_down": ">",  # 跌停多于涨停
        "red_line": "<500",
        "highest_board": "<=4",
        "position": "0-10%"
    },
    "start": {  # 启动
        "limit_up": ">=30",
        "limit_down": "<10",
        "red_line": ">2000",
        "highest_board": ">4",
        "position": "30-50%"
    },
    "ferment": {  # 发酵
        "continuous_board": ">=15",
        "limit_up_ratio": ">80%",
        "broken_plate_ratio": "<20%",
        "position": "50-70%"
    },
    "peak": {  # 高潮
        "limit_up": ">=60",
        "highest_board": ">=7",
        "position": "50-70%",  # 逐步减
        "action": "逐步减仓"
    },
    "decline": {  # 退潮
        "limit_down": ">=10",
        "broken_plate_ratio": ">50%",
        "highest_board": "<=4",
        "position": "0-10%"
    }
}
```

### 5.2 计划生成模块 (PlanGeneratorAgent)

```python
# 模块职责：根据市场分析和策略配置生成交易计划

class PlanGeneratorAgent:
    """计划生成Agent"""

    async def generate_plans(
        self,
        analysis: AIMarketAnalysis,
        selections: List[AIStockSelection],
        strategy: AIStrategyConfig,
        capital: float
    ) -> List[AITradePlan]:
        """
        生成交易计划
        1. 根据仓位配置分配每只股票的仓位
        2. 计算价格区间
        3. 设置止损止盈
        4. 生成验证条件
        """

    def _calculate_position(self, stock: AIStockSelection, strategy: AIStrategyConfig) -> float:
        """计算仓位"""

    def _calculate_prices(self, stock: AIStockSelection, mode: str, current_price: float) -> PriceRange:
        """计算价格区间"""

    def _generate_validation(self, stock: AIStockSelection, mode: str) -> ValidationConditions:
        """生成验证条件"""
```

### 5.3 执行控制模块 (ExecutionAgent)

```python
# 模块职责：监控价格、验证条件、触发执行

class ExecutionAgent:
    """执行控制Agent"""

    async def start_monitoring(self, plan: AITradePlan):
        """开始监控计划"""

    async def check_trigger(self, plan: AITradePlan, price: float) -> TriggerResult:
        """
        检查触发条件
        1. 价格是否到达
        2. 验证条件是否满足
        3. 是否在有效时段
        """

    async def execute_plan(self, plan: AITradePlan, price: float, quantity: int) -> Trade:
        """执行计划"""

    async def check_time_stop(self, position: Position) -> bool:
        """检查时间止损"""

    async def check_stop_loss(self, position: Position, current_price: float) -> bool:
        """检查止损"""

    async def check_take_profit(self, position: Position, current_price: float) -> TakeProfitResult:
        """检查止盈"""
```

### 5.4 学习优化模块 (LearningAgent)

```python
# 模块职责：从历史交易中学习，优化策略

class LearningAgent:
    """学习优化Agent"""

    async def learn(self, start_date: date, end_date: date) -> AILearning:
        """
        执行学习
        1. 统计各项绩效指标
        2. 分析各模式胜率
        3. 发现优化点
        4. 生成建议
        """

    def _calculate_metrics(self, trades: List[Trade]) -> PerformanceMetrics:
        """计算绩效指标"""

    def _analyze_modes(self, trades: List[Trade]) -> ModeAnalysis:
        """分析各模式效果"""

    def _generate_insights(self, metrics: PerformanceMetrics, mode_analysis: ModeAnalysis) -> List[Insight]:
        """生成洞察"""

    def _generate_recommendations(self, insights: List[Insight]) -> StrategyAdjustment:
        """生成策略调整建议"""
```

---

## 六、核心流程时序

### 6.1 每日AI交易流程

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           每日AI交易时序图                                  │
└─────────────────────────────────────────────────────────────────────────────┘

时间        用户操作                  系统/AI                          外部
──────────  ───────────────────────  ────────────────────────────────  ──────
09:15      [点击] 开盘前分析
                                    ──▶ AI市场分析
                                                │
                                    ◀─── 返回分析结果
            [查看] 分析结果
            [点击] AI选股
                                    ──▶ AI选股
                                                │
                                    ◀─── 返回选股列表
            [查看] 选股结果
            [点击] 生成计划
                                    ──▶ AI生成计划
                                                │
                                    ◀─── 返回计划列表

09:20      [审核] 批准/修改/拒绝计划
                                    ──▶ 审批确认
                                    ──▶ 进入执行队列
                                                │
                                    ◀─── 监控已启动

09:30      [监控] 实时监控价格
                        ◀──── 行情推送
                                    │
                        ◀──── 条件触发
            [确认/取消] 执行确认
                                    ──▶ 执行交易
                                    ──▶ 记录成交
                                                │券商API
                                    ──────────▶ 成交回报
                                                │
                                    ◀─────────

10:30      [监控] 接近时间止损
                                    ──▶ 触发时间止损
                                    ──▶ 记录卖出

14:30      [监控] 尾盘处理
                                    ──▶ 检查持仓
                                    ──▶ 触发止盈/移动止损

15:00      [点击] 盘后复盘
                                    ──▶ AI学习优化
                                                │
                                    ◀─── 绩效报告+建议
```

---

## 七、总结

本完整设计文档涵盖了：

| 模块 | 内容 |
|------|------|
| **系统架构** | 前端→API→服务层→AI层→数据层 |
| **数据模型** | 10个核心表(现有4个+新增6个AI模型) |
| **API设计** | 15+核心接口(分析/选股/计划/审批/执行/学习) |
| **前端设计** | 10+核心页面(Dashboard/分析/审批/监控/绩效) |
| **核心模块** | 4大AI Agent(分析/生成/执行/学习) |

需要我开始实现某个模块吗？
