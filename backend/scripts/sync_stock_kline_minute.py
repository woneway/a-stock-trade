#!/usr/bin/env python3
"""
同步分时数据到数据库
同步过去5天的数据（分时数据量大，只保留近5日）
"""
import sys
sys.path.insert(0, '.')

import pymysql
from datetime import datetime, timedelta
from app.provider.akshare import get_stock_info_a_code_name, get_stock_zh_a_hist_min_em

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 13306,
    'user': 'root',
    'password': 'asset123456',
    'database': 'astock',
    'charset': 'utf8mb4'
}


def sync_stock_kline_minute(days: int = 5, stock_codes: list = None):
    """
    同步分时数据

    Args:
        days: 保留天数，默认5天
        stock_codes: 股票代码列表，默认同步所有股票
    """
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    print(f"[{datetime.now()}] 开始同步分时数据...")
    print(f"时间范围: {start_date} - {end_date} (最近{days}天)")

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
        INSERT INTO stock_kline_minute (trade_date, stock_code, time_minute, open, close, high, low, volume, amount, avg_price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            open=VALUES(open), close=VALUES(close), high=VALUES(high), low=VALUES(low),
            volume=VALUES(volume), amount=VALUES(amount), avg_price=VALUES(avg_price)
    '''

    for i, code in enumerate(stock_codes):
        try:
            # 获取5分钟级别的分时数据
            results = get_stock_zh_a_hist_min_em(
                symbol=code,
                period="5",
                start_date=start_date,
                end_date=end_date
            )

            if results:
                for r in results:
                    cursor.execute(insert_sql, (
                        str(r.日期) if r.日期 else None,
                        code,
                        r.时间,
                        r.开盘,
                        r.收盘,
                        r.最高,
                        r.最低,
                        r.成交量,
                        r.成交额,
                        r.均价
                    ))
                total_records += len(results)

            if (i + 1) % 100 == 0:
                conn.commit()
                print(f"已处理 {i + 1}/{len(stock_codes)} 只股票，累计 {total_records} 条分时数据")

        except Exception as e:
            print(f"处理股票 {code} 失败: {e}")

    conn.commit()
    print(f"[{datetime.now()}] 同步完成，共 {total_records} 条分时数据")

    cursor.execute('SELECT COUNT(*) FROM stock_kline_minute')
    print(f"数据库现有: {cursor.fetchone()[0]} 条分时数据")

    conn.close()


if __name__ == "__main__":
    # 同步指定股票列表
    # sync_stock_kline_minute(stock_codes=['000001', '000002', '600000'])

    # 同步所有股票（近5天）
    sync_stock_kline_minute()

    # 也可以指定保留天数
    # sync_stock_kline_minute(days=10)
