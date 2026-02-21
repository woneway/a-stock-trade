# 前端 API 调用需求

## 前端页面组件

### 1. 首页 (Dashboard)
- 总资产、可用资金、持仓市值、持仓数量
- 持仓列表 (股票代码、名称、成本价、现价、盈亏)
- 今日交易记录

### 2. 今日计划 (TodayPlan)
#### 盘前
- 大盘指数 (上证、创业板)
- 情绪周期 (可选择: 冰点/回暖/高潮/分歧/退潮)
- 涨停板数据
- 龙虎榜 (机构榜、游资榜)
- 资金流向 (主力流入/流出、北向资金)
- 板块强度
- 消息面
- 盘前计划保存

#### 盘中
- 关注股票列表 (股票、现价、涨跌幅、策略、持仓/成本、状态、操作)
- 监控提醒列表
- 买入/卖出交易弹窗

#### 盘后
- 今日操作记录 (股票、操作、价格、数量、金额、手续费、买入理由)
- 盘后复盘 (情绪记录、失误记录、买卖点分析、心得体会、明日计划)

### 3. 策略 (Strategy)
- 策略列表 (名称、适用场景、胜率、使用次数)
- 策略详情 (参数配置、买入信号、卖出信号)
- 从模板创建策略
- 自定义策略

### 4. 计划列表 (Plans)
- 按月份查看计划
- 计划详情 (策略、选股、执行记录、复盘总结)

### 5. 设置 (Settings)
- 账户 (总资产、可用资金)
- 风控 (仓位控制、亏损限制、止盈止损、交易限制)
- 通知 (信号提醒、交易提醒、止损提醒)
- 应用 (主题风格)

---

## 需要后端提供的 API

### Dashboard
```typescript
GET /api/dashboard/summary
// 返回: { totalAssets, availableCash, positionValue, positionCount, todayPnl, todayPnlPercent }

GET /api/dashboard/positions
// 返回: [{ code, name, quantity, entryPrice, currentPrice, pnl, pnlPercent }]

GET /api/dashboard/today-trades
// 返回: [{ code, name, action, price, quantity, amount, fee, reason, time }]
```

### 关注股票 (监控)
```typescript
GET /api/monitored-stocks
// 返回: [{ id, code, name, price, change, strategy, status, quantity?, entryPrice? }]

POST /api/monitored-stocks
// 入参: { code, name, strategy }

PUT /api/monitored-stocks/:id
// 入参: { status, quantity, entryPrice }

DELETE /api/monitored-stocks/:id
```

### 提醒
```typescript
GET /api/alerts
// 返回: [{ id, stockCode, stockName, type, message, triggered }]

POST /api/alerts
// 入参: { stockCode, stockName, alertType, targetPrice }

DELETE /api/alerts/:id
```

### 交易
```typescript
GET /api/trades
// 返回: [{ id, code, name, action, price, quantity, amount, fee, reason, entryPrice?, exitPrice?, pnl?, pnlPercent? }]

POST /api/trades
// 入参: { code, name, action, price, quantity, reason }

GET /api/trades/summary
// 返回: { tradeCount, totalFee, totalPnl }
```

### 计划
```typescript
GET /api/plans?date=2026-02-22
// 返回: [{ id, date, status, strategy, stocks, trades, review }]

GET /api/plans/:id
// 返回: { id, date, prePlan, trades, postReview }
```

### 盘前/盘后计划
```typescript
GET /api/plan/pre
// 返回: { sentiment, sectors, targetStocks, planBasis }

PUT /api/plan/pre
// 入参: { sentiment, sectors, targetStocks, planBasis }

GET /api/plan/post
// 返回: { emotionRecord, mistakes, tradeAnalysis, lessons, tomorrowPlan }

PUT /api/plan/post
// 入参: { emotionRecord, mistakes, tradeAnalysis, lessons, tomorrowPlan }
```

### 设置
```typescript
GET /api/all-settings
// 返回: { account, riskConfig, notificationConfig, appConfig }

GET /api/account
PUT /api/account

GET /api/risk-config
PUT /api/risk-config
```

### 市场数据
```typescript
GET /api/market/indices
GET /api/market/limit-up
GET /api/market/dragon-list
GET /api/market/capital-flow
GET /api/market/north-money
GET /api/market/sector-strength
GET /api/market/news
GET /api/market/sentiment
```

### 策略
```typescript
GET /api/strategies
// 返回: [{ id, name, scene, winRate, useCount, params, buySignals, sellSignals }]

POST /api/strategies
PUT /api/strategies/:id
DELETE /api/strategies/:id
```
