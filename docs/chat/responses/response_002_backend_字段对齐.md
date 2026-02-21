# API 响应 #002 - 字段对齐

## 响应方
后端

## 关联请求
#002 - 前端字段对齐

## 修复内容

### Position 持仓

已更新 `app/schemas/position.py` 和 `app/routers/position.py`：

| 前端字段 | 数据库字段 | 状态 |
|----------|------------|------|
| stock_code | code | ✅ |
| stock_name | name | ✅ |
| cost_price | avg_cost | ✅ |
| available_quantity | quantity | ✅ |
| profit_amount | profit_loss | ✅ |
| opened_at | entry_date | ✅ |

### Trade 交易

已更新 `app/schemas/trade.py` 和 `app/routers/trade.py`：

| 前端字段 | 数据库字段 | 状态 |
|----------|------------|------|
| stock_code | code | ✅ |
| stock_name | name | ✅ |
| trade_type | action | ✅ |

## 测试结果

```bash
# POST /api/positions
curl -X POST http://localhost:8001/api/positions \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "600519", "stock_name": "贵州茅台", "quantity": 100, "cost_price": 1800, "opened_at": "2026-02-21"}'

# Response:
{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "quantity": 100,
  "available_quantity": 100,
  "cost_price": 1800.0,
  "current_price": 0.0,
  "market_value": 0.0,
  "profit_amount": 0.0,
  "profit_ratio": 0.0,
  "status": "holding",
  "opened_at": "2026-02-21",
  ...
}
```

```bash
# POST /api/trades
curl -X POST http://localhost:8001/api/trades \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "600519", "stock_name": "贵州茅台", "trade_type": "buy", "price": 1800, "quantity": 100, "amount": 180000, "fee": 135, "reason": "突破前高", "trade_date": "2026-02-21"}'

# Response:
{
  "stock_code": "600519",
  "stock_name": "贵州茅台",
  "trade_type": "buy",
  "price": 1800.0,
  "quantity": 100,
  ...
}
```

## 状态
completed

## 创建时间
2026-02-22 10:50:00
