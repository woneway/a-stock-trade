#!/usr/bin/env python3
"""
数据同步入口脚本
按顺序执行所有同步任务
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime
from scripts.sync_stock_info import sync_stock_info
from scripts.sync_stock_kline import sync_stock_kline
from scripts.sync_stock_kline_minute import sync_stock_kline_minute


def main():
    print("=" * 50)
    print("AKShare 数据同步任务")
    print("=" * 50)

    # 1. 同步股票基本信息
    print("\n[1/3] 同步股票基本信息...")
    sync_stock_info()

    # 2. 同步历史K线（过去一年）
    print("\n[2/3] 同步历史K线...")
    sync_stock_kline()

    # 3. 同步分时数据（过去5天）
    print("\n[3/3] 同步分时数据...")
    sync_stock_kline_minute()

    print("\n" + "=" * 50)
    print("所有同步任务完成!")
    print("=" * 50)


if __name__ == "__main__":
    main()
