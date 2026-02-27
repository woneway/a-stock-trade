# A股交易系统 - AkShare 接口接入文档

> 本文档记录已接入的 AkShare 数据接口，包含接口名、描述、出入参等信息。

---

## 一、已配置缓存的接口

### 1. 实时行情

| 接口名 | 描述 | 查询类型 | 同步到DB | 备注 |
|--------|------|-----------|-----------|------|
| stock_zh_a_spot_em | A股实时行情 | realtime | 否 | 实时数据，每次从akshare获取 |

### 2. 涨跌停

| 接口名 | 描述 | 查询类型 | 同步到DB | 备注 |
|--------|------|-----------|-----------|------|
| stock_zh_a_limit_up_em | 涨停板 | date | 是 | 按日期查询，需传date参数(YYYYMMDD) |
| stock_zt_pool_em | 涨停板池 | date | 是 | 按日期查询，需传trade_date参数 |

### 3. 资金流向

| 接口名 | 描述 | 查询类型 | 同步到DB | 备注 |
|--------|------|-----------|-----------|------|
| stock_individual_fund_flow | 个股资金流向 | stock | 是 | 按股票代码查询，需传stock参数 |
| stock_sector_fund_flow_rank | 板块资金流向排名 | params | 是 | 需传indicator(净额/占比)、sector_type(行业/概念) |

### 4. 龙虎榜

| 接口名 | 描述 | 查询类型 | 同步到DB | 备注 |
|--------|------|-----------|-----------|------|
| stock_lhb_detail_em | 龙虎榜详情 | date_range | 是 | 按日期范围查询，需传start_date、end_date |
| stock_lhb_yytj_sina | 龙虎榜游资追踪 | latest | 是 | 返回最新游资动向 |
| stock_lh_yyb_most | 龙虎榜营业部-上榜次数 | latest | 是 | 返回上榜次数最多的营业部 |

### 5. 板块

| 接口名 | 描述 | 查询类型 | 同步到DB | 备注 |
|--------|------|-----------|-----------|------|
| stock_board_industry_name_em | 行业板块 | realtime | 否 | 实时获取 |
| stock_board_concept_name_em | 概念板块 | realtime | 否 | 实时获取 |

### 6. 涨停板池

| 接口名 | 描述 | 查询类型 | 同步到DB | 备注 |
|--------|------|-----------|-----------|------|
| stock_zt_pool_strong_em | 涨停板池-强势 | realtime | 否 | 实时获取 |
| stock_zt_pool_previous_em | 昨日涨停池 | date/realtime | 是 | 支持按日期查询 |

### 7. 交易日历

| 接口名 | 描述 | 查询类型 | 同步到DB | 备注 |
|--------|------|-----------|-----------|------|
| tool_trade_date_hist_sina | A股交易日历 | date_range | 是 | 后台自动同步最近1年数据 |

---

## 二、游资常用核心接口（10个）

> 以下是游资看板使用的核心接口，已验证可用

### 1. 涨跌停数据

| 接口名 | 描述 | 主要字段 |
|--------|------|----------|
| stock_zt_pool_em | 涨停板池 | 代码、名称、现价、涨跌幅、涨停原因、连板数 |
| stock_zh_a_limit_down_em | 跌停板 | 代码、名称、现价、涨跌幅 |
| stock_zt_pool_zbgc_em | 炸板股 | 代码、名称、现价、涨跌幅 |
| stock_zt_pool_previous_em | 昨日涨停 | 代码、名称、现价、涨跌幅、涨停原因 |
| stock_zt_pool_strong_em | 强势涨停 | 代码、名称、现价、涨跌幅 |

### 2. 资金流向

| 接口名 | 描述 | 主要字段 |
|--------|------|----------|
| stock_individual_fund_flow | 个股资金流向 | 代码、名称、收盘价、涨跌幅、主力净流入-净额 |
| stock_fund_flow_concept | 概念板块资金流向 | 板块名称、主力净流入、涨跌幅 |
| stock_fund_flow_industry | 行业板块资金流向 | 板块名称、涨跌幅、成交额 |
| stock_hsgt_fund_flow_summary_em | 沪深港通资金流向 | 类型(沪股通/深股通)、今日、昨日变化 |

### 3. 龙虎榜

| 接口名 | 描述 | 主要字段 |
|--------|------|----------|
| stock_lh_yyb_most | 营业部排行 | 营业部名称、上榜次数、合计动用资金 |
| stock_lhb_detail_em | 龙虎榜详情 | 代码、名称、上榜日、解读 |

---

## 三、API 调用示例

### 1. 查询涨停板池

```bash
curl -X POST http://localhost:8000/api/data/akshare/execute \
  -H "Content-Type: application/json" \
  -d '{
    "func_name": "stock_zt_pool_em",
    "params": {}
  }'
```

### 2. 查询个股资金流向

```bash
curl -X POST http://localhost:8000/api/data/akshare/execute \
  -H "Content-Type: application/json" \
  -d '{
    "func_name": "stock_individual_fund_flow",
    "params": {}
  }'
```

### 3. 查询板块资金流向

```bash
curl -X POST http://localhost:8000/api/data/akshare/execute \
  -H "Content-Type: application/json" \
  -d '{
    "func_name": "stock_sector_fund_flow_rank",
    "params": {
      "indicator": "净额",
      "sector_type": "行业资金流"
    }
  }'
```

### 4. 查询营业部排行

```bash
curl -X POST http://localhost:8000/api/data/akshare/execute \
  -H "Content-Type: application/json" \
  -d '{
    "func_name": "stock_lh_yyb_most",
    "params": {}
  }'
```

### 5. 获取交易状态

```bash
curl http://localhost:8000/api/data/trade-status
```

返回示例：
```json
{
  "is_trade_time": true,
  "is_trade_day": true,
  "current_time": "14:30:00",
  "current_date": "2026-02-27",
  "weekday": "周五"
}
```

---

## 四、响应格式

### 成功响应

```json
{
  "source": "cache",
  "data": [
    {
      "代码": "600519",
      "名称": "贵州茅台",
      "现价": 1800.0,
      "涨跌幅": 2.5
    }
  ],
  "columns": ["代码", "名称", "现价", "涨跌幅"],
  "lineage": {
    "func_name": "stock_zt_pool_em",
    "source": "database",
    "last_updated": "2026-02-27 14:30:00",
    "record_count": 50
  }
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| source | 数据来源：cache(数据库) / akshare(实时) |
| data | 数据数组 |
| columns | 列名列表 |
| lineage | 数据血缘信息 |

---

## 五、接口分类索引

### 按用途分类

| 分类 | 接口 |
|------|------|
| **涨跌停** | stock_zt_pool_em, stock_zh_a_limit_down_em, stock_zt_pool_zbgc_em, stock_zt_pool_previous_em, stock_zt_pool_strong_em |
| **资金流向** | stock_individual_fund_flow, stock_fund_flow_concept, stock_fund_flow_industry, stock_hsgt_fund_flow_summary_em |
| **龙虎榜** | stock_lh_yyb_most, stock_lhb_detail_em, stock_lhb_yytj_sina |
| **板块** | stock_board_industry_name_em, stock_board_concept_name_em |
| **交易辅助** | tool_trade_date_hist_sina, stock_zh_a_spot_em |

---

## 六、注意事项

1. **非交易时间**：部分接口（如涨停板、跌停板）在非交易时间可能返回空数据
2. **缓存机制**：设置了缓存的接口首次调用会从akshare获取并保存到数据库，后续优先返回缓存数据
3. **强制刷新**：前端可通过设置 `Cache-Control: no-cache` 头强制从akshare获取最新数据
4. **数据字段**：部分接口返回英文字段名，系统已配置字段映射转换为中文

---

> 文档更新时间：2026-02-27
