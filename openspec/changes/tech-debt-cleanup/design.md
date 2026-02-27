## Context

项目存在多个技术债务问题，需要系统性地清理和修复。

### 当前问题

1. **安全配置问题**
   - CORS 允许所有来源 (`allow_origins=["*"]`)
   - SECRET_KEY 硬编码为 "secret-key"
   - DEBUG 默认 True

2. **未使用代码**
   - `backend/app/routers/yz_data.py` - 已从 main.py 移除但文件仍存在
   - `backend/app/providers/` - 目录存在但未导入
   - `backend/app/agents/` - 目录存在但未使用
   - `frontend/src/hooks/useFetch.ts` - 定义但未使用
   - `frontend/src/services/aiPlan.ts` - 定义但未使用

3. **代码重复**
   - get_db() 在 3 个路由文件中重复定义

4. **超大文件**
   - data.py 超过 3000 行

## Goals / Non-Goals

**Goals:**
1. 修复安全配置问题
2. 删除所有未使用代码
3. 提取公共 get_db() 依赖
4. 改善代码组织结构

**Non-Goals:**
- 不修改业务逻辑
- 不添加新功能
- 不改变 API 接口

## Decisions

### 1. CORS 配置

```python
# 修改前
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
)

# 修改后 - 使用环境变量控制
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
)
```

### 2. SECRET_KEY 配置

```python
# 修改前
SECRET_KEY: str = "secret-key"

# 修改后
SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
```

### 3. get_db() 提取

```python
# database.py 新增
def get_db():
    with Session(engine) as session:
        yield session
```

然后在各个路由中使用 `Depends(get_db)` 替换直接定义。

### 4. 未使用文件删除

直接删除以下文件/目录：
- backend/app/routers/yz_data.py
- backend/app/providers/
- backend/app/agents/
- frontend/src/hooks/useFetch.ts
- frontend/src/services/aiPlan.ts

## Risks / Trade-offs

- [风险] 删除 agents/ 可能影响未来 AI 功能扩展
  - 缓解：当前未使用，可保留但从 git 删除
- [权衡] 拆分 data.py 可能影响现有接口
  - 缓解：保持 API 路径不变，只移动代码位置

## Migration Plan

1. 修复安全配置
2. 删除未使用文件
3. 提取 get_db() 依赖
4. 测试验证
5. 提交代码

## Open Questions

- 是否需要保留 agents/ 目录作为未来扩展？
- data.py 拆分的粒度如何控制？
