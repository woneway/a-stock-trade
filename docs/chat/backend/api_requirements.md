# 前端与后端 API 对接文档

## 后端 API 路由

### 1. 市场数据 (market)
- `GET /api/v1/market/indices` - 大盘指数
- `GET /api/v1/market/limit-up` - 涨停板数据
- `GET /api/v1/market/dragon-list` - 龙虎榜
- `GET /api/v1/market/capital-flow` - 资金流向
- `GET /api/v1/market/north-money` - 北向资金
- `GET /api/v1/market/sector-strength` - 板块强度
- `GET /api/v1/market/news` - 消息面
- `GET /api/v1/market/sentiment` - 情绪周期
- `POST /api/v1/market/indices` - 创建指数
- `POST /api/v1/market/sector-strength` - 创建板块强度
- `POST /api/v1/market/sentiment` - 创建情绪周期

### 2. 关注股票 (watch_stock)
- `GET /api/v1/watch-stock` - 获取关注股票列表
- `POST /api/v1/watch-stock` - 添加关注股票
- `GET /api/v1/watch-stock/{item_id}` - 获取单个关注股票
- `PUT /api/v1/watch-stock/{item_id}` - 更新关注股票
- `DELETE /api/v1/watch-stock/{item_id}` - 删除关注股票

### 3. 交易记录 (trade)
- `GET /api/v1/trades` - 获取交易记录
- `POST /api/v1/trades` - 创建交易记录
- `GET /api/v1/trades/summary` - 交易汇总
- `GET /api/v1/trades/{item_id}` - 获取单个交易

### 4. 计划 (plan)
- `GET /api/v1/plan/pre` - 盘前计划
- `POST /api/v1/plan/pre` - 创建盘前计划
- `PUT /api/v1/plan/pre` - 更新盘前计划
- `GET /api/v1/plan/post` - 盘后复盘
- `POST /api/v1/plan/post` - 创建盘后复盘
- `PUT /api/v1/plan/post` - 更新盘后复盘

---

## 前端期望的 API (frontend/src/services/api.ts)

### 当前问题
前端调用的 API 路径与后端不匹配：

| 前端期望路径 | 后端实际路径 | 状态 |
|-------------|-------------|------|
| /api/dashboard/summary | 无 | 需新增 |
| /api/dashboard/today-plans | 无 | 需新增 |
| /api/dashboard/positions-summary | 无 | 需新增 |
| /api/dashboard/signals | 无 | 需新增 |
| /api/plans | 无 | 需新增 |
| /api/positions | 无 | 需新增 |
| /api/trades | /api/v1/trades | 需对接 |
| /api/reviews | 无 | 需新增 |
| /api/monitored-stocks | /api/v1/watch-stock | 需对接 |
| /api/alerts | 无 | 需新增 |
| /api/account | 无 | 需新增 |
| /api/risk-config | 无 | 需新增 |
| /api/all-settings | 无 | 需新增 |

---

## 待处理事项

### 后端需要实现
1. Dashboard 相关 API (summary, today-plans, positions-summary, signals)
2. Plans CRUD API
3. Positions CRUD API
4. Reviews API
5. Alerts API
6. Settings API (account, risk-config, notification-config, app-config)

### 前端需要调整
1. 将 /api/monitored-stocks 改为 /api/v1/watch-stock
2. 将 /api/trades 改为 /api/v1/trades
3. 添加缺失的 API 调用
