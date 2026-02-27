#!/usr/bin/env python3
"""
同步股票基本信息到数据库
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime


def sync_stock_info():
    """同步股票基本信息"""
    from app.provider.akshare import get_stock_info_a_code_name

    print(f"[{datetime.now()}] 开始同步股票基本信息...")

    results = get_stock_info_a_code_name()
    print(f"获取到 {len(results)} 条股票数据")

    # TODO: 替换为实际的数据库插入操作
    # 示例：
    # from app.models import StockInfo
    # from app.database import SessionLocal
    # db = SessionLocal()
    # for r in results:
    #     db.merge(StockInfo(code=r.code, name=r.name))
    # db.commit()

    print(f"[{datetime.now()}] 同步完成")


if __name__ == "__main__":
    sync_stock_info()
