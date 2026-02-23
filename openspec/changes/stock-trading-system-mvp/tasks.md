# 实现任务清单：A股智能交易信号系统 MVP

## 1. 项目初始化

- [ ] 1.1 创建项目目录结构 (backend/, frontend/, data/)
- [ ] 1.2 后端：创建 requirements.txt
- [ ] 1.3 前端：创建 package.json
- [ ] 1.4 安装依赖

## 2. 后端 - 数据层

- [ ] 2.1 创建SQLite数据库连接
- [ ] 2.2 实现 TargetPool 模型和Repository
- [ ] 2.3 实现 Position 模型和Repository
- [ ] 2.4 实现 Trade 模型和Repository
- [ ] 2.5 实现 StrategyConfig 模型和Repository
- [ ] 2.6 实现 TradingPlan 模型和Repository（包含交易时段控制）

## 3. 后端 - 数据获取

- [ ] 3.1 实现 akshare 数据获取服务
- [ ] 3.2 获取全市场股票列表
- [ ] 3.3 获取个股日线数据
- [ ] 3.4 获取实时行情数据
- [ ] 3.5 获取涨停板数据

## 4. 后端 - 策略实现

- [ ] 4.1 实现策略基类和接口
- [ ] 4.2 实现情绪周期-冰点策略
- [ ] 4.3 实现KDJ金叉策略
- [ ] 4.4 实现首板战法策略（可选）
- [ ] 4.5 实现策略扫描器

## 5. 后端 - API

- [ ] 5.1 创建 FastAPI 应用
- [ ] 5.2 实现 /api/scan 端点
- [ ] 5.3 实现 /api/pool 端点（包含手动选股筛选功能）
- [ ] 5.4 实现 /api/positions 端点（支持分批建仓）
- [ ] 5.5 实现 /api/trades 端点
- [ ] 5.6 实现 /api/config 端点
- [ ] 5.7 实现 /api/plan 端点（交易计划+时段控制）
- [ ] 5.8 实现复盘相关端点

## 6. 前端 - 基础

- [ ] 6.1 配置 Vite + React + TypeScript
- [ ] 6.2 配置 Tailwind CSS
- [ ] 6.3 创建页面路由
- [ ] 6.4 创建布局组件（顶部导航、侧边栏）

## 7. 前端 - 页面

- [ ] 7.1 首页/Dashboard 页面
- [ ] 7.2 目标股池页面（包含手动筛选功能）
- [ ] 7.3 交易计划页面（包含时段控制、分批建仓）
- [ ] 7.4 持仓管理页面
- [ ] 7.5 交易记录页面
- [ ] 7.6 复盘页面
- [ ] 7.7 策略配置页面

## 8. 前端 - 实时监控（V1.0）

- [ ] 8.1 实时监控页面
- [ ] 8.2 轮询服务
- [ ] 8.3 桌面通知

## 9. 集成与测试

- [ ] 9.1 前后端联调
- [ ] 9.2 完整流程测试
- [ ] 9.3 UI/UX 优化

---

## 技术栈总结

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.9+, FastAPI, SQLAlchemy, akshare |
| 前端 | React 18, TypeScript, Vite, Tailwind CSS, Recharts |
| 数据库 | SQLite |
| 数据源 | akshare |
