#!/usr/bin/env python3
"""
同步分时数据到数据库
同步过去5天的数据（分时数据量大，只保留近5日）
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta


def sync_stock_kline_minute(days: int = 5):
    """
    同步分时数据

    Args:
        days: 保留天数，默认5天
    """
    from app.provider.akshare import get_stock_info_a_code_name, get_stock_zh_a_hist_min_em

    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    print(f"[{datetime.now()}] 开始同步分时数据...")
    print(f"时间范围: {start_date} - {end_date} (最近{days}天)")

    # 获取所有股票代码
    stocks = get_stock_info_a_code_name()
    print(f"共有 {len(stocks)} 只股票")

    total_records = 0
    for i, stock in enumerate(stocks):
        try:
            # 获取5分钟级别的分时数据
            results = get_stock_zh_a_hist_min_em(
                symbol=stock.code,
                period="5",
                start_date=start_date,
                end_date=end_date
            )

            if results:
                # TODO: 替换为实际的数据库插入操作
                # 示例：
                # from app.models import StockKlineMinute
                # from app.database import SessionLocal
                # db = SessionLocal()
                # for r in results:
                #     db.merge(StockKlineMinute(
                #         trade_date=r.日期,
                #         stock_code=stock.code,
                #         time_minute=r.时间,
                #         open=r.开盘,
                #         close=r.收盘,
                #         ...
                #     ))
                # db.commit()

                total_records += len(results)

            if (i + 1) % 100 == 0:
                print(f"已处理 {i + 1}/{len(stocks)} 只股票，累计 {total_records} 条分时数据")

        except Exception as e:
            print(f"处理股票 {stock.code} 失败: {e}")

    print(f"[{datetime.now()}] 同步完成，共 {total_records} 条分时数据")


if __name__ == "__main__":
    # 可以指定保留天数
    # sync_stock_kline_minute(days=10)
    sync_stock_kline_minute()
