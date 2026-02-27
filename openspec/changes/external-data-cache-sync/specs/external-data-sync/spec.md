## ADDED Requirements

### Requirement: 手动同步单日数据
系统 SHALL 支持手动同步指定日期的数据到本地数据库。

#### Scenario: 同步指定日期
- **WHEN** 调用 POST /api/data/akshare/sync/stock_zh_a_limit_up_em?trade_date=2025-02-27
- **THEN** 系统调用 akshare 获取指定日期数据，存储到 external_limit_up 表

#### Scenario: 同步今天（默认）
- **WHEN** 调用 POST /api/data/akshare/sync/stock_zh_a_limit_up_em（不带日期参数）
- **THEN** 系统同步今天的数据

### Requirement: 同步日期范围数据
系统 SHALL 支持同步一段时间内的数据。

#### Scenario: 同步日期范围
- **WHEN** 调用 POST /api/data/akshare/sync/stock_lhb_detail_em?start_date=2025-01-01&end_date=2025-02-27
- **THEN** 系统遍历日期范围，调用 akshare 获取每日数据，存储到 external_lhb_detail 表

### Requirement: 不支持同步的接口返回错误
系统 SHALL 对不支持同步的接口返回明确错误信息。

#### Scenario: 调用不支持同步的接口
- **WHEN** 调用 POST /api/data/akshare/sync/stock_zh_a_spot_em
- **THEN** 系统返回 400 错误，提示"该接口不支持同步"
