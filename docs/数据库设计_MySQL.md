# AKShare 数据库表设计 (MySQL)

## 设计原则

1. **只保留核心表**：股票基础、历史K线、分时数据
2. **字段一致**：数据库字段与API返回字段保持一致
3. **索引优化**：针对常用查询字段建立索引

---

## 表清单

| 表名 | 对应接口 | 说明 |
|------|----------|------|
| stock_info | stock_info_a_code_name | 股票代码映射 |
| stock_kline | stock_zh_a_hist | 日K线数据 |
| stock_kline_minute | stock_zh_a_hist_min_em | 分时数据 |

---

## 字段差异说明

| 字段名 | 说明 |
|--------|------|
| **stock_kline.trade_date** | AKShare返回`日期`，数据库用`trade_date`避免与MySQL关键字冲突 |
| **stock_kline_minute.time_minute** | 用`time_minute`避免与MySQL `TIME` 类型混淆 |
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

-- 差异: 无，直接使用code/name
```

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

## 数据同步策略

### stock_info - 股票代码映射
- **更新频率**：每日
- **策略**：全量覆盖

### stock_kline - 日K线数据
- **更新频率**：每日（收盘后）
- **时间范围**：过去1年
- **策略**：增量追加，只同步新数据

### stock_kline_minute - 分时数据
- **更新频率**：每日（收盘后）
- **时间范围**：过去5日（分时数据量大，只保留近5日）
- **策略**：增量追加

---

## 同步脚本示例

```python
# sync_stock_info.py - 同步股票基本信息
from datetime import datetime, timedelta
from app.provider.akshare import get_stock_info_a_code_name

def sync_stock_info():
    """同步股票基本信息"""
    results = get_stock_info_a_code_name()
    for r in results:
        # 存入数据库
        save_stock_info(code=r.code, name=r.name)

# sync_stock_kline.py - 同步历史K线
def sync_stock_kline():
    """同步过去一年的K线数据"""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

    # 获取所有股票代码
    stocks = get_stock_info_a_code_name()

    for stock in stocks:
        results = get_stock_zh_a_hist(
            symbol=stock.code,
            start_date=start_date,
            end_date=end_date
        )
        for r in results:
            # 存入数据库
            save_kline(
                trade_date=r.日期,
                stock_code=stock.code,
                open=r.开盘,
                close=r.收盘,
                # ...
            )

# sync_stock_kline_minute.py - 同步分时数据
def sync_stock_kline_minute():
    """同步过去5天的分时数据"""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")

    stocks = get_stock_info_a_code_name()

    for stock in stocks:
        results = get_stock_zh_a_hist_min_em(
            symbol=stock.code,
            period="5",
            start_date=start_date,
            end_date=end_date
        )
        for r in results:
            # 存入数据库
            save_kline_minute(
                trade_date=r.日期,
                stock_code=stock.code,
                time_minute=r.时间,
                # ...
            )
```
