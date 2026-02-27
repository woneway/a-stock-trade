## ADDED Requirements

### Requirement: 统一数据入口
所有数据查询 SHALL 通过 /api/data/akshare/* 接口访问。

#### Scenario: 统一入口
- **WHEN** 前端调用 /api/yz/* 接口
- **THEN** 路由到 /api/data/akshare/* 处理

### Requirement: 删除重复接口
yz_data.py 中的独立接口 SHALL 被删除，功能合并到 data_v2.py。

#### Scenario: 删除 yz_data
- **WHEN** yz_data.py 路由被删除
- **THEN** 所有功能通过 execute 接口访问

### Requirement: 缓存服务分离
缓存逻辑 SHALL 分离到独立服务，execute 接口只负责调度。

#### Scenario: 调用 execute
- **WHEN** 前端调用 POST /api/data/akshare/execute
- **THEN** 接口调用缓存服务，返回结果和血缘信息

### Requirement: 缓存服务返回血缘
缓存服务 SHALL 返回数据血缘信息。

#### Scenario: 缓存命中
- **WHEN** 本地有缓存数据
- **THEN** 返回 {data, columns, source: "cache", lineage: {...}}

#### Scenario: 缓存未命中
- **WHEN** 本地无缓存数据
- **THEN** 调用 akshare，返回 {data, columns, source: "akshare", lineage: {...}}
