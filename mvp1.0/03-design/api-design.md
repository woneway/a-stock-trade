# API 设计 - v7版本

## 接口规范

- 基础路径：`/api/v1`
- 数据格式：JSON
- 认证方式：Token

---

## 接口列表

### 1. Dashboard

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /dashboard/summary | 账户概览 |
| GET | /dashboard/today-plans | 今日计划 |
| GET | /dashboard/positions-summary | 持仓汇总 |
| GET | /dashboard/signals | 信号提醒 |

### 2. 交易计划

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /plans | 获取计划列表 |
| GET | /plans/{id} | 获取单个计划 |
| POST | /plans | 创建计划 |
| PUT | /plans/{id} | 更新计划 |
| DELETE | /plans/{id} | 删除计划 |
| PUT | /plans/{id}/status | 更新计划状态 |

**Request - 创建计划**
```json
{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "stock_type": "stock",
  "trade_mode": "龙头",
  "buy_timing": "十点前",
  "validation_conditions": {"volume": "5亿", "turnover": "10%"},
  "target_price": 1700.00,
  "position_ratio": 10,
  "stop_loss_price": 1562.00,
  "stop_loss_ratio": -5,
  "take_profit_price": 1870.00,
  "take_profit_ratio": 10,
  "hold_period": "1-2天",
  "logic": "AI算力龙头，技术形态突破",
  "plan_date": "2026-02-20"
}
```

### 3. 持仓管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /positions | 获取持仓列表 |
| GET | /positions/{id} | 获取单个持仓 |
| POST | /positions | 添加持仓 |
| PUT | /positions/{id} | 更新持仓 |
| DELETE | /positions/{id} | 删除持仓 |
| POST | /positions/{id}/sell | 卖出持仓 |

**Response - 持仓列表**
```json
{
  "positions": [
    {
      "id": 1,
      "stock_code": "600519",
      "stock_name": "贵州茅台",
      "quantity": 100,
      "available_quantity": 100,
      "cost_price": 1650.00,
      "current_price": 1700.00,
      "profit_amount": 5000.00,
      "profit_ratio": 3.03,
      "stop_loss_price": 1562.00,
      "status": "holding",
      "opened_at": "2026-02-15"
    }
  ]
}
```

### 4. 交易记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /trades | 获取交易记录 |
| GET | /trades/statistics | 统计数据 |
| POST | /trades | 添加交易记录 |
| GET | /trades/export | 导出交易记录 |

**Response - 统计**
```json
{
  "total_trades": 20,
  "win_count": 13,
  "loss_count": 7,
  "win_rate": 65,
  "total_profit": 12500.00,
  "avg_profit": 625.00
}
```

### 5. 复盘

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /review/emotion | 情绪周期 |
| GET | /review/sectors | 热门板块 |
| GET | /review/limit-up | 涨停板 |
| GET | /review/my-plans | 我的计划复盘 |
| GET | /review/strategy | 明日策略 |

### 6. 监控

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /monitor/plans | 监控计划股 |
| GET | /monitor/quotes | 实时行情 |
| GET | /monitor/signals | 信号提醒 |

### 7. 设置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /settings/risk | 风控配置 |
| PUT | /settings/risk | 更新风控配置 |
| GET | /settings/notification | 通知配置 |
| PUT | /settings/notification | 更新通知配置 |
| GET | /settings/theme | 主题配置 |
| PUT | /settings/theme | 更新主题配置 |

**Request - 风控配置**
```json
{
  "max_position_ratio": 20,
  "daily_loss_limit": 5,
  "default_stop_loss": -5,
  "default_take_profit": 10,
  "max_positions": 5
}
```

**Request - 通知配置**
```json
{
  "signal_notify": true,
  "trade_notify": true,
  "stop_loss_notify": true
}
```

**Request - 主题配置**
```json
{
  "theme": "dark"
}
```

---

## 响应格式

**成功**
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

**失败**
```json
{
  "code": -1,
  "message": "错误信息",
  "data": null
}
```

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| -1 | 通用错误 |
| 1001 | 参数错误 |
| 1002 | 数据不存在 |
| 2001 | 超过仓位限制 |
| 2002 | 超过持仓数限制 |
| 2003 | 超过日亏损限制 |
