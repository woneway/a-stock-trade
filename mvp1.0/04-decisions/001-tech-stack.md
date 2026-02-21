# ADR-001: 技术栈选择

- **状态**: 已决定
- **日期**: 2026-02-20
- **决策者**: Lianwu

## 背景

需要选择适合个人投资者使用的A股交易辅助系统技术栈，要求开发效率高、维护成本低、本地部署。

## 决策

采用 **Python FastAPI + React + SQLite** 架构。

## 理由

| 选择 | 理由 |
|------|------|
| FastAPI | 现代化、自动API文档、async支持、akshare生态契合 |
| SQLite | 零配置、本地文件、个人项目够用、无需运维 |
| SQLAlchemy | Python ORM标准、SQLite适配好 |
| akshare | 免费、A股数据覆盖全、社区活跃 |
| React 18 + TS | 生态丰富、类型安全、组件化 |
| Vite | 开发体验好、构建快 |
| Tailwind CSS | 原子化CSS、深色主题方便、开发效率高 |
| Recharts | React原生图表库、TS支持 |

## 放弃的方案

| 方案 | 放弃原因 |
|------|----------|
| Django | 过重，个人项目不需要全功能框架 |
| Vue3 | React生态更丰富，Recharts更适合金融图表 |
| PostgreSQL | 个人项目不需要，增加运维成本 |
| ECharts | 非React原生，集成成本高 |

## 后果

- 需要维护前后端两套代码
- SQLite在并发写入时有限制（个人使用不影响）
- akshare有IP限流风险，需要设计数据源抽象层
