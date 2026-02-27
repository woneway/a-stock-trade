## Context

### 背景
当前后端有两套数据接口：
- `data_v2.py` - 通用 akshare 查询接口
- `yz_data.py` - 游资数据接口，有本地缓存

这种设计导致：
1. 功能重复，维护成本高
2. execute 接口逻辑复杂（300+ 行）
3. 无数据血缘，不知道数据来源和更新时间

### 约束
- 保持现有数据库表结构不变
- 不影响现有前端调用
- 尽量减少 breaking changes

## Goals / Non-Goals

**Goals:**
1. 统一数据入口 - 所有数据查询通过 `/api/data/akshare/*` 访问
2. 简化 execute 接口 - 分离缓存逻辑到独立服务
3. 添加数据血缘 - 返回数据来源、更新时间、同步状态

**Non-Goals:**
- 不修改数据库表结构
- 不添加定时任务（后续迭代）
- 不修改前端页面

## Decisions

### 1. 统一数据入口

```
删除 yz_data.py
保留 data_v2.py 作为唯一数据入口
```

**理由**: 减少维护成本，统一 API 风格

### 2. 分离缓存服务

```python
# 当前：execute 接口混合了所有逻辑
@router.post("/execute")
def execute():
    # 1. 检查缓存
    # 2. 调用 akshare
    # 3. 保存到数据库
    # 4. 返回数据

# 重构后：
@router.post("/execute")
def execute():
    # 1. 调用缓存服务
    # 2. 返回结果（包含血缘信息）
```

**理由**: 单一职责，易于测试和维护

### 3. 数据血缘设计

```python
class DataLineage(SQLModel, table=True):
    """数据血缘表"""
    __tablename__ = "data_lineage"

    id: int
    func_name: str  # 接口名
    params_hash: str  # 参数哈希
    source: str  # 数据来源: cache/akshare
    last_updated: datetime  # 最后更新时间
    record_count: int  # 记录数
```

**理由**: 轻量级追踪，不需要修改现有表结构

### 4. 响应格式

```json
{
  "data": [...],
  "columns": [...],
  "source": "cache",
  "lineage": {
    "func_name": "stock_lh_yyb_most",
    "source": "cache",
    "last_updated": "2025-02-27T16:30:00",
    "record_count": 153
  }
}
```

## Risks / Trade-offs

- [风险] 删除 yz_data 可能影响依赖它的前端
  - 缓解：yz_data 功能已在 data_v2 中实现，前端无需修改
- [风险] 缓存逻辑分离后可能引入 bug
  - 缓解：先在测试环境验证，再上线
- [权衡] 数据血缘会增加响应时间
  - 接受：血缘信息很小，影响可忽略

## Migration Plan

1. 创建 DataLineage 表
2. 修改 YzDataService 返回血缘信息
3. 简化 execute 接口
4. 删除 yz_data.py
5. 更新 main.py 路由注册
6. 测试验证

## Open Questions

- 是否需要保留 yz_data.py 作为兼容层？
- 数据血缘保留多长时间？（建议7天）
