# 设计文档：A股智能交易信号系统 MVP

## Context

本项目是游资风格的A股交易辅助系统，核心场景是：
- 每日收盘后复盘选股
- 制定次日交易计划
- 盘中实时监控信号

第一阶段（MVP）目标：实现收盘后选股和目标股池管理，Web界面展示。

## Goals / Non-Goals

**Goals:**
- 实现每日收盘后策略扫描功能
- 实现目标股池的创建、查询、状态管理
- 实现计划价格和仓位管理
- 实现Web界面展示
- 实现本地SQLite数据存储

**Non-Goals:**
- 暂不实现实时行情监控（V1.0）
- 暂不实现卖点监控和止损提醒（V1.0）
- 暂不实现移动端完整支持

## Decisions

### Decision 1: 技术栈选择

**选择：** Python FastAPI + React + SQLite

**后端：**
- Python 3.9+
- FastAPI：现代化、高性能API框架
- SQLAlchemy：ORM
- akshare：免费A股数据接口

**前端：**
- React 18 + TypeScript
- Vite：构建工具
- Tailwind CSS：样式框架
- React Router：路由管理
- Recharts：图表库
- Axios：HTTP客户端

### Decision 2: 架构设计

**选择：** 前后端分离架构

```
项目结构:
├── backend/                 # 后端
│   ├── src/
│   │   ├── api/           # API路由
│   │   ├── services/      # 业务逻辑
│   │   ├── repos/         # 数据访问
│   │   ├── models/        # 数据模型
│   │   ├── strategies/    # 策略实现
│   │   └── main.py        # 入口
│   └── requirements.txt
│
├── frontend/               # 前端
│   ├── src/
│   │   ├── components/   # 组件
│   │   ├── pages/        # 页面
│   │   ├── hooks/        # 自定义Hook
│   │   ├── services/     # API服务
│   │   └── App.tsx       # 入口
│   ├── index.html
│   └── package.json
│
└── data/                  # 数据
    └── stock.db           # SQLite数据库
```

### Decision 3: API设计

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/scan | 执行策略扫描 |
| GET | /api/pool | 获取目标股池 |
| PUT | /api/pool/{id} | 更新目标股 |
| GET | /api/positions | 获取持仓列表 |
| POST | /api/positions | 添加持仓 |
| GET | /api/trades | 获取交易记录 |
| POST | /api/trades | 添加交易记录 |
| GET | /api/config/strategies | 获取策略配置 |
| PUT | /api/config/strategies/{name} | 更新策略配置 |

### Decision 4: 实时监控方案

**选择：** 前端轮询 + 后端缓存

- 前端每60秒轮询一次
- 后端使用内存缓存行情数据
- 桌面通知使用浏览器Notification API

### Decision 5: UI设计风格

**选择：** 深色主题 + 金融风格

- 深色背景护眼
- 红色表示上涨，绿色表示下跌（A股习惯）
- 卡片式布局，信息密度适中
- 响应式设计，优先桌面端

---

## 数据流设计

```
用户操作 -> 前端 -> 后端API -> Service -> Repository -> SQLite
                                    ↓
                              策略引擎
                                    ↓
                              akshare
```

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 数据源不稳定 | 添加重试机制，本地缓存 |
| 策略过拟合 | 保守参数，提供回测功能 |
| 前端构建复杂 | 使用Vite简化配置 |
| API安全 | CORS配置，本地部署 |

---

## 里程碑

| 周次 | 任务 |
|------|------|
| 第1周 | 项目初始化、后端架构、数据库设计 |
| 第2周 | 策略实现、API开发 |
| 第3周 | 前端开发、页面实现 |
| 第4周 | 集成测试、修复BUG |
