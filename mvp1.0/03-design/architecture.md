# 技术架构设计

## 整体架构

```
前后端分离架构

用户操作 → 前端(React) → 后端API(FastAPI) → Service → Repository → SQLite
                                                  ↓
                                            策略引擎
                                                  ↓
                                            akshare(数据源)
```

## 项目结构

```
项目根目录/
├── backend/                 # 后端
│   ├── src/
│   │   ├── api/           # API路由
│   │   ├── services/      # 业务逻辑
│   │   ├── repos/         # 数据访问
│   │   ├── models/        # 数据模型
│   │   ├── strategies/    # 策略实现
│   │   └── main.py        # 入口
│   ├── requirements.txt
│   └── .env
│
├── frontend/               # 前端
│   ├── src/
│   │   ├── components/   # 通用组件
│   │   ├── pages/        # 页面组件
│   │   ├── hooks/        # 自定义Hook
│   │   ├── services/     # API服务
│   │   ├── types/        # TypeScript类型
│   │   └── App.tsx       # 入口
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
│
└── data/                  # 数据
    └── stock.db           # SQLite数据库
```

## 策略框架

```python
class BaseStrategy:
    name: str
    enabled: bool
    priority: int

    def scan(self, stocks: List[Stock]) -> List[Signal]: ...
    def filter(self, stock: Stock) -> bool: ...
    def calculate_confidence(self, stock: Stock) -> float: ...
    def get_signal_reason(self, stock: Stock) -> str: ...
```

## 实时监控架构

```
前端轮询(每60秒) → 后端API → akshare实时行情
                              ↓
                        内存缓存(60秒)
                              ↓
                        风控规则检查
                              ↓
                        Browser Notification
```

## 数据缓存策略

| 数据类型 | 缓存位置 | 过期时间 |
|----------|----------|----------|
| 实时行情 | 内存 | 60秒 |
| 涨停板 | 内存 | 5分钟 |
| 板块数据 | 内存 | 5分钟 |
| 日K线 | SQLite | 每日收盘后更新 |
| 历史数据 | SQLite | 永久保留 |
| 策略结果 | SQLite | 每日覆盖 |

## 非功能需求

| 指标 | 要求 |
|------|------|
| 数据更新 | 每日15:30后30分钟内完成 |
| 策略扫描 | 全市场 < 5分钟 |
| API响应 | < 1秒 |
| 前端加载 | < 3秒 |
