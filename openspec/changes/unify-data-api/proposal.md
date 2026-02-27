## Why

当前后端存在三个核心问题：
1. **数据接口重叠** - yz_data.py 和 data_v2.py 功能重复，增加维护成本
2. **execute 接口逻辑复杂** - 混合了缓存、查询、同步逻辑，难以理解和维护
3. **无数据血缘** - 不知道数据从哪来、何时更新，数据可信度低

需要统一数据接口，简化逻辑，并添加数据血缘追踪。

## What Changes

1. **删除 yz_data.py 路由**
   - 将 yz_data.py 的功能合并到 data_v2.py
   - 统一通过 `/api/data/akshare/execute` 访问

2. **重构 execute 接口**
   - 分离缓存逻辑到独立服务
   - 简化主接口逻辑
   - 添加数据血缘信息返回

3. **添加数据血缘功能**
   - 返回数据来源（cache/akshare）
   - 返回数据更新时间
   - 添加 sync_status 接口查询同步状态

4. **增强同步接口**
   - 添加批量同步功能
   - 添加定时同步支持

## Capabilities

### New Capabilities
- **data-lineage**: 数据血缘追踪
  - 记录数据来源、更新时间
  - 提供数据状态查询接口
- **batch-sync**: 批量数据同步
  - 支持一次同步多个接口
  - 支持定时同步配置

### Modified Capabilities
- **akshare-query**: 现有查询能力扩展
  - 分离缓存逻辑到独立服务
  - 返回数据血缘信息

## Impact

- **删除**: backend/app/routers/yz_data.py
- **修改**: backend/app/routers/data_v2.py - execute 接口
- **修改**: backend/app/services/yz_data_service.py - 简化为纯缓存服务
- **新增**: 数据血缘表和查询接口
