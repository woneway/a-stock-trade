## ADDED Requirements

### Requirement: 数据血缘追踪
execute 接口 SHALL 返回数据血缘信息，包括数据来源、更新时间、记录数。

#### Scenario: 返回缓存数据时
- **WHEN** 查询缓存数据时
- **THEN** 返回 lineage.source="cache" 和最后更新时间

#### Scenario: 返回实时数据时
- **WHEN** 查询无缓存需要调用 akshare 时
- **THEN** 返回 lineage.source="akshare" 和当前时间

### Requirement: 数据来源标识
返回的 JSON SHALL 包含 source 字段标识数据来源。

#### Scenario: 来自缓存
- **WHEN** 数据从本地数据库获取
- **THEN** source 字段值为 "cache"

#### Scenario: 来自 akshare
- **WHEN** 数据从 akshare API 获取
- **THEN** source 字段值为 "akshare"

### Requirement: 更新时间记录
每次数据查询 SHALL 记录更新时间到血缘表。

#### Scenario: 查询时更新血缘
- **WHEN** 用户执行数据查询
- **THEN** 更新 data_lineage 表中的 last_updated 时间
