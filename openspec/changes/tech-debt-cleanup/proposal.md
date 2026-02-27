## Why

项目存在严重的技术债务问题，影响开发效率和系统安全：
1. **安全问题** - CORS 配置过于宽松、SECRET_KEY 硬编码、DEBUG 未关闭
2. **未使用代码** - 多个文件/目录未被使用但占用空间
3. **代码重复** - get_db() 在多处重复定义
4. **超大文件** - data.py 超过 3000 行，难以维护

## What Changes

### 1. 安全修复
- 修复 CORS 配置，允许具体来源而非 "*"
- SECRET_KEY 从环境变量读取
- DEBUG 默认改为 False

### 2. 清理未使用代码
- 删除 backend/app/routers/yz_data.py
- 删除 backend/app/providers/ 目录
- 删除 backend/app/agents/ 目录
- 删除 frontend/src/hooks/useFetch.ts
- 删除 frontend/src/services/aiPlan.ts

### 3. 提取公共依赖
- 在 database.py 添加 get_db() 函数
- 替换所有重复的 get_db() 定义

### 4. 拆分大文件
- 将 data.py 拆分为多个模块

## Capabilities

- **security-hardening**: 安全配置加固
- **code-cleanup**: 清理未使用代码
- **refactoring**: 重构提取公共代码

## Impact

- **删除**: 5 个未使用文件/目录
- **修改**: CORS 配置、config.py、database.py、3个路由文件
- **拆分**: data.py 拆分为多个模块
