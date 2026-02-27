## ADDED Requirements

### Requirement: 缓存配置支持 sync 标签
系统 SHALL 支持在缓存配置中定义接口是否需要同步到数据库。

#### Scenario: sync=true 的接口需要同步
- **WHEN** 调用 execute 接口查询 `stock_zh_a_limit_up_em`，use_cache=true
- **THEN** 系统先查询本地 external_limit_up 表，如果有数据则返回缓存数据

#### Scenario: sync=false 的接口不持久化
- **WHEN** 调用 execute 接口查询 `stock_zh_a_spot_em`，use_cache=true
- **THEN** 系统直接调用 akshare API，不存储到数据库

### Requirement: 查询时自动同步
当本地无缓存数据且接口需要同步时（sync=true），系统 SHALL 自动调用 akshare 并存储到本地。

#### Scenario: 首次查询自动同步
- **WHEN** 首次查询需要同步的接口（如涨停板），本地无数据
- **THEN** 系统调用 akshare 获取数据，并**自动存储**到对应本地表，返回数据给用户

#### Scenario: 缓存不存在时自动缓存
- **WHEN** 调用 execute 接口，use_cache=true，且缓存表无数据，且 sync=true
- **THEN** 系统自动完成：
  1. 调用 akshare 获取数据
  2. 将数据存储到本地数据库
  3. 返回数据给用户

#### Scenario: 有缓存时直接返回
- **WHEN** 查询需要同步的接口，且本地有数据
- **THEN** 系统直接返回本地数据，不调用 akshare

### Requirement: use_cache 参数控制
系统 SHALL 支持 use_cache 参数控制是否使用缓存。

#### Scenario: use_cache=false 跳过缓存
- **WHEN** 调用 execute 接口设置 use_cache=false
- **THEN** 系统直接调用 akshare API，忽略本地缓存

#### Scenario: use_cache=true（默认）使用缓存
- **WHEN** 调用 execute 接口不传 use_cache 或传 use_cache=true
- **THEN** 系统优先返回本地缓存数据
