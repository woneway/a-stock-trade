## ADDED Requirements

### Requirement: 查询默认使用缓存
前端查询 SHALL 默认使用缓存（use_cache=true）。

#### Scenario: 首次查询触发同步
- **WHEN** 用户点击"查询"按钮，且本地无缓存
- **THEN** 系统自动从 akshare 获取数据并缓存，返回给用户

#### Scenario: 有缓存直接返回
- **WHEN** 用户点击"查询"按钮，且本地有缓存
- **THEN** 系统直接从本地返回缓存数据

### Requirement: 强制刷新功能
前端 SHALL 支持强制刷新，忽略本地缓存。

#### Scenario: 点击强制刷新
- **WHEN** 用户点击"强制刷新"按钮
- **THEN** 系统调用 execute 接口时设置 use_cache=false，强制从 akshare 获取新数据

### Requirement: 手动同步按钮
对于需要同步的接口，前端 SHALL 提供"同步"按钮。

#### Scenario: 点击同步按钮
- **WHEN** 用户点击"同步"按钮
- **THEN** 系统调用 sync 接口，将数据同步到本地数据库

### Requirement: 显示数据来源
前端 SHALL 在结果区域显示数据来源（缓存/实时）。

#### Scenario: 显示缓存标识
- **WHEN** 返回的数据来自本地缓存
- **THEN** 结果区域显示"数据来源：本地缓存"

#### Scenario: 显示实时标识
- **WHEN** 返回的数据来自 akshare 实时调用
- **THEN** 结果区域显示"数据来源：实时"
