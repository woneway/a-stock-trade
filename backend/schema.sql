-- AKShare 数据库表结构
-- MySQL 8.0

-- 股票代码映射
CREATE TABLE IF NOT EXISTS stock_info (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(10) NOT NULL COMMENT '股票代码',
    name VARCHAR(50) NOT NULL COMMENT '股票名称',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    UNIQUE KEY uk_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票代码映射';

-- 日K线数据
CREATE TABLE IF NOT EXISTS stock_kline (
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

-- 分时数据
CREATE TABLE IF NOT EXISTS stock_kline_minute (
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
