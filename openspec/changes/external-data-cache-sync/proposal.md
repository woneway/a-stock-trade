## Why

目前数据查询系统存在以下问题：
1. 前后端割裂 - yz_data 是独立系统，与 data_v2 完全分开
2. 数据不同步 - 没有将 akshare 数据持久化到数据库的机制
3. 扩展性差 - 每个需要缓存的接口需要单独开发

需要实现通用的外部数据本地缓存能力，支持一键同步数据到数据库。

## What Changes

1. **扩展 data_v2.py 的 execute 接口**
   - 添加 `use_cache` 参数控制是否使用缓存
   - 添加 `sync` 标签标识哪些接口需要同步到数据库

2. **添加同步接口**
   - `POST /api/data/akshare/sync/{func_name}` - 手动同步指定函数数据

3. **完善游资常用接口的缓存表**
   - 已有8个表，需要完善字段映射

4. **前端适配**
   - 使用缓存查询参数 `use_cache=true`
   - 添加"同步"按钮触发手动同步

## Capabilities

### New Capabilities

- **external-data-cache**: 通用外部数据缓存能力
  - 支持在查询时自动缓存数据到本地表
  - 支持手动触发数据同步
  - 区分需要同步(sync=true)和不需要同步(sync=false)的接口

- **external-data-sync**: 外部数据同步管理
  - 支持按日期同步单日数据
  - 支持按日期范围同步历史数据

- **frontend-cache-query**: 前端缓存查询集成
  - 查询默认使用缓存
  - 支持手动刷新

### Modified Capabilities

- **akshare-query**: 现有 akshare 查询能力扩展
  - 新增缓存相关参数

## Impact

- **后端**: 修改 data_v2.py，扩展 execute 接口
- **前端**: 修改 DataQuery.tsx，添加缓存参数和同步按钮
- **数据库**: 已有 external_yz_common.py 的8个表
