#!/usr/bin/env python3
"""
同步历史K线数据到数据库
同步过去一年的数据
"""
import sys
sys.path.insert(0, '.')

import pymysql
from datetime import datetime, timedelta
from app.provider.akshare import get_stock_info_a_code_name, get_stock_zh_a_hist

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 13306,
    'user': 'root',
    'password': 'asset123456',
    'database': 'astock',
    'charset': 'utf8mb4'
}


def sync_stock_kline(start_date: str = None, end_date: str = None, stock_codes: list = None):
    """
    同步历史K线数据

    Args:
        start_date: 开始日期，格式 YYYYMMDD，默认过去一年
        end_date: 结束日期，格式 YYYYMMDD，默认今天
        stock_codes: 股票代码列表，默认同步所有股票
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

    print(f"[{datetime.now()}] 开始同步K线数据...")
    print(f"时间范围: {start_date} - {end_date}")

    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 获取股票代码
    if stock_codes is None:
        cursor.execute('SELECT code FROM stock_info')
        stock_codes = [row[0] for row in cursor.fetchall()]
    print(f"共有 {len(stock_codes)} 只股票")

    total_records = 0
    insert_sql = '''
        INSERT INTO stock_kline (trade_date, stock_code, open, close, high, low, volume, amount, amplitude, change_pct, turnover_rate)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            open=VALUES(open), close=VALUES(close), high=VALUES(high), low=VALUES(low),
            volume=VALUES(volume), amount=VALUES(amount), amplitude=VALUES(amplitude),
            change_pct=VALUES(change_pct), turnover_rate=VALUES(turnover_rate)
    '''

    for i, code in enumerate(stock_codes):
        try:
            results = get_stock_zh_a_hist(
                symbol=code,
                start_date=start_date,
                end_date=end_date
            )

            if results:
                for r in results:
                    cursor.execute(insert_sql, (
                        str(r.日期) if r.日期 else None,
                        code,
                        r.开盘,
                        r.收盘,
                        r.最高,
                        r.最低,
                        r.成交量,
                        r.成交额,
                        r.振幅,
                        r.涨跌幅,
                        r.换手率
                    ))
                total_records += len(results)

            if (i + 1) % 100 == 0:
                conn.commit()
                print(f"已处理 {i + 1}/{len(stock_codes)} 只股票，累计 {total_records} 条K线数据")

        except Exception as e:
            print(f"处理股票 {code} 失败: {e}")

    conn.commit()
    print(f"[{datetime.now()}] 同步完成，共 {total_records} 条K线数据")

    cursor.execute('SELECT COUNT(*) FROM stock_kline')
    print(f"数据库现有: {cursor.fetchone()[0]} 条K线数据")

    conn.close()


if __name__ == "__main__":
    # 同步指定股票列表
    # sync_stock_kline(stock_codes=['000001', '000002', '600000'])

    # 同步所有股票（过去一年）
    sync_stock_kline()

    # 也可以指定日期范围
    # sync_stock_kline("20240101", "20241231")
