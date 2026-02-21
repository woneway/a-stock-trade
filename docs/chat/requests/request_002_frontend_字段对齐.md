# API 请求 #002 - 字段名称对齐

## 发起方
前端

## 优先级
高

## 问题描述
前端期望的字段名与后端返回的字段名不一致，导致无法正常对接。

## 字段对照表

### Position 持仓

| 前端期望 | 后端当前 | 说明 |
|----------|----------|------|
| stock_code | code | 股票代码 |
| stock_name | name | 股票名称 |
| cost_price | avg_cost | 成本价 |
| available_quantity | quantity | 可用数量 |
| profit_amount | profit_loss | 盈亏金额 |
| opened_at | entry_date | 开仓日期 |

### Trade 交易

| 前端期望 | 后端当前 | 说明 |
|----------|----------|------|
| stock_code | code | 股票代码 |
| stock_name | name | 股票名称 |
| trade_type | action | 交易类型 (buy/sell) |
| trade_date | trade_date | 交易日期 |

## 修复方案

请修改后端 schema，保持字段名与前端一致：

### app/schemas/position.py
```python
class PositionBase(BaseModel):
    stock_code: str      # 原: code
    stock_name: str     # 原: name
    quantity: int
    available_quantity: int  # 新增
    cost_price: float   # 原: avg_cost
    current_price: float = 0
    profit_amount: float = 0  # 原: profit_loss
    profit_ratio: float = 0
    status: str = "holding"
    opened_at: date     # 原: entry_date
```

### app/schemas/trade.py
```python
class TradeBase(BaseModel):
    stock_code: str     # 原: code
    stock_name: str      # 原: name
    trade_type: str     # 原: action
    price: float
    quantity: int
    amount: float
    fee: float
    reason: str
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    trade_date: date
```

## 状态
pending

## 创建时间
2026-02-22 10:45:00
