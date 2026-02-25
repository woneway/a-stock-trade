# A股交易系统

## 系统架构

### 技术栈
- 后端: FastAPI + SQLModel + SQLite
- 前端: React + TypeScript + Vite
- 数据: akshare + baostock

### 目录结构
```
backend/app/
├── main.py           # FastAPI 入口
├── config.py         # 配置
├── database.py       # 数据库连接
├── models/           # ORM 模型
├── schemas/          # Pydantic schemas
├── routers/          # API 路由
│   ├── strategy.py   # 策略管理
│   ├── plan.py       # 计划管理
│   ├── trade.py      # 交易记录
│   ├── position.py   # 持仓
│   ├── dashboard.py  # 首页概览
│   ├── market.py     # 市场数据
│   ├── settings.py   # 设置
│   ├── backtest/     # 回测模块
│   └── ...
├── services/         # 业务逻辑层
├── providers/        # 数据提供者
└── agents/          # AI代理

frontend/src/
├── pages/            # 页面组件
│   ├── Dashboard.tsx  # 首页
│   ├── TodayPlan.tsx   # 今日计划
│   ├── Strategy.tsx    # 策略管理
│   ├── PlanList.tsx    # 计划列表
│   ├── Backtest.tsx    # 回测
│   └── Settings.tsx    # 设置
├── components/        # 公共组件
│   └── Layout.tsx
├── services/         # API 调用
│   └── api.ts
└── types/           # 类型定义
```

## 功能模块

### 1. 策略管理
- CRUD 策略模板
- 8大核心要素配置
- 适用场景说明

### 2. 计划管理
- 盘前计划（选股、仓位、止损）
- 盘后复盘
- 智能分析

### 3. 交易记录
- 买入/卖出记录
- 关联计划
- 盈亏统计

### 4. 持仓管理
- 当前持仓
- 成本价/现价
- 盈亏比例

### 5. 市场数据
- 大盘指数
- 涨停/跌停数据
- 龙虎榜
- 板块强度
- 换手率排行

### 6. 回测（测试中）
- 双均线策略
- RSI策略
- MACD策略
- 布林带策略

### 7. 设置
- 账户配置
- 风险控制
- 通知设置

## API 端点

| 模块 | 前缀 | 功能 |
|------|------|------|
| 策略 | `/api/strategies` | CRUD |
| 计划 | `/api/plan` | 盘前/盘后计划 |
| 交易 | `/api/trades` | 记录 |
| 持仓 | `/api/positions` | 持仓 |
| 大盘 | `/api/market` | 指数/涨停/板块 |
| 设置 | `/api/settings` | 配置 |
| 回测 | `/api/backtest` | 回测 |
| 数据 | `/api/sync` | 数据同步 |

## 启动

```bash
# 后端
cd backend && python -m uvicorn app.main:app --port 8000

# 前端
cd frontend && npm run dev
```

## 数据库

- SQLite: `backend/app/data/stock_trading.db`
- 股票数据: 5190 只
- K线数据: 24926 条

## 注意事项

- 游资策略靠复盘而非回测
- 市场数据同步需要外网访问
