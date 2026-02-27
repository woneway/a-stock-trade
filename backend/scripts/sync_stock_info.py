#!/usr/bin/env python3
"""
同步股票基本信息到数据库
"""
import sys
sys.path.insert(0, '.')

import pymysql
from datetime import datetime
from app.provider.akshare import get_stock_info_a_code_name

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 13306,
    'user': 'root',
    'password': 'asset123456',
    'database': 'astock',
    'charset': 'utf8mb4'
}


def sync_stock_info():
    """同步股票基本信息"""
    print(f"[{datetime.now()}] 开始同步股票基本信息...")

    # 获取数据
    results = get_stock_info_a_code_name()
    print(f"获取到 {len(results)} 条股票数据")

    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 插入数据
    insert_sql = 'INSERT INTO stock_info (code, name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE name=VALUES(name)'

    for r in results:
        cursor.execute(insert_sql, (r.code, r.name))

    conn.commit()
    print(f"[{datetime.now()}] 同步完成，共 {len(results)} 条")

    cursor.execute('SELECT COUNT(*) FROM stock_info')
    print(f"数据库现有: {cursor.fetchone()[0]} 条")

    conn.close()


if __name__ == "__main__":
    sync_stock_info()
