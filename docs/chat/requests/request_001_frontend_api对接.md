# API 请求 #001 - 前端对接后端现有接口

## 发起方
前端

## 优先级
高

## 需求描述
前端目前使用 Mock 数据，需要对接后端真实 API。请确认后端已实现的接口，前端将调整代码进行对接。

## 后端已实现的接口

### 1. 市场数据 (market)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/market/indices | 大盘指数 |
| GET | /api/v1/market/limit-up | 涨停板数据 |
| GET | /api/v1/market/dragon-list | 龙虎榜 |
| GET | /api/v1/market/capital-flow | 资金流向 |
| GET | /api/v1/market/north-money | 北向资金 |
| GET | /api/v1/market/sector-strength | 板块强度 |
| GET | /api/v1/market/news | 消息面 |
| GET | /api/v1/market/sentiment | 情绪周期 |

### 2. 关注股票 (watch_stock)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/watch-stock | 获取关注股票列表 |
| POST | /api/v1/watch-stock | 添加关注股票 |
| GET | /api/v1/watch-stock/{id} | 获取单个 |
| PUT | /api/v1/watch-stock/{id} | 更新 |
| DELETE | /api/v1/watch-stock/{id} | 删除 |

### 3. 交易记录 (trade)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/trades | 获取交易记录 |
| POST | /api/v1/trades | 创建交易 |
| GET | /api/v1/trades/summary | 交易汇总 |
| GET | /api/v1/trades/{id} | 获取单个 |

### 4. 计划 (plan)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/plan/pre | 盘前计划 |
| POST | /api/v1/plan/pre | 创建盘前计划 |
| PUT | /api/v1/plan/pre | 更新盘前计划 |
| GET | /api/v1/plan/post | 盘后复盘 |
| POST | /api/v1/plan/post | 创建复盘 |
| PUT | /api/v1/plan/post | 更新复盘 |

## 前端需要后端补充的接口

### 缺失清单
1. **Dashboard 汇总** - GET /api/dashboard/summary
2. **持仓列表** - GET /api/positions
3. **设置** - GET/PUT /api/settings (账户、风控、通知)
4. **策略管理** - GET/POST/PUT/DELETE /api/strategies
5. **提醒** - GET/POST/DELETE /api/alerts

## 状态
pending

## 创建时间
2026-02-22 10:00:00
