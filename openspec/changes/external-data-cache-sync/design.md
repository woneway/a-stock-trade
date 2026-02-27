## Context

### 背景
目前系统中有两套数据查询接口：
1. `data_v2.py` - 通用的 akshare 查询接口，每次调用实时请求 akshare
2. `yz_data.py` - 独立的游资数据接口，有本地缓存能力

两套系统完全割裂，增加了维护成本。用户需要：
- 区分哪些接口走 yz_data，哪些走 data_v2
- 手动管理数据同步

### 约束
- 每个外部数据表与 akshare 接口一对一对应
- 实时行情不需要持久化到数据库
- 其他接口需要支持手动/自动同步到本地

## Goals / Non-Goals

**Goals:**
- 统一数据查询入口，所有接口都通过 data_v2 查询
- 通用缓存能力：任何 akshare 接口都可以选择是否使用缓存
- 区分需要同步(sync=true)和不需要同步(sync=false)的接口
- 支持手动同步和自动同步

**Non-Goals:**
- 不做通用缓存表（一对一对应）
- 不修改现有业务数据库表结构

## Decisions

### 1. 缓存配置设计

```python
# 缓存配置：模型 + 是否需要同步
CACHE_MODELS = {
    "stock_zh_a_spot_em": {"model": ExternalStockSpot, "sync": False},
    "stock_zh_a_limit_up_em": {"model": ExternalLimitUp, "sync": True},
    # ...
}

# 接口定义中添加 sync 标签
CATEGORIES = {
    "A股行情": [
        {"name": "stock_zh_a_spot_em", "description": "实时行情", "sync": False},
        {"name": "stock_zh_a_limit_up_em", "description": "涨停板", "sync": True},
    ],
}
```

### 2. 执行逻辑

```python
@router.post("/execute")
def execute_akshare(
    func_name: str,
    params: dict = {},
    use_cache: bool = True,
):
    cache_config = CACHE_MODELS.get(func_name)

    # 有缓存表且启用缓存
    if cache_config and use_cache:
        local_data = query_from_local(cache_config["model"], params)
        if local_data:
            return {"source": "cache", "data": local_data}

        # 无缓存，调用akshare
        data = call_akshare(func_name, params)

        # 如果需要同步则存储
        if cache_config["sync"]:
            save_to_local(cache_config["model"], params, data)

        return {"source": "akshare", "data": data}

    # 无缓存配置，直接调用akshare
    return {"source": "akshare", "data": call_akshare(func_name, params)}
```

### 3. 同步接口设计

```python
@router.post("/sync/{func_name}")
def sync_function(
    func_name: str,
    trade_date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """手动同步数据到本地"""
    cache_config = CACHE_MODELS.get(func_name)
    if not cache_config:
        raise HTTPException(404, "该接口不支持同步")

    data = call_akshare(func_name, params)
    save_to_local(cache_config["model"], params, data)
    return {"synced": len(data), "source": "akshare"}
```

### 4. 前端设计

- 默认 use_cache=true
- 每次查询自动触发同步（如果需要）
- 添加"强制同步"按钮，调用 sync 接口

## Risks / Trade-offs

- [风险] 字段映射可能因 akshare API 变化而失效
  - 缓解：添加字段兼容性检查，记录未知字段
- [风险] 数据量过大导致数据库膨胀
  - 缓解：按日期清理旧数据，或使用分表策略
- [权衡] 实时行情不持久化，缓存失效后需重新请求
  - 接受：实时行情数据量大，持久化成本高
