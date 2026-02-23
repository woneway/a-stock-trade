# 数据库设计 - v7版本

## 核心表结构

### 1. trading_plans（交易计划）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| stock_code | VARCHAR(10) | 是 | 股票代码 |
| stock_name | VARCHAR(50) | 是 | 股票名称 |
| stock_type | VARCHAR(20) | 是 | 标的类型：stock/etf/bond |
| trade_mode | VARCHAR(20) | 是 | 交易模式：龙头/首板/二板/反包/低吸/半路 |
| buy_timing | VARCHAR(50) | 否 | 买入时机：十点前/分歧转一致/低开低吸 |
| validation_conditions | TEXT | 否 | 验证条件JSON：{"volume": "5亿", "turnover": "10%"} |
| target_price | DECIMAL(10,2) | 是 | 目标买入价 |
| position_ratio | DECIMAL(5,2) | 是 | 仓位比例(%) |
| stop_loss_price | DECIMAL(10,2) | 否 | 止损价 |
| stop_loss_ratio | DECIMAL(5,2) | 否 | 止损比例(%) |
| take_profit_price | DECIMAL(10,2) | 否 | 止盈价 |
| take_profit_ratio | DECIMAL(5,2) | 否 | 止盈比例(%) |
| hold_period | VARCHAR(20) | 否 | 持仓周期：1天/2天/3天 |
| logic | TEXT | 否 | 题材/逻辑 |
| status | VARCHAR(20) | 是 | 状态：observing/holding/completed |
| execute_result | VARCHAR(50) | 否 | 执行结果：已买入/条件未满足/止盈卖出/止损卖出/放弃 |
| plan_date | DATE | 是 | 计划日期 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

### 2. positions（持仓）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| stock_code | VARCHAR(10) | 是 | 股票代码 |
| stock_name | VARCHAR(50) | 是 | 股票名称 |
| quantity | INTEGER | 是 | 持仓数量 |
| available_quantity | INTEGER | 是 | 可用数量（T+1限制） |
| cost_price | DECIMAL(10,2) | 是 | 成本价 |
| current_price | DECIMAL(10,2) | 否 | 当前价 |
| profit_amount | DECIMAL(12,2) | 否 | 盈亏金额 |
| profit_ratio | DECIMAL(8,4) | 否 | 盈亏比例(%) |
| stop_loss_price | DECIMAL(10,2) | 否 | 止损价 |
| take_profit_price | DECIMAL(10,2) | 否 | 止盈价 |
| plan_id | INTEGER | 否 | 关联计划ID |
| status | VARCHAR(20) | 是 | 状态：holding/closed |
| opened_at | DATE | 是 | 建仓日期 |
| created_at | DATETIME | 是 | 创建时间 |
| updated_at | DATETIME | 是 | 更新时间 |

### 3. trades（交易记录）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| stock_code | VARCHAR(10) | 是 | 股票代码 |
| stock_name | VARCHAR(50) | 是 | 股票名称 |
| trade_type | VARCHAR(10) | 是 | buy/sell |
| quantity | INTEGER | 是 | 成交数量 |
| price | DECIMAL(10,2) | 是 | 成交价格 |
| amount | DECIMAL(12,2) | 是 | 成交金额 |
| fee | DECIMAL(10,2) | 否 | 手续费 |
| stamp_duty | DECIMAL(10,2) | 否 | 印花税 |
| position_id | INTEGER | 否 | 关联持仓ID |
| plan_id | INTEGER | 否 | 关联计划ID |
| trade_date | DATE | 是 | 交易日期 |
| trade_time | TIME | 否 | 交易时间 |
| notes | TEXT | 否 | 备注 |
| created_at | DATETIME | 是 | 创建时间 |

### 4. market_review（市场复盘数据）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| review_date | DATE | 是 | 复盘日期 |
| emotion_cycle | VARCHAR(20) | 否 | 情绪周期：分歧/一致/高潮/退潮 |
| emotion_advice | VARCHAR(100) | 否 | 情绪建议 |
| advice_position | DECIMAL(5,2) | 否 | 建议仓位 |
| hot_sectors | JSON | 否 | 热门板块JSON |
| limit_up_count | INTEGER | 否 | 涨停数量 |
| limit_down_count | INTEGER | 否 | 跌停数量 |
| created_at | DATETIME | 是 | 创建时间 |

### 5. limit_up_stocks（涨停板）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| stock_code | VARCHAR(10) | 是 | 股票代码 |
| stock_name | VARCHAR(50) | 是 | 股票名称 |
| sector | VARCHAR(50) | 否 | 所属板块 |
| limit_time | TIME | 否 | 涨停时间 |
| seal_amount | DECIMAL(15,2) | 否 | 封单金额 |
| turnover_rate | DECIMAL(8,4) | 否 | 换手率(%) |
| break_count | INTEGER | 否 | 炸板次数 |
| review_date | DATE | 是 | 复盘日期 |
| created_at | DATETIME | 是 | 创建时间 |

### 6. account（账户）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| total_assets | DECIMAL(15,2) | 是 | 总资产 |
| available_cash | DECIMAL(15,2) | 是 | 可用资金 |
| market_value | DECIMAL(15,2) | 是 | 持仓市值 |
| today_profit | DECIMAL(12,2) | 否 | 今日盈亏 |
| today_profit_ratio | DECIMAL(8,4) | 否 | 今日盈亏比例(%) |
| total_profit | DECIMAL(12,2) | 否 | 总盈亏 |
| total_profit_ratio | DECIMAL(8,4) | 否 | 总盈亏比例(%) |
| updated_at | DATETIME | 是 | 更新时间 |

### 7. risk_config（风控配置）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| max_position_ratio | DECIMAL(5,2) | 是 | 单笔最大仓位(%) |
| daily_loss_limit | DECIMAL(5,2) | 是 | 日亏损上限(%) |
| default_stop_loss | DECIMAL(5,2) | 是 | 默认止损(%) |
| default_take_profit | DECIMAL(5,2) | 是 | 默认止盈(%) |
| max_positions | INTEGER | 是 | 最大持仓数 |
| updated_at | DATETIME | 是 | 更新时间 |

### 8. notification_config（通知配置）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| signal_notify | BOOLEAN | 是 | 信号提醒开关 |
| trade_notify | BOOLEAN | 是 | 成交通知开关 |
| stop_loss_notify | BOOLEAN | 是 | 止损通知开关 |
| updated_at | DATETIME | 是 | 更新时间 |

### 9. app_config（应用配置）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | INTEGER | 是 | 主键，自增 |
| theme | VARCHAR(20) | 是 | 主题：light/dark |
| updated_at | DATETIME | 是 | 更新时间 |

---

## 索引设计

```sql
-- 交易计划索引
CREATE INDEX idx_plan_status ON trading_plans(status);
CREATE INDEX idx_plan_date ON trading_plans(plan_date);

-- 持仓索引
CREATE INDEX idx_position_status ON positions(status);

-- 交易记录索引
CREATE INDEX idx_trade_date ON trades(trade_date);
CREATE INDEX idx_trade_stock ON trades(stock_code);

-- 涨停板索引
CREATE INDEX idx_limit_date ON limit_up_stocks(review_date);
```

---

## ER关系

```
trading_plans (1) ─────< positions (many)
positions (1) ─────< trades (many)
trading_plans (1) ─────< trades (many)
```
