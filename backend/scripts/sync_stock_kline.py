#!/usr/bin/env python3
"""
同步历史K线数据到数据库
同步过去一年的数据
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta


def sync_stock_kline(start_date: str = None, end_date: str = None):
    """
    同步历史K线数据

    Args:
        start_date: 开始日期，格式 YYYYMMDD，默认过去一年
        end_date: 结束日期，格式 YYYYMMDD，默认今天
    """
    from app.provider.akshare import get_stock_info_a_code_name, get_stock_zh_a_hist

    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

    print(f"[{datetime.now()}] 开始同步K线数据...")
    print(f"时间范围: {start_date} - {end_date}")

    # 获取所有股票代码
    stocks = get_stock_info_a_code_name()
    print(f"共有 {len(stocks)} 只股票")

    total_records = 0
    for i, stock in enumerate(stocks):
        try:
            results = get_stock_zh_a_hist(
                symbol=stock.code,
                start_date=start_date,
                end_date=end_date
            )

            if results:
                # TODO: 替换为实际的数据库插入操作
                # 示例：
                # from app.models import StockKline
                # from app.database import SessionLocal
                # db = SessionLocal()
                # for r in results:
                #     db.merge(StockKline(
                #         trade_date=r.日期,
                #         stock_code=stock.code,
                #         open=r.开盘,
                #         close=r.收盘,
                #         ...
                #     ))
                # db.commit()

                total_records += len(results)

            if (i + 1) % 100 == 0:
                print(f"已处理 {i + 1}/{len(stocks)} 只股票，累计 {total_records} 条K线数据")

        except Exception as e:
            print(f"处理股票 {stock.code} 失败: {e}")

    print(f"[{datetime.now()}] 同步完成，共 {total_records} 条K线数据")


if __name__ == "__main__":
    # 可以指定日期范围
    # sync_stock_kline("20240101", "20241231")
    sync_stock_kline()
