# A股交易系统开发方法记忆

## 项目架构

- 后端: FastAPI + SQLModel
- 前端: React + TypeScript + Vite

## 常用方法

### 1. 代码重构
- 创建 `services/` 目录分离业务逻辑
- 大路由文件拆分为子模块目录
- 统一 `__init__.py` 导出

### 2. 调试
- `curl` 测试API端点
- Playwright 浏览器自动化测试

### 3. 启动
- 后端: `cd backend && python -m uvicorn app.main:app --port 8000`
- 前端: `cd frontend && npm run build`

## 常见问题
- 模块导入错误 → 检查 `__init__.py` 导出
- 前端API 404 → 检查路由前缀
- Playwright失败 → 关闭Chrome实例重试
