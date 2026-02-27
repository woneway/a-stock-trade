# AKShare 数据库表设计 (MySQL)

## 设计原则

1. **一对一映射**: 每个AKShare接口对应一张数据库表
2. **字段一致**: 数据库字段与API返回字段保持一致
3. **字段差异说明**: 如有差异会单独标注
4. **索引优化**: 针对常用查询字段建立索引

---

## 表清单

| 表名 | 对应接口 | 说明 |
|------|----------|------|
| stock_info | stock_info_a_code_name | 股票代码映射 |
| stock_kline | stock_zh_a_hist | 日K线数据 |
| stock_kline_minute | stock_zh_a_hist_min_em | 分时数据 |
| lhb_detail | stock_lhb_detail_em | 龙虎榜详情 |
| lhb_department | stock_lhb_yybph_em | 营业部排行 |
| lhb_stock_stats | stock_lhb_stock_statistic_em | 个股上榜统计 |
| lhb_stock_detail | stock_lhb_stock_detail_em | 个股龙虎榜详情 |
| fund_flow_market | stock_market_fund_flow | 大盘资金流向 |
| fund_flow_sector | stock_sector_fund_flow_rank | 板块资金流 |
| fund_flow_stock | stock_individual_fund_flow | 个股资金流 |
| zt_pool | stock_zt_pool_em | 涨停股池 |
| zt_pool_previous | stock_zt_pool_previous_em | 昨日涨停 |
| zt_pool_limit_down | stock_zt_pool_dtgc_em | 跌停股池 |
| zt_pool_broken | stock_zt_pool_zbgc_em | 炸板股池 |
| margin_sse | stock_margin_sse | 上交所两融 |
| margin_szse | stock_margin_szse | 深交所两融 |
| margin_account | stock_margin_account_info | 两融账户统计 |
| dzjy_detail | stock_dzjy_mrmx | 大宗交易明细 |
| dzjy_summary | stock_dzjy_mrtj | 大宗交易统计 |
| board_concept | stock_board_concept_name_em | 概念板块 |
| board_industry | stock_board_industry_name_em | 行业板块 |
| market_activity | stock_market_activity_legu | 赚钱效应 |
| market_high_low | stock_a_high_low_statistics | 创新高/新低 |
| stock_hot_rank | stock_hot_rank_em | 热度排名 |

---

## 字段差异说明

| 字段名 | 说明 |
|--------|------|
| **stock_kline.date** | AKShare返回`日期`，数据库用`date`避免与MySQL关键字冲突 |
| **fund_flow.date** | 同上，用`trade_date`更明确 |
| **margin.date** | 同上 |
| 所有`float`类型 | MySQL中统一使用`DECIMAL(20,4)`保证精度 |

---

## 详细表结构

### 1. stock_info - 股票代码映射

```sql
CREATE TABLE stock_info (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    name VARCHAR(50) NOT NULL COMMENT '股票名称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    UNIQUE KEY uk_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票代码映射';
```

**差异**: 无，直接使用code/name

---

### 2. stock_kline - 日K线数据

```sql
CREATE TABLE stock_kline (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    open DECIMAL(20,4) COMMENT '开盘价',
    close DECIMAL(20,4) COMMENT '收盘价',
    high DECIMAL(20,4) COMMENT '最高价',
    low DECIMAL(20,4) COMMENT '最低价',
    volume DECIMAL(20,4) COMMENT '成交量(手)',
    amount DECIMAL(20,4) COMMENT '成交额(元)',
    amplitude DECIMAL(10,4) COMMENT '振幅(%)',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    turnover_rate DECIMAL(10,4) COMMENT '换手率(%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date),
    INDEX idx_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日K线数据';

-- 差异: '日期' -> 'trade_date' 避免MySQL关键字冲突
```

---

### 3. stock_kline_minute - 分时数据

```sql
CREATE TABLE stock_kline_minute (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    time_minute TIME NOT NULL COMMENT '分钟时间',
    open DECIMAL(20,4) COMMENT '开盘价',
    close DECIMAL(20,4) COMMENT '收盘价',
    high DECIMAL(20,4) COMMENT '最高价',
    low DECIMAL(20,4) COMMENT '最低价',
    volume DECIMAL(20,4) COMMENT '成交量',
    amount DECIMAL(20,4) COMMENT '成交额',
    avg_price DECIMAL(20,4) COMMENT '均价',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date_time (stock_code, trade_date, time_minute),
    INDEX idx_date (trade_date),
    INDEX idx_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分时数据';

-- 差异: '时间' -> 'time_minute' 更明确
```

---

### 4. lhb_detail - 龙虎榜详情

```sql
CREATE TABLE lhb_detail (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '上榜日期',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    close_price DECIMAL(20,4) COMMENT '收盘价',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    lhb_net_buy DECIMAL(20,4) COMMENT '龙虎榜净买额(元)',
    lhb_buy DECIMAL(20,4) COMMENT '龙虎榜买入额(元)',
    lhb_sell DECIMAL(20,4) COMMENT '龙虎榜卖出额(元)',
    reason VARCHAR(200) COMMENT '上榜原因',
    after_1d_change DECIMAL(10,4) COMMENT '上榜后1日涨幅(%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date),
    INDEX idx_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='龙虎榜详情';

-- 差异: '上榜日' -> 'trade_date' 统一命名
-- 差异: '上榜后1日' -> 'after_1d_change' 更简洁
```

---

### 5. lhb_department - 营业部排行

```sql
CREATE TABLE lhb_department (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rank_num INT COMMENT '排名',
    dept_name VARCHAR(100) NOT NULL COMMENT '营业部名称',
    period VARCHAR(20) COMMENT '统计周期: 近一月/近三月等',
    buy_count_1d INT COMMENT '上榜后1天-买入次数',
    avg_change_1d DECIMAL(10,4) COMMENT '上榜后1天-平均涨幅(%)',
    up_prob_1d DECIMAL(10,4) COMMENT '上榜后1天-上涨概率(%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_dept_period (dept_name, period),
    INDEX idx_rank (rank_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='营业部排行';
```

---

### 6. lhb_stock_stats - 个股上榜统计

```sql
CREATE TABLE lhb_stock_stats (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rank_num INT COMMENT '排名',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    lhb_count INT COMMENT '上榜次数',
    lhb_net_buy DECIMAL(20,4) COMMENT '龙虎榜净买额(元)',
    period VARCHAR(20) COMMENT '统计周期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_period (stock_code, period),
    INDEX idx_rank (rank_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个股上榜统计';
```

---

### 7. lhb_stock_detail - 个股龙虎榜详情

```sql
CREATE TABLE lhb_stock_detail (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    dept_name VARCHAR(100) COMMENT '交易营业部名称',
    buy_amount DECIMAL(20,4) COMMENT '买入金额(元)',
    sell_amount DECIMAL(20,4) COMMENT '卖出金额(元)',
    net_amount DECIMAL(20,4) COMMENT '净额(元)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_code_date (stock_code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个股龙虎榜详情';
```

---

### 8. fund_flow_market - 大盘资金流向

```sql
CREATE TABLE fund_flow_market (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    sh_close DECIMAL(20,4) COMMENT '上证收盘价',
    sh_change_pct DECIMAL(10,4) COMMENT '上证涨跌幅(%)',
    sz_close DECIMAL(20,4) COMMENT '深证收盘价',
    sz_change_pct DECIMAL(10,4) COMMENT '深证涨跌幅(%)',
    main_inflow DECIMAL(20,4) COMMENT '主力净流入-净额(元)',
    main_inflow_pct DECIMAL(10,4) COMMENT '主力净流入-净占比(%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date (trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大盘资金流向';

-- 差异: '日期' -> 'trade_date'
-- 差异: 只保留核心字段(主力净流入)，完整字段可扩展
```

---

### 9. fund_flow_sector - 板块资金流

```sql
CREATE TABLE fund_flow_sector (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rank_num INT COMMENT '排名',
    sector_name VARCHAR(50) NOT NULL COMMENT '板块名称',
    sector_type VARCHAR(20) COMMENT '板块类型: 行业/概念/地域',
    indicator VARCHAR(10) COMMENT '时间范围: 今日/5日/10日',
    change_pct DECIMAL(10,4) COMMENT '今日涨跌幅(%)',
    main_inflow DECIMAL(20,4) COMMENT '主力净流入-净额(元)',
    main_inflow_stock VARCHAR(50) COMMENT '主力净流入最大股',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_name_type_indicator (sector_name, sector_type, indicator),
    INDEX idx_rank (rank_num),
    INDEX idx_indicator (indicator)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='板块资金流排名';
```

---

### 10. fund_flow_stock - 个股资金流

```sql
CREATE TABLE fund_flow_stock (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    close_price DECIMAL(20,4) COMMENT '收盘价',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    main_inflow DECIMAL(20,4) COMMENT '主力净流入-净额(元)',
    main_inflow_pct DECIMAL(10,4) COMMENT '主力净流入-净占比(%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date),
    INDEX idx_code (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个股资金流历史';
```

---

### 11. zt_pool - 涨停股池

```sql
CREATE TABLE zt_pool (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT COMMENT '序号',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    close_price DECIMAL(20,4) COMMENT '最新价',
    amount DECIMAL(20,4) COMMENT '成交额(元)',
    turnover_rate DECIMAL(10,4) COMMENT '换手率(%)',
    first_board_time TIME COMMENT '首次封板时间',
    last_board_time TIME COMMENT '最后封板时间',
    broken_count INT COMMENT '炸板次数',
    board_stats VARCHAR(20) COMMENT '涨停统计: 成功/失败',
    continuous_boards INT COMMENT '连板数',
    industry VARCHAR(50) COMMENT '所属行业',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date),
    INDEX idx_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='涨停股池';
```

---

### 12. zt_pool_previous - 昨日涨停

```sql
CREATE TABLE zt_pool_previous (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT COMMENT '序号',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    close_price DECIMAL(20,4) COMMENT '最新价',
    turnover_rate DECIMAL(10,4) COMMENT '换手率(%)',
    amplitude DECIMAL(10,4) COMMENT '振幅(%)',
    yesterday_board_time TIME COMMENT '昨日封板时间',
    yesterday_boards INT COMMENT '昨日连板数',
    industry VARCHAR(50) COMMENT '所属行业',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='昨日涨停股池';
```

---

### 13. zt_pool_limit_down - 跌停股池

```sql
CREATE TABLE zt_pool_limit_down (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT COMMENT '序号',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    close_price DECIMAL(20,4) COMMENT '最新价',
    continuous_days INT COMMENT '连续跌停天数',
    industry VARCHAR(50) COMMENT '所属行业',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='跌停股池';

-- 差异: '连续跌停' -> 'continuous_days' 更明确的命名
```

---

### 14. zt_pool_broken - 炸板股池

```sql
CREATE TABLE zt_pool_broken (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT COMMENT '序号',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    broken_count INT COMMENT '炸板次数',
    industry VARCHAR(50) COMMENT '所属行业',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='炸板股池';
```

---

### 15. margin_sse - 上交所融资融券

```sql
CREATE TABLE margin_sse (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '信用交易日期',
    margin_balance DECIMAL(20,4) COMMENT '融资余额(元)',
    margin_buy DECIMAL(20,4) COMMENT '融资买入额(元)',
    short_balance DECIMAL(20,4) COMMENT '融券余量(股)',
    margin_total DECIMAL(20,4) COMMENT '融资融券余额(元)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date (trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上交所融资融券';

-- 差异: '信用交易日期' -> 'trade_date' 统一命名
-- 差异: 字段简化，更清晰的命名
```

---

### 16. margin_szse - 深交所融资融券

```sql
CREATE TABLE margin_szse (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '信用交易日期',
    margin_balance DECIMAL(20,4) COMMENT '融资余额(元)',
    margin_buy DECIMAL(20,4) COMMENT '融资买入额(元)',
    short_sell DECIMAL(20,4) COMMENT '融券卖出量(股)',
    margin_total DECIMAL(20,4) COMMENT '融资融券余额(元)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date (trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='深交所融资融券';

-- 差异: 同上
```

---

### 17. margin_account - 两融账户统计

```sql
CREATE TABLE margin_account (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '日期',
    margin_balance DECIMAL(20,4) COMMENT '融资余额(亿元)',
    short_balance DECIMAL(20,4) COMMENT '融券余额(亿元)',
    margin_buy DECIMAL(20,4) COMMENT '融资买入额(亿元)',
    short_sell DECIMAL(20,4) COMMENT '融券卖出额(亿元)',
    company_count INT COMMENT '证券公司数量',
    dept_count INT COMMENT '营业部数量',
    personal_count DECIMAL(20,4) COMMENT '个人投资者数量',
    org_count DECIMAL(20,4) COMMENT '机构投资者数量',
    trading_count DECIMAL(20,4) COMMENT '参与交易的投资者数量',
    debt_count DECIMAL(20,4) COMMENT '有融资融券负债的投资者数量',
    collateral_value DECIMAL(20,4) COMMENT '担保物总价值(亿元)',
    avg_maintain_ratio DECIMAL(10,4) COMMENT '平均维持担保比例(%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date (trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='两融账户统计';
```

---

### 18. dzjy_detail - 大宗交易明细

```sql
CREATE TABLE dzjy_detail (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT COMMENT '序号',
    stock_code VARCHAR(10) NOT NULL COMMENT '证券代码',
    stock_name VARCHAR(50) COMMENT '证券简称',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    close_price DECIMAL(20,4) COMMENT '收盘价',
    deal_price DECIMAL(20,4) COMMENT '成交价',
    premium_rate DECIMAL(10,4) COMMENT '折溢率(%)',
    volume DECIMAL(20,4) COMMENT '成交量(股)',
    amount DECIMAL(20,4) COMMENT '成交额(元)',
    amount_ratio DECIMAL(20,4) COMMENT '成交额/流通市值',
    buyer_dept VARCHAR(100) COMMENT '买方营业部',
    seller_dept VARCHAR(100) COMMENT '卖方营业部',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date, rank_num),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大宗交易明细';

-- 差异: '序号' -> 'rank_num' 更简洁
-- 差异: '买方营业部' -> 'buyer_dept' 更简洁
```

---

### 19. dzjy_summary - 大宗交易统计

```sql
CREATE TABLE dzjy_summary (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT COMMENT '序号',
    stock_code VARCHAR(10) NOT NULL COMMENT '证券代码',
    stock_name VARCHAR(50) COMMENT '证券简称',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    close_price DECIMAL(20,4) COMMENT '收盘价',
    deal_price DECIMAL(20,4) COMMENT '成交价',
    premium_rate DECIMAL(10,4) COMMENT '折溢率(%)',
    deal_count INT COMMENT '成交笔数',
    total_volume DECIMAL(20,4) COMMENT '成交总量(万股)',
    total_amount DECIMAL(20,4) COMMENT '成交总额(万元)',
    amount_ratio DECIMAL(20,4) COMMENT '成交总额/流通市值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大宗交易统计';
```

---

### 20. board_concept - 概念板块

```sql
CREATE TABLE board_concept (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT COMMENT '排名',
    board_name VARCHAR(50) COMMENT '板块名称',
    board_code VARCHAR(20) COMMENT '板块代码',
    close_price DECIMAL(20,4) COMMENT '最新价',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    total_market DECIMAL(20,4) COMMENT '总市值',
    turnover_rate DECIMAL(10,4) COMMENT '换手率(%)',
    up_count INT COMMENT '上涨家数',
    down_count INT COMMENT '下跌家数',
    lead_stock VARCHAR(50) COMMENT '领涨股票',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (board_code, trade_date),
    INDEX idx_date (trade_date),
    INDEX idx_rank (rank_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='概念板块行情';

-- 差异: '排名' -> 'rank_num' 更简洁
-- 差异: '板块名称' -> 'board_name' 更明确
```

---

### 21. board_industry - 行业板块

```sql
CREATE TABLE board_industry (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT COMMENT '排名',
    board_name VARCHAR(50) COMMENT '板块名称',
    board_code VARCHAR(20) COMMENT '板块代码',
    close_price DECIMAL(20,4) COMMENT '最新价',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    total_market DECIMAL(20,4) COMMENT '总市值',
    turnover_rate DECIMAL(10,4) COMMENT '换手率(%)',
    up_count INT COMMENT '上涨家数',
    down_count INT COMMENT '下跌家数',
    lead_stock VARCHAR(50) COMMENT '领涨股票',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (board_code, trade_date),
    INDEX idx_date (trade_date),
    INDEX idx_rank (rank_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='行业板块行情';
```

---

### 22. market_activity - 赚钱效应分析

```sql
CREATE TABLE market_activity (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '统计日期',
    item_name VARCHAR(50) NOT NULL COMMENT '指标名称',
    item_value VARCHAR(50) COMMENT '指标值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date_item (trade_date, item_name),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='赚钱效应分析';

-- 差异: 改为键值对形式，更灵活
-- 包含: 上涨/下跌/涨停/跌停/平盘/停牌/活跃度等
```

---

### 23. market_high_low - 创新高/新低

```sql
CREATE TABLE market_high_low (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日',
    index_close DECIMAL(20,4) COMMENT '相关指数收盘价',
    high_20d INT COMMENT '20日新高',
    low_20d INT COMMENT '20日新低',
    high_60d INT COMMENT '60日新高',
    low_60d INT COMMENT '60日新低',
    high_120d INT COMMENT '120日新高',
    low_120d INT COMMENT '120日新低',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date (trade_date),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='创新高/新低统计';

-- 差异: '新高20日' -> 'high_20d' 更简洁
-- 差异: '相关指数收盘价' -> 'index_close' 更简洁
```

---

### 24. stock_hot_rank - 热度排名

```sql
CREATE TABLE stock_hot_rank (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    rank_num INT NOT NULL COMMENT '排名',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    close_price DECIMAL(20,4) COMMENT '最新价',
    change_amount DECIMAL(20,4) COMMENT '涨跌额',
    change_pct DECIMAL(10,4) COMMENT '涨跌幅(%)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_date (trade_date),
    INDEX idx_rank (rank_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票热度排名';

-- 差异: '涨跌额' -> 'change_amount' 更明确
```

---

## 字段差异汇总

| 原字段 | 数据库字段 | 差异原因 |
|--------|------------|----------|
| 日期 | trade_date | 避免与MySQL关键字`DATE`混淆 |
| 时间 | time_minute | 避免与MySQL`TIME`类型混淆 |
| 上榜日 | trade_date | 统一命名规范 |
| 序号 | rank_num | `rank`是SQL保留字 |
| 排名 | rank_num | 同上 |
| 涨跌幅 | change_pct | 更简洁的命名 |
| 涨跌额 | change_amount | 更明确的命名 |
| 融资余额 | margin_balance | 更明确的业务命名 |
| 融券余量 | short_balance | 更明确的业务命名 |
| 成交额/流通市值 | amount_ratio | 简化命名 |
| 所有金额字段 | DECIMAL(20,4) | 保证精度，AKShare返回float |

---

## 索引策略

1. **主键索引**: 自增ID
2. **唯一索引**: 防止重复数据 (code + date组合)
3. **普通索引**: 常用查询字段 (trade_date, stock_code, rank_num等)

---

## 数据更新策略

| 表类型 | 更新频率 | 策略 |
|--------|----------|------|
| stock_info | 每日 | 全量覆盖 |
| stock_kline | 每日 | 增量追加 |
| stock_kline_minute | 每日 | 增量追加 |
| lhb_* | 每日(T+1) | 增量追加 |
| fund_flow_* | 每日 | 覆盖或增量 |
| zt_pool_* | 每日 | 覆盖 |
| margin_* | 每日(T+1) | 覆盖 |
| dzjy_* | 每日(T+1) | 增量追加 |
| board_* | 每日 | 覆盖 |
| market_activity | 每日 | 覆盖 |
| market_high_low | 每日 | 覆盖 |
| stock_hot_rank | 每日 | 覆盖 |
