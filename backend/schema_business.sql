-- 业务数据表结构
-- 从 SQLite 迁移到 MySQL

-- 计划表
CREATE TABLE IF NOT EXISTS plans (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50) NOT NULL COMMENT '类型: day_plan/weekly_plan',
    trade_date DATE NOT NULL COMMENT '交易日期',
    status VARCHAR(50) NOT NULL COMMENT '状态: draft/executing/completed',
    template TEXT COMMENT '模板',
    content TEXT COMMENT '内容',
    related_id BIGINT COMMENT '关联计划ID',
    stock_count INT COMMENT '股票数量',
    execution_rate FLOAT COMMENT '执行率',
    pnl FLOAT COMMENT '盈亏',
    tags VARCHAR(500) COMMENT '标签',
    created_at DATE NOT NULL COMMENT '创建日期',
    updated_at DATE NOT NULL COMMENT '更新日期',
    INDEX idx_trade_date (trade_date),
    INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='计划表';

-- 回测策略表
CREATE TABLE IF NOT EXISTS backtest_strategies (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '策略名称',
    strategy_type VARCHAR(50) COMMENT '策略类型',
    description TEXT COMMENT '描述',
    params TEXT COMMENT '参数JSON',
    created_at DATE NOT NULL,
    updated_at DATE NOT NULL,
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测策略表';

-- 持仓表
CREATE TABLE IF NOT EXISTS positions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    position_type VARCHAR(20) NOT NULL COMMENT '持仓类型: long/short',
    quantity INT NOT NULL COMMENT '数量',
    avg_cost DECIMAL(20,4) COMMENT '平均成本',
    current_price DECIMAL(20,4) COMMENT '当前价格',
    market_value DECIMAL(20,4) COMMENT '市值',
    unrealized_pnl DECIMAL(20,4) COMMENT '未实现盈亏',
    realized_pnl DECIMAL(20,4) COMMENT '已实现盈亏',
    position_ratio DECIMAL(10,4) COMMENT '仓位比例',
    trade_date DATE NOT NULL COMMENT '交易日期',
    created_at DATE NOT NULL,
    updated_at DATE NOT NULL,
    UNIQUE KEY uk_code_date (stock_code, trade_date),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓表';

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(50) NOT NULL COMMENT '订单ID',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    direction VARCHAR(10) NOT NULL COMMENT '方向: buy/sell',
    order_type VARCHAR(20) NOT NULL COMMENT '订单类型: limit/market',
    price DECIMAL(20,4) COMMENT '委托价格',
    quantity INT NOT NULL COMMENT '委托数量',
    filled_quantity INT COMMENT '成交数量',
    status VARCHAR(20) NOT NULL COMMENT '状态: pending/filled/cancelled',
    order_date DATE NOT NULL COMMENT '委托日期',
    order_time TIME NOT NULL COMMENT '委托时间',
    filled_date DATE COMMENT '成交日期',
    filled_time TIME COMMENT '成交时间',
    created_at DATE NOT NULL,
    updated_at DATE NOT NULL,
    INDEX idx_order_id (order_id),
    INDEX idx_stock_code (stock_code),
    INDEX idx_order_date (order_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 成交记录表
CREATE TABLE IF NOT EXISTS trades (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_id VARCHAR(50) NOT NULL COMMENT '成交ID',
    order_id VARCHAR(50) COMMENT '订单ID',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    direction VARCHAR(10) NOT NULL COMMENT '方向: buy/sell',
    price DECIMAL(20,4) NOT NULL COMMENT '成交价格',
    quantity INT NOT NULL COMMENT '成交数量',
    amount DECIMAL(20,4) NOT NULL COMMENT '成交金额',
    commission DECIMAL(20,4) COMMENT '手续费',
    trade_date DATE NOT NULL COMMENT '成交日期',
    trade_time TIME NOT NULL COMMENT '成交时间',
    created_at DATE NOT NULL,
    updated_at DATE NOT NULL,
    INDEX idx_trade_id (trade_id),
    INDEX idx_stock_code (stock_code),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成交记录表';

-- 策略信号表
CREATE TABLE IF NOT EXISTS strategy_signals (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    strategy_name VARCHAR(100) NOT NULL COMMENT '策略名称',
    stock_code VARCHAR(10) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(50) COMMENT '股票名称',
    signal_value VARCHAR(20) NOT NULL COMMENT '信号: buy/sell/hold',
    strength DECIMAL(10,4) COMMENT '信号强度',
    price DECIMAL(20,4) COMMENT '价格',
    reason TEXT COMMENT '原因',
    trade_date DATE NOT NULL COMMENT '交易日期',
    created_at DATE NOT NULL,
    INDEX idx_strategy (strategy_name),
    INDEX idx_stock_code (stock_code),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略信号表';

-- 交易日历表
CREATE TABLE IF NOT EXISTS trade_calendar (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    trade_date DATE NOT NULL COMMENT '交易日期',
    is_trading_day TINYINT(1) NOT NULL COMMENT '是否交易日',
    created_at DATE NOT NULL,
    UNIQUE KEY uk_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易日历表';
