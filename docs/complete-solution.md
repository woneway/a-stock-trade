# 游资交易系统 - 完整实施方案

> 基于现有系统 + 新增AI能力

---

## 一、现有系统分析

### 1.1 已实现功能

| 模块 | 后端API | 前端页面 | 状态 |
|------|---------|----------|------|
| Dashboard | ✅ dashboard.py | Dashboard.tsx | 已完成 |
| 复盘 | ✅ review.py | - | 需完善 |
| 交易计划 | ✅ plans.py | TodayPlan.tsx, PlanList.tsx | 已完成 |
| 持仓 | ✅ positions.py | - | 需完善 |
| 交易记录 | ✅ trades.py | - | 需完善 |
| 监控 | ✅ monitor.py | - | 需完善 |
| 设置 | ✅ settings.py | Settings.tsx | 已完成 |
| 策略 | - | Strategy.tsx | 已完成 |
| 回测 | - | Backtest.tsx | 已完成 |

### 1.2 现有路由

```
/           - Dashboard 首页
/today      - 今日计划
/plans      - 计划列表
/strategy   - 策略配置
/settings   - 系统设置
/backtest   - 回测
```

### 1.3 现有数据模型

```python
# models.py 已有的表
TradingPlan   # 交易计划
Position      # 持仓
Trade        # 交易记录
Account      # 账户
RiskConfig   # 风控配置
NotificationConfig  # 通知配置
AppConfig    # 应用配置
```

---

## 二、需要新增的功能

### 2.1 新增页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 选股 | /selection | 股票筛选 |
| 监控 | /monitor | 实时监控 |
| 持仓 | /positions | 持仓管理 |
| 记录 | /trades | 交易记录 |
| 统计 | /statistics | 绩效统计 |

### 2.2 新增后端API

| API | 说明 |
|-----|------|
| /api/v1/selection/* | 选股相关 |
| /api/v1/monitor/* | 监控相关 |
| /api/v1/positions/* | 持仓相关 |
| /api/v1/trades/* | 交易记录相关 |
| /api/v1/statistics/* | 统计相关 |

### 2.3 新增数据模型

```python
# 需要新增的表
AIStrategyConfig     # AI策略配置
AIMarketAnalysis     # 市场分析
AIStockSelection    # 选股结果
AIExecutionLog      # 执行日志
AILearning          # 学习记录
```

---

## 三、完整实施方案

### 3.1 第一阶段：完善现有功能

#### 3.1.1 路由调整

```typescript
// App.tsx 路由调整
const routes = [
  { path: '/', name: '首页', component: Dashboard },
  { path: '/review', name: '复盘', component: Review },
  { path: '/selection', name: '选股', component: Selection },
  { path: '/plans', name: '计划', component: Plans },
  { path: '/plan/:id', name: '计划详情', component: PlanDetail },
  { path: '/monitor', name: '监控', component: Monitor },
  { path: '/positions', name: '持仓', component: Positions },
  { path: '/trades', name: '记录', component: Trades },
  { path: '/statistics', name: '统计', component: Statistics },
  { path: '/strategy', name: '策略', component: Strategy },
  { path: '/settings', name: '设置', component: Settings },
  { path: '/backtest', name: '回测', component: Backtest },
]
```

#### 3.1.2 页面组件

```
pages/
├── Dashboard.tsx      # 首页 - 保持不变
├── Review.tsx        # 复盘 - 新增
├── Selection.tsx     # 选股 - 新增
├── Plans/
│   ├── Index.tsx    # 计划列表 - 现有PlanList改
│   └── Detail.tsx   # 计划详情 - 新增
├── Monitor.tsx       # 监控 - 新增
├── Positions.tsx     # 持仓 - 新增
├── Trades.tsx        # 记录 - 新增
├── Statistics.tsx    # 统计 - 新增
├── Strategy.tsx      # 策略 - 现有
├── Settings.tsx     # 设置 - 现有
└── Backtest.tsx    # 回测 - 现有
```

### 3.2 第二阶段：新增数据模型

```python
# backend/app/models/ai_models.py

class AIStrategyConfig(Base):
    """AI策略配置"""
    __tablename__ = "ai_strategy_config"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    risk_preference = Column(String(20))        # aggressive/moderate/conservative
    trade_modes = Column(JSON)                  # ["low_buy", "breakthrough", "limit_up"]
    max_position_per_trade = Column(Float, default=20)
    max_total_position = Column(Float, default=70)
    auto_buy = Column(Boolean, default=False)
    auto_sell = Column(Boolean, default=False)
    confirm_before_trade = Column(Boolean, default=True)
    stop_loss = Column(Float, default=-5)
    time_stop_minutes = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AIMarketAnalysis(Base):
    """市场分析"""
    __tablename__ = "ai_market_analysis"

    id = Column(Integer, primary_key=True)
    analysis_date = Column(Date)

    # 指标
    limit_up_count = Column(Integer)
    limit_down_count = Column(Integer)
    broken_plate_ratio = Column(Float)
    highest_board = Column(Integer)
    red_line_ratio = Column(Float)

    # 分析结果
    market_sentiment = Column(String(20))    # bullish/bearish/neutral
    market_cycle = Column(String(20))        # ice/start/ferment/peak/decline/chaos
    risk_level = Column(Float)              # 0-1
    opportunity_score = Column(Float)        # 0-1
    recommendation = Column(String(20))      # heavy/medium/light/empty

    hot_sectors = Column(JSON)
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class AIStockSelection(Base):
    """选股结果"""
    __tablename__ = "ai_stock_selection"

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("ai_market_analysis.id"))

    stock_code = Column(String(10))
    stock_name = Column(String(50))
    sector = Column(String(50))

    selection_type = Column(String(20))     # 龙头/补涨/首板
    score = Column(Float)                  # 0-1
    recommended_mode = Column(String(20))   # 推荐交易模式
    reason = Column(Text)
    status = Column(String(20))           # pending/approved/rejected
    created_at = Column(DateTime, default=datetime.now)


class AITradePlan(Base):
    """交易计划"""
    __tablename__ = "ai_trade_plans"

    id = Column(Integer, primary_key=True)
    plan_date = Column(Date)

    stock_code = Column(String(10))
    stock_name = Column(String(50))
    trade_mode = Column(String(20))

    target_price = Column(Float)
    position_ratio = Column(Float)
    stop_loss_price = Column(Float)
    stop_loss_ratio = Column(Float)
    take_profit_price_1 = Column(Float)
    take_profit_ratio_1 = Column(Float)
    take_profit_price_2 = Column(Float)
    take_profit_ratio_2 = Column(Float)

    validation_conditions = Column(JSON)
    valid_time_start = Column(String(10))
    valid_time_end = Column(String(10))

    ai_confidence = Column(Float)
    ai_reasoning = Column(Text)

    approval_status = Column(String(20))   # pending/approved/rejected
    execution_status = Column(String(20))  # waiting/executed/cancelled

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AIExecutionLog(Base):
    """执行日志"""
    __tablename__ = "ai_execution_log"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("ai_trade_plans.id"))

    trigger_type = Column(String(50))      # price/time/stop_loss/take_profit
    trigger_price = Column(Float)
    trigger_time = Column(DateTime)

    decision = Column(String(20))          # execute/wait/skip
    result = Column(String(20))            # success/failed/cancelled

    created_at = Column(DateTime, default=datetime.now)


class AILearning(Base):
    """学习记录"""
    __tablename__ = "ai_learning"

    id = Column(Integer, primary_key=True)
    learn_date = Column(Date)

    total_trades = Column(Integer)
    win_rate = Column(Float)
    profit_loss_ratio = Column(Float)

    mode_stats = Column(JSON)
    sector_stats = Column(JSON)

    insights = Column(JSON)
    recommendations = Column(Text)

    created_at = Column(DateTime, default=datetime.now)
```

### 3.3 第三阶段：API开发

```
backend/app/api/
├── __init__.py
├── dashboard.py      # 现有 - 保持
├── review.py        # 现有 - 需完善
├── plans.py         # 现有 - 需完善
├── positions.py     # 现有 - 需完善
├── trades.py       # 现有 - 需完善
├── monitor.py      # 现有 - 需完善
├── settings.py     # 现有 - 保持
├── selection.py    # 新增 - 选股API
├── statistics.py   # 新增 - 统计API
└── ai.py           # 新增 - AI相关API
```

#### 3.3.1 选股API (selection.py)

```python
@router.get("/selection")
def get_stock_selections(
    date: str = None,
    sector: str = None,
    status: str = None
):
    """获取选股结果列表"""

@router.post("/selection/generate")
def generate_selections(request: GenerateSelectionRequest):
    """生成选股结果"""

@router.post("/selection/{id}/approve")
def approve_selection(id: int, action: str):
    """审批选股结果"""
```

#### 3.3.2 监控API (monitor.py - 扩展)

```python
@router.get("/monitor/positions")
def get_monitored_positions():
    """获取监控中的持仓"""

@router.get("/monitor/plans")
def get_monitored_plans():
    """获取监控中的计划"""

@router.post("/monitor/plan/{id}/execute")
def execute_plan(id: int, request: ExecuteRequest):
    """执行计划"""

@router.post("/monitor/position/{id}/sell")
def sell_position(id: int, request: SellRequest):
    """卖出持仓"""
```

#### 3.3.3 统计API (statistics.py)

```python
@router.get("/statistics/performance")
def get_performance(
    start_date: str,
    end_date: str,
    group_by: str = "day"  # day/week/month
):
    """获取绩效统计"""

@router.get("/statistics/mode-analysis")
def get_mode_analysis():
    """获取模式分析"""

@router.get("/statistics/sector-analysis")
def get_sector_analysis():
    """获取板块分析"""
```

#### 3.3.4 AI API (ai.py)

```python
@router.post("/ai/analyze-market")
def analyze_market():
    """AI市场分析"""

@router.post("/ai/generate-plans")
def generate_trade_plans(request: GeneratePlansRequest):
    """AI生成交易计划"""

@router.post("/ai/plan/{id}/approve")
def approve_plan(id: int, action: str):
    """审批AI计划"""

@router.get("/ai/insights")
def get_ai_insights():
    """获取AI学习洞察"""
```

### 3.4 第四阶段：前端开发

#### 3.4.1 页面组件开发

```
frontend/src/pages/
├── Dashboard.tsx      # 首页 - 优化
├── Review.tsx         # 复盘 - 新增
│   └── components/
│       ├── SentimentCard.tsx
│       ├── CycleIndicator.tsx
│       ├── SectorList.tsx
│       └── PositionSlider.tsx
│
├── Selection.tsx      # 选股 - 新增
│   └── components/
│       ├── StockCard.tsx
│       ├── SectorFilter.tsx
│       └── StockList.tsx
│
├── Plans/
│   ├── Index.tsx      # 计划列表 - 优化
│   └── Detail.tsx     # 计划详情 - 新增
│       └── components/
│           ├── PlanForm.tsx
│           ├── ValidationConditions.tsx
│           └── ApprovalActions.tsx
│
├── Monitor.tsx        # 监控 - 新增
│   └── components/
│       ├── PriceTicker.tsx
│       ├── PositionCard.tsx
│       ├── AlertList.tsx
│       └── ExecuteButton.tsx
│
├── Positions.tsx      # 持仓 - 新增
│   └── components/
│       ├── PositionCard.tsx
│       ├── ProfitTag.tsx
│       └── SellModal.tsx
│
├── Trades.tsx         # 记录 - 新增
│   └── components/
│       ├── TradeTable.tsx
│       └── TradeFilter.tsx
│
├── Statistics.tsx     # 统计 - 新增
│   └── components/
│       ├── PerformanceCard.tsx
│       ├── ProfitChart.tsx
│       ├── ModeChart.tsx
│       └── InsightPanel.tsx
│
├── Strategy.tsx       # 策略 - 现有
├── Settings.tsx       # 设置 - 现有
└── Backtest.tsx      # 回测 - 现有
```

#### 3.4.2 组件规范

```typescript
// types/index.ts
export interface Stock {
  code: string
  name: string
  sector: string
  price: number
  change: number
}

export interface TradePlan {
  id: number
  stock_code: string
  stock_name: string
  trade_mode: 'low_buy' | 'breakthrough' | 'limit_up' | 'tail'
  target_price: number
  position_ratio: number
  stop_loss_price: number
  take_profit_price_1: number
  status: 'pending' | 'approved' | 'executing' | 'completed' | 'cancelled'
}

export interface Position {
  id: number
  stock_code: string
  stock_name: string
  quantity: number
  cost_price: number
  current_price: number
  profit_amount: number
  profit_ratio: number
}

export interface Trade {
  id: number
  stock_code: string
  stock_name: string
  type: 'buy' | 'sell'
  price: number
  quantity: number
  trade_date: string
  notes: string
}

export interface MarketAnalysis {
  id: number
  analysis_date: string
  limit_up_count: number
  limit_down_count: number
  broken_plate_ratio: number
  market_sentiment: 'bullish' | 'bearish' | 'neutral'
  market_cycle: 'ice' | 'start' | 'ferment' | 'peak' | 'decline' | 'chaos'
  risk_level: number
  opportunity_score: number
  hot_sectors: string[]
}

export interface Performance {
  total_trades: number
  win_rate: number
  profit_loss_ratio: number
  total_profit: number
  max_drawdown: number
}
```

#### 3.4.3 服务层

```typescript
// services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
})

// 选股
export const selectionApi = {
  getList: (params) => api.get('/selection', { params }),
  generate: (data) => api.post('/selection/generate', data),
  approve: (id, action) => api.post(`/selection/${id}/approve`, { action }),
}

// 计划
export const planApi = {
  getList: (params) => api.get('/plans', { params }),
  get: (id) => api.get(`/plans/${id}`),
  create: (data) => api.post('/plans', data),
  update: (id, data) => api.put(`/plans/${id}`, data),
  delete: (id) => api.delete(`/plans/${id}`),
}

// 监控
export const monitorApi = {
  getPositions: () => api.get('/monitor/positions'),
  getPlans: () => api.get('/monitor/plans'),
  execute: (id, data) => api.post(`/monitor/plan/${id}/execute`, data),
  sell: (id, data) => api.post(`/monitor/position/${id}/sell`, data),
}

// 持仓
export const positionApi = {
  getList: () => api.get('/positions'),
  update: (id, data) => api.put(`/positions/${id}`, data),
}

// 记录
export const tradeApi = {
  getList: (params) => api.get('/trades', { params }),
  create: (data) => api.post('/trades', data),
}

// 统计
export const statisticsApi = {
  getPerformance: (params) => api.get('/statistics/performance', { params }),
  getModeAnalysis: () => api.get('/statistics/mode-analysis'),
  getSectorAnalysis: () => api.get('/statistics/sector-analysis'),
}

// AI
export const aiApi = {
  analyzeMarket: () => api.post('/ai/analyze-market'),
  generatePlans: (data) => api.post('/ai/generate-plans', data),
  approvePlan: (id, action) => api.post(`/ai/plan/${id}/approve`, { action }),
  getInsights: () => api.get('/ai/insights'),
}
```

---

## 四、工作流实现

### 4.1 每日工作流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          每日工作流实现                                    │
└─────────────────────────────────────────────────────────────────────────────┘

09:15 开盘前
├── 打开系统 → 首页显示今日作战模式
├── 进入复盘 → 查看昨日市场分析（自动生成）
│   └── 判断情绪周期 → 确定仓位策略
├── 进入选股 → 筛选符合条件的股票
│   └── 添加到计划
├── 进入计划 → 制定详细交易计划
│   └── 确认/修改/放弃
└── 进入监控 → 等待触发

09:30-15:00 盘中
├── 监控页面
│   ├── 价格触及目标 → 买入确认
│   ├── 止损预警 → 卖出确认
│   └── 止盈提醒 → 卖出确认
└── 持仓页面 → 查看当前持仓

15:00 盘后
├── 记录页面 → 查看今日成交
├── 统计页面 → 查看绩效统计
└── 进入复盘 → 准备明日
```

### 4.2 核心交互

```typescript
// 复盘页面交互
const handleAnalyze = async () => {
  const analysis = await aiApi.analyzeMarket()
  setMarketAnalysis(analysis)
  // 自动判断情绪周期
  // 显示仓位建议
}

// 选股页面交互
const handleSelectStocks = async (filters) => {
  const stocks = await selectionApi.generate(filters)
  setStockList(stocks)
}

const handleAddToPlan = (stock) => {
  // 跳转到计划页面，带入股票信息
  navigate('/plans', { state: { stock } })
}

// 计划页面交互
const handleApprove = async (planId, action) => {
  await planApi.update(planId, { approval_status: action })
  refreshPlans()
}

// 监控页面交互
const handleExecute = async (planId, price) => {
  await monitorApi.execute(planId, { price, quantity: 100 })
  refreshMonitor()
}

const handleSell = async (positionId, price) => {
  await monitorApi.sell(positionId, { price })
  refreshPositions()
}
```

---

## 五、实施计划

### 5.1 阶段一：基础架构（1周）

- [ ] 调整前端路由
- [ ] 新增数据模型
- [ ] 开发选股API
- [ ] 开发统计API

### 5.2 阶段二：核心页面（1周）

- [ ] 复盘页面
- [ ] 选股页面
- [ ] 计划页面优化
- [ ] 监控页面

### 5.3 阶段三：持仓与记录（3天）

- [ ] 持仓页面
- [ ] 记录页面
- [ ] 统计页面

### 5.4 阶段四：AI能力（1周）

- [ ] AI市场分析
- [ ] AI计划生成
- [ ] 学习优化

---

## 六、总结

这个方案覆盖了：

| 类别 | 内容 |
|------|------|
| 现有功能 | Dashboard、计划、策略、设置、回测 |
| 新增页面 | 复盘、选股、监控、持仓、记录、统计 |
| 新增API | 选股、监控、统计、AI |
| 新增模型 | AI策略配置、市场分析、选股结果、执行日志、学习记录 |

按照工作流：**复盘 → 选股 → 计划 → 监控 → 记录**
