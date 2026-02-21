# 技术选型评估

## 技术栈选择

| 层级 | 技术选型 | 备选方案 | 选择理由 |
|------|----------|----------|----------|
| 后端框架 | Python FastAPI | Flask, Django | 现代化、高性能、自动API文档 |
| 数据库 | SQLite | PostgreSQL | 本地存储、零配置、个人项目足够 |
| ORM | SQLAlchemy | Peewee | 生态成熟、SQLite适配好 |
| 数据源 | akshare | baostock, 掘金API | 免费、数据较全、社区活跃 |
| 前端框架 | React 18 + TypeScript | Vue3 | 生态丰富、TS支持好 |
| 构建工具 | Vite | Webpack | 快速构建、开箱即用 |
| 样式 | Tailwind CSS | CSS Modules | 原子化CSS、开发效率高 |
| 路由 | React Router | TanStack Router | 成熟稳定 |
| 图表 | Recharts | ECharts | React生态原生、TS支持 |
| HTTP客户端 | Axios | fetch | 拦截器、错误处理方便 |

## 量化平台对比（不采用的原因）

| 平台 | 不采用原因 |
|------|------------|
| 聚宽JoinQuant | 偏量化基金场景，非游资超短线；专业版收费 |
| 迅投QMT | 50万资金门槛；机构向；需券商开通 |
| vnpy | 偏期货；学习成本高；缺A股游资场景 |
| 掘金量化 | 可作为备选数据源，但不作为主平台 |

## 不集成的服务

| 服务 | 原因 |
|------|------|
| 券商API/QMT/PTrade | 用户需求是人工操作，不需要自动交易 |
| Level2行情 | 费用高，个人用户不需要 |
| Wind/Choice | 费用高，个人用户不需要 |
