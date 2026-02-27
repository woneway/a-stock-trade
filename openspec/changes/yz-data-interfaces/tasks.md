# Tasks: yz-data-interfaces

## 1. 涨停板池相关接口

### 1.1 stock_zt_pool_strong_em - 涨停板池-强势
- [ ] 在 external_yz_common.py 创建 ExternalZtPoolStrong 模型
- [ ] 在 cache_service.py 添加缓存配置 (query_type: date)
- [ ] 实现查询和保存方法

### 1.2 stock_zt_pool_previous_em - 昨日涨停池
- [ ] 在 external_yz_common.py 创建 ExternalZtPoolPrevious 模型
- [ ] 在 cache_service.py 添加缓存配置 (query_type: date)
- [ ] 实现查询和保存方法

## 2. 板块相关接口

### 2.1 stock_board_industry_name_em - 行业板块
- [ ] 在 external_yz_common.py 创建 ExternalBoardIndustry 模型
- [ ] 在 cache_service.py 添加缓存配置 (query_type: latest)
- [ ] 实现查询和保存方法

### 2.2 stock_board_concept_name_em - 概念板块
- [ ] 在 external_yz_common.py 创建 ExternalBoardConcept 模型
- [ ] 在 cache_service.py 添加缓存配置 (query_type: latest)
- [ ] 实现查询和保存方法

## 3. 沪深港通相关接口

### 3.1 stock_hsgt_em - 沪深港通持股
- [ ] 在 external_yz_common.py 创建 ExternalHsgt 模型
- [ ] 在 cache_service.py 添加缓存配置 (query_type: date)
- [ ] 实现查询和保存方法

## 4. 融资融券相关接口

### 4.1 stock_rzrq_em - 融资融券
- [ ] 在 external_yz_common.py 创建 ExternalRzrq 模型
- [ ] 在 cache_service.py 添加缓存配置 (query_type: date)
- [ ] 实现查询和保存方法

## 5. 大宗交易相关接口

### 5.1 stock_dzjy_em - 大宗交易
- [ ] 在 external_yz_common.py 创建 ExternalDzjy 模型
- [ ] 在 cache_service.py 添加缓存配置 (query_type: date)
- [ ] 实现查询和保存方法

## 6. 测试验证

### 6.1 接口测试
- [ ] 测试每个接口的 execute 调用
- [ ] 测试缓存命中/未命中场景
- [ ] 验证返回数据与直接调用 akshare 一致性

### 6.2 数据库测试
- [ ] 验证数据正确保存到数据库
- [ ] 验证从数据库查询结果正确

## 7. 代码审查与提交

### 7.1 代码审查
- [ ] 使用 code-reviewer 审查代码

### 7.2 提交代码
- [ ] 创建 git commit
- [ ] 推送到远程仓库
