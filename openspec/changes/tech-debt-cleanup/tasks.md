# Tasks: tech-debt-cleanup

## 1. 安全修复

### 1.1 修复 CORS 配置
- [x] 读取 `backend/app/main.py`
- [x] 修改 CORS 配置，使用环境变量控制允许来源
- [x] 添加 ALLOWED_ORIGINS 环境变量支持

### 1.2 修复 SECRET_KEY 配置
- [x] 读取 `backend/app/config.py`
- [x] 修改 SECRET_KEY 从环境变量读取
- [x] 修改 DEBUG 默认值为 False

## 2. 清理未使用代码

### 2.1 删除后端未使用文件
- [x] 删除 `backend/app/routers/yz_data.py`
- [x] 删除 `backend/app/providers/` 目录
- [x] 删除 `backend/app/agents/` 目录

### 2.2 删除前端未使用文件
- [x] 删除 `frontend/src/hooks/useFetch.ts`
- [x] 删除 `frontend/src/services/aiPlan.ts`

## 3. 提取公共依赖

### 3.1 添加 get_db() 到 database.py
- [x] 读取 `backend/app/database.py`
- [x] 添加 get_db() 函数

### 3.2 替换重复的 get_db() 定义
- [x] 修改 `backend/app/routers/daily.py` - 删除本地 get_db()，使用 Depends(get_db)
- [x] 修改 `backend/app/routers/backtest/router.py` - 删除本地 get_db()，使用 Depends(get_db)
- [x] 修改 `backend/app/routers/backtest_strategy.py` - 删除本地 get_db()，使用 Depends(get_db)

## 4. 测试验证

### 4.1 后端测试
- [x] 测试后端服务正常启动
- [x] 测试各 API 接口正常

### 4.2 前端测试
- [x] 测试前端服务正常启动
- [x] 测试各页面正常加载

## 5. 代码审查与提交

### 5.1 代码审查
- [x] 使用 code-reviewer 审查修改的代码
- [x] 修复提出的问题

### 5.2 提交代码
- [ ] 创建 git commit
- [ ] 推送到远程仓库
