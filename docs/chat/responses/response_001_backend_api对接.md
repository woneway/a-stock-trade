# API 响应 #001 - 前端对接后端接口

## 响应方
后端

## 关联请求
#001 - 前端对接后端现有接口

## 问题说明

### 1. API 路径差异
前端使用 `/api/v1/...`，后端当前使用 `/api/...`

**解决方案**: 前端已将 `baseURL` 改为 `/api`，通过 Vite 代理转发

### 2. 需要实现的缺失接口

| 序号 | 接口 | 路径 | 状态 | 说明 |
|------|------|------|------|------|
| 1 | Dashboard 汇总 | GET /api/dashboard/summary | 待实现 | 今日计划数、持仓数、胜率等 |
| 2 | 持仓列表 | GET /api/positions | 待实现 | 当前持仓股票 |
| 3 | 账户设置 | GET/PUT /api/settings/account | 待实现 | 资金账号等 |
| 4 | 风控设置 | GET/PUT /api/settings/risk | 待实现 | 止损比例、仓位等 |
| 5 | 通知设置 | GET/PUT /api/settings/notification | 待实现 | 提醒开关等 |
| 6 | 策略管理 | GET/POST/PUT/DELETE /api/strategies | 待实现 | 交易策略配置 |
| 7 | 提醒列表 | GET /api/alerts | 待实现 | 监控提醒 |

## 已对接接口验证

| 接口 | 状态 |
|------|------|
| /api/market/* | ✅ 已对接 |
| /api/watch-stocks | ✅ 已对接 |
| /api/trades | ✅ 已对接 |
| /api/plan/pre | ✅ 已对接 |
| /api/plan/post | ✅ 已对接 |

## 已完成

后端已完成以下接口实现：

### Dashboard
| 接口 | 方法 | 状态 |
|------|------|------|
| /api/dashboard/summary | GET | ✅ |

### Settings
| 接口 | 方法 | 状态 |
|------|------|------|
| /api/settings/account | GET/PUT | ✅ |
| /api/settings/risk | GET/PUT | ✅ |
| /api/settings/notification | GET/PUT | ✅ |

### Positions
| 接口 | 方法 | 状态 |
|------|------|------|
| /api/positions | GET/POST | ✅ |
| /api/positions/{id} | GET/PUT/DELETE | ✅ |
| /api/positions/{id}/close | POST | ✅ |

### Alerts
| 接口 | 方法 | 状态 |
|------|------|------|
| /api/alerts | GET/POST | ✅ |
| /api/alerts/{id} | GET/PUT/DELETE | ✅ |
| /api/alerts/{id}/trigger | POST | ✅ |

### Strategies
| 接口 | 方法 | 状态 |
|------|------|------|
| /api/strategies | GET/POST | ✅ |
| /api/strategies/{id} | GET/PUT/DELETE | ✅ |

## 状态
completed

## 创建时间
2026-02-22 10:30:00
