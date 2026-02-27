## Why

游资常用数据接口有15个，但只有8个配置了缓存和DB模型，还有7个接口未配置：
- stock_zt_pool_strong_em - 涨停板池-强势
- stock_zt_pool_previous_em - 昨日涨停池
- stock_board_industry_name_em - 行业板块
- stock_board_concept_name_em - 概念板块
- stock_hsgt_em - 沪深港通持股
- stock_rzrq_em - 融资融券
- stock_dzjy_em - 大宗交易

## What Changes

### 1. 补充缺失的缓存配置
为7个接口添加 CACHE_CONFIG 配置：
- 确定查询类型 (date/params/latest)
- 确定是否需要同步到数据库
- 配置对应的数据库模型

### 2. 创建数据库模型
为需要缓存的接口创建对应的数据库模型：
- ExternalZtPoolStrong
- ExternalZtPoolPrevious
- ExternalBoardIndustry
- ExternalBoardConcept
- ExternalHsgt
- ExternalRzrq
- ExternalDzjy

### 3. 实现数据查询和保存方法
在 CacheService 中实现对应的查询和保存方法

## Capabilities

- **cache-config**: 补充缓存配置
- **db-model**: 创建数据库模型
- **query-method**: 实现查询和保存方法

## Impact

- 新增 7 个数据库模型
- 修改 cache_service.py 添加缓存配置和方法
- 修改 external_yz_common.py 添加模型定义
