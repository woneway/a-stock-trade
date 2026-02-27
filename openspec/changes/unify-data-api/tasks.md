# Tasks: unify-data-api

## 1. 创建数据血缘表

### 1.1 创建 DataLineage 模型
- [x] 在 `backend/app/models/` 下创建 `data_lineage.py`
- [x] 定义 DataLineage SQLModel，包含字段：id, func_name, params_hash, source, last_updated, record_count
- [x] 添加 func_name + params_hash 唯一索引

### 1.2 注册模型到数据库
- [x] 在 `backend/app/models/__init__.py` 导出 DataLineage
- [x] 验证数据库迁移创建 data_lineage 表

## 2. 简化 execute 接口

### 2.1 分离缓存服务
- [x] 重命名 `yz_data_service.py` 为 `cache_service.py` (或保留) - 保留原文件名
- [x] 提取查询缓存方法到独立函数
- [x] 提取保存缓存方法到独立函数
- [x] 确保 cache_service 只负责缓存操作

### 2.2 修改 execute 接口
- [x] 读取 `backend/app/routers/data_v2.py`
- [x] 简化 execute 路由逻辑：调用缓存服务 → 返回结果
- [x] 添加 lineage 信息到响应

### 2.3 添加血缘记录
- [x] 在缓存命中时，更新 lineage 的 last_updated
- [x] 在缓存未命中调用 akshare 后，记录新的 lineage
- [x] 返回 lineage.source 标识数据来源

## 3. 删除重复接口

### 3.1 移除 yz_data 路由
- [x] 删除 `backend/app/routers/yz_data.py` - 从 main.py 中移除路由注册
- [x] 或保留空文件作为 404 兼容

### 3.2 更新路由注册
- [x] 读取 `backend/app/main.py`
- [x] 移除 yz_data 路由注册
- [x] 验证 data_v2 路由正常工作

## 4. 测试验证

### 4.1 后端测试
- [x] 测试 execute 接口返回 lineage 信息
- [x] 测试缓存命中时 source="cache"
- [x] 测试缓存未命中时 source="akshare"
- [x] 测试删除 yz_data 路由后前端调用正常

### 4.2 前后端联调
- [ ] 启动后端服务
- [ ] 启动前端服务
- [ ] 验证游资数据页面正常工作

## 5. 代码审查

### 5.1 代码质量检查
- [x] 使用 code-reviewer 审查修改的代码
- [x] 修复提出的问题

### 5.2 提交代码
- [ ] 创建 git commit
- [ ] 推送到远程仓库
